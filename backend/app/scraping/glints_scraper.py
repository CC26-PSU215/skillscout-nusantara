import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

class GlintsScraper:
    def __init__(self):
        self.base_url = "https://glints.com/opportunities/jobs/explore"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []
    
    def scrape_jobs(self, category="tech", pages=10):
        """Scrape Glints job listings"""
        for page in range(1, pages + 1):
            print(f"Scraping page {page}...")
            params = {
                'category': category,
                'slug': 'computer-software',
                'page': page
            }

            try:
                response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                job_cards = soup.find_all('div', attrs={'data-glints-tracking-element-name': 'job_card'})
                if not job_cards:
                    print(f"  No job cards found on page {page}")

                for card in job_cards:
                    job = self.extract_job_data(card)
                    if job:
                        self.data.append(job)

                time.sleep(2)

            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

        return self.data

    def extract_job_data(self, card):
        """Extract job information from a Glints job card"""
        try:
            title_link = card.select_one('h2 a')
            if not title_link:
                return None

            job_title = title_link.get_text(strip=True)
            job_href = title_link.get('href', '')
            job_url = f"https://glints.com{job_href}" if job_href.startswith('/') else job_href

            company_tag = card.find('a', href=lambda value: value and '/companies/' in value)
            company_name = company_tag.get_text(strip=True) if company_tag else ''

            location_tags = [
                a.get_text(strip=True)
                for a in card.find_all('a', href=lambda value: value and '/job-location/' in value)
                if a.get_text(strip=True)
            ]
            location = ', '.join(location_tags).strip()

            salary_range = 'Not specified'
            employment_type = 'Not specified'
            experience_level = 'Not specified'
            posted_date = 'Not specified'

            for span in card.find_all('span'):
                text = span.get_text(strip=True)
                if not text:
                    continue
                lower_text = text.lower()
                if 'gaji' in lower_text or 'rp' in lower_text:
                    salary_range = text
                elif any(term in lower_text for term in ['kontrak', 'full time', 'full-time', 'part time', 'part-time', 'freelance', 'permanent']):
                    employment_type = text
                elif 'tahun' in lower_text or 'year' in lower_text:
                    experience_level = text
                elif any(term in lower_text for term in ['hari', 'today', 'yesterday', 'week']):
                    posted_date = text

            industry_category = card.get('data-gtm-job-category', '') or card.get('data-glints-tracking-job-category', '')

            return {
                'job_id': card.get('data-gtm-job-id', ''),
                'job_title': job_title,
                'company_name': company_name,
                'industry_category': industry_category,
                'raw_description': '',
                'location': location,
                'posted_date': posted_date,
                'salary_range': salary_range,
                'employment_type': employment_type,
                'job_url': job_url,
                'source_platform': 'Glints',
                'extracted_job_skills': [],
                'experience_level': experience_level
            }
        except Exception:
            return None
    
    def save_to_csv(self, filename='glints_jobs.csv'):
        """Save scraped data to CSV"""
        output_dir = Path(__file__).resolve().parents[3] / 'datasets' / 'raw'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        df = pd.DataFrame(self.data)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} jobs to {output_path}")
        return df

# Usage
if __name__ == "__main__":
    scraper = GlintsScraper()
    scraper.scrape_jobs(category="tech", pages=5)  # Scrape 10 pages
    scraper.save_to_csv()