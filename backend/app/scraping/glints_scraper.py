"""
Glints Job Scraper — SkillScout Nusantara.

Scrapes job listings from Glints.com and inserts them into the database.
Includes URL validation to ensure only accessible job links are stored.

Usage standalone:
    python -m app.scraping.glints_scraper

Usage from code:
    from app.scraping.glints_scraper import GlintsScraper
    scraper = GlintsScraper()
    result = await scraper.scrape_and_save_to_db(pages=5)
"""

import re
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ── Skill extraction from title ──────────────────────────────────────────────

_TITLE_SKILLS = {
    "python", "java", "javascript", "typescript", "golang", "go", "rust",
    "kotlin", "swift", "php", "ruby", "c++", "c#", "cobol", "sql",
    "react", "vue", "angular", "nextjs", "node", "express", "django",
    "flask", "fastapi", "spring", "laravel",
    "docker", "kubernetes", "aws", "gcp", "azure", "devops", "ci/cd",
    "machine learning", "deep learning", "data science", "data analyst",
    "data engineer", "frontend", "backend", "fullstack", "full stack",
    "mobile", "android", "ios", "flutter", "react native",
    "qa", "quality assurance", "security", "network", "cloud",
    "iot", "blockchain", "ai", "nlp",
    "power bi", "tableau", "excel",
}


def extract_skills_from_title(title: str) -> list[str]:
    """Ekstrak skill/teknologi dari judul pekerjaan."""
    if not title:
        return []
    title_lower = title.lower()
    found = []
    # Multi-word dulu (prioritas)
    multi = sorted([s for s in _TITLE_SKILLS if " " in s], key=len, reverse=True)
    for skill in multi:
        if skill in title_lower:
            found.append(skill)
    # Single-word
    for skill in _TITLE_SKILLS:
        if " " not in skill and re.search(r"\b" + re.escape(skill) + r"\b", title_lower):
            if skill not in found:
                found.append(skill)
    return sorted(set(found))


class GlintsScraper:
    """Scraper untuk lowongan kerja dari Glints.com."""

    def __init__(self):
        self.base_url = "https://glints.com/id/job-category/computer-software"
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }
        self.data: list[dict] = []

    async def validate_url(self, url: str, client: httpx.AsyncClient) -> bool:
        """
        Validate that a URL is accessible (returns 2xx/3xx).
        Returns False for 404, timeouts, or connection errors.
        """
        if not url or not url.startswith("http"):
            return False
        try:
            resp = await client.head(url, follow_redirects=True, timeout=10)
            return resp.status_code < 400
        except (httpx.RequestError, httpx.HTTPStatusError):
            return False

    def scrape_jobs(self, pages: int = 5) -> list[dict]:
        """
        Scrape Glints job listings (synchronous HTTP).
        Returns list of raw job dicts.
        """
        import requests
        import time

        self.data = []
        for page in range(1, pages + 1):
            logger.info(f"Scraping Glints page {page}/{pages}...")
            params = {
                'category': 'tech',
                'slug': 'computer-software',
                'page': page,
            }

            try:
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=15,
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')

                job_cards = soup.find_all(
                    'div',
                    attrs={'data-glints-tracking-element-name': 'job_card'},
                )
                if not job_cards:
                    logger.warning(f"No job cards found on page {page}")

                for card in job_cards:
                    job = self._extract_job_data(card)
                    if job and job.get('job_title'):
                        self.data.append(job)

                time.sleep(2)  # Rate limiting

            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                continue

        logger.info(f"Scraped {len(self.data)} jobs total")
        return self.data

    def _extract_job_data(self, card) -> Optional[dict]:
        """Extract job information from a Glints job card."""
        try:
            title_link = card.select_one('h2 a')
            if not title_link:
                return None

            job_title = title_link.get_text(strip=True)
            job_href = title_link.get('href', '')
            job_url = (
                f"https://glints.com{job_href}"
                if job_href.startswith('/')
                else job_href
            )

            company_tag = card.find(
                'a', href=lambda value: value and '/companies/' in value
            )
            company_name = company_tag.get_text(strip=True) if company_tag else ''

            location_tags = [
                a.get_text(strip=True)
                for a in card.find_all(
                    'a', href=lambda value: value and '/job-location/' in value
                )
                if a.get_text(strip=True)
            ]
            location = ', '.join(location_tags).strip()

            salary_range = ''
            employment_type = ''
            experience_level = ''

            for span in card.find_all('span'):
                text = span.get_text(strip=True)
                if not text:
                    continue
                lower_text = text.lower()
                if 'gaji' in lower_text or 'rp' in lower_text:
                    salary_range = text
                elif any(term in lower_text for term in [
                    'kontrak', 'full time', 'full-time',
                    'part time', 'part-time', 'freelance', 'permanent'
                ]):
                    employment_type = text
                elif 'tahun' in lower_text or 'year' in lower_text:
                    experience_level = text

            return {
                'job_title': job_title,
                'company_name': company_name,
                'raw_description': '',
                'location': location,
                'salary_range': salary_range,
                'employment_type': employment_type,
                'job_url': job_url,
                'source_platform': 'Glints',
                'extracted_job_skills': [],
                'experience_level': experience_level,
            }
        except Exception as e:
            logger.debug(f"Error extracting job data: {e}")
            return None

    async def scrape_and_save_to_db(self, pages: int = 5) -> dict:
        """
        Scrape Glints and insert valid jobs into the database.

        Returns:
            dict with keys: scraped, new_inserted, skipped_duplicate,
                            skipped_invalid_url, errors
        """
        from sqlalchemy import select
        from app.database import async_session
        from app.db.models import Job

        # 1. Scrape (synchronous requests)
        raw_jobs = self.scrape_jobs(pages=pages)

        stats = {
            "scraped": len(raw_jobs),
            "new_inserted": 0,
            "skipped_duplicate": 0,
            "skipped_invalid_url": 0,
            "errors": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if not raw_jobs:
            return stats

        # 2. Validate URLs and insert to DB
        async with httpx.AsyncClient(
            headers=self.headers,
            follow_redirects=True,
        ) as http_client:
            async with async_session() as session:
                for job_data in raw_jobs:
                    try:
                        source_url = job_data.get('job_url', '')

                        # Check duplicate by source_url
                        if source_url:
                            existing = await session.execute(
                                select(Job).where(Job.source_url == source_url)
                            )
                            if existing.scalar_one_or_none():
                                stats["skipped_duplicate"] += 1
                                continue

                        # Validate URL is accessible
                        if source_url:
                            is_valid = await self.validate_url(
                                source_url, http_client
                            )
                            if not is_valid:
                                logger.warning(
                                    f"Invalid URL skipped: {source_url}"
                                )
                                stats["skipped_invalid_url"] += 1
                                continue

                        # Extract skills from title
                        skills = extract_skills_from_title(
                            job_data.get('job_title', '')
                        )

                        # Create Job record
                        job = Job(
                            id=str(uuid.uuid4()),
                            title=job_data.get('job_title', '').strip(),
                            company=job_data.get('company_name', '').strip(),
                            description=job_data.get(
                                'raw_description', ''
                            ).strip(),
                            skills=skills,
                            location=job_data.get('location', '') or None,
                            source_url=source_url or None,
                        )
                        session.add(job)
                        stats["new_inserted"] += 1

                    except Exception as e:
                        logger.error(f"Error processing job: {e}")
                        stats["errors"] += 1
                        continue

                await session.commit()

        logger.info(
            f"Scrape complete: {stats['new_inserted']} new, "
            f"{stats['skipped_duplicate']} duplicates, "
            f"{stats['skipped_invalid_url']} invalid URLs"
        )
        return stats

    def save_to_csv(self, filename: str = 'glints_jobs.csv') -> pd.DataFrame:
        """Save scraped data to CSV."""
        output_dir = Path(__file__).resolve().parents[3] / 'datasets' / 'raw'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        df = pd.DataFrame(self.data)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} jobs to {output_path}")
        return df


# ── CLI Usage ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    scraper = GlintsScraper()

    print("🔍 Starting Glints scraping + DB insert...")
    result = asyncio.run(scraper.scrape_and_save_to_db(pages=5))
    print(f"\n📊 Results:")
    for k, v in result.items():
        print(f"   {k}: {v}")