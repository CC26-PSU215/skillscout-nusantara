"""
Data Cleaning Pipeline — SkillScout Nusantara.

Membersihkan data mentah dari scraping (Glints, dll) dan data AI (CSV)
sebelum dimasukkan ke database atau digunakan untuk training model.

Pipeline:
  1. Load raw CSV
  2. Hapus duplikat & baris kosong
  3. Normalisasi teks (lowercase, strip whitespace, hapus karakter aneh)
  4. Normalisasi lokasi (standarisasi nama kota/provinsi)
  5. Ekstrak skill dari judul pekerjaan (jika kolom skill kosong)
  6. Parse salary range ke angka (min_salary, max_salary)
  7. Validasi & buang baris yang tidak valid
  8. Export ke CSV bersih + opsional insert ke database

Penggunaan:
  python -m app.cleaning.clean_raw_data              # clean semua
  python -m app.cleaning.clean_raw_data --source glints
  python -m app.cleaning.clean_raw_data --source ai
  python -m app.cleaning.clean_raw_data --insert      # clean + insert ke DB
"""

import argparse
import re
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd


# ── Path constants ────────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parents[3]  # skillscout-nusantara/
RAW_DIR = ROOT_DIR / "datasets" / "raw"
CLEAN_DIR = ROOT_DIR / "datasets" / "cleaned"
AI_DIR = ROOT_DIR / "ai"


# ── Normalisasi Teks ─────────────────────────────────────────────────────────

def normalize_text(text: Optional[str]) -> str:
    """Bersihkan dan normalisasi teks umum."""
    if not text or not isinstance(text, str):
        return ""
    # Strip whitespace dan newlines berlebihan
    text = re.sub(r"\s+", " ", text).strip()
    # Hapus karakter kontrol non-printable
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text


def normalize_title(title: str) -> str:
    """Standarisasi judul pekerjaan."""
    title = normalize_text(title)
    if not title:
        return ""
    # Hapus prefix/suffix umum yang noise
    title = re.sub(r"\s*[-–—]\s*(Remote|WFH|Hybrid|Onsite|Urgent).*$",
                   "", title, flags=re.IGNORECASE)
    # Kapitalisasi wajar
    return title.strip()


# ── Normalisasi Lokasi ────────────────────────────────────────────────────────

# Mapping singkatan / variasi → bentuk baku
_LOCATION_MAP = {
    "dki jakarta":         "DKI Jakarta",
    "jakarta":             "DKI Jakarta",
    "jakarta selatan":     "Jakarta Selatan, DKI Jakarta",
    "jakarta pusat":       "Jakarta Pusat, DKI Jakarta",
    "jakarta barat":       "Jakarta Barat, DKI Jakarta",
    "jakarta timur":       "Jakarta Timur, DKI Jakarta",
    "jakarta utara":       "Jakarta Utara, DKI Jakarta",
    "bandung":             "Bandung, Jawa Barat",
    "surabaya":            "Surabaya, Jawa Timur",
    "yogyakarta":          "Yogyakarta, DI Yogyakarta",
    "semarang":            "Semarang, Jawa Tengah",
    "medan":               "Medan, Sumatera Utara",
    "makassar":            "Makassar, Sulawesi Selatan",
    "bali":                "Bali",
    "denpasar":            "Denpasar, Bali",
    "tangerang":           "Tangerang, Banten",
    "bekasi":              "Bekasi, Jawa Barat",
    "depok":               "Depok, Jawa Barat",
    "bogor":               "Bogor, Jawa Barat",
    "malang":              "Malang, Jawa Timur",
    "solo":                "Solo, Jawa Tengah",
}


def normalize_location(loc: Optional[str]) -> str:
    """Standarisasi format lokasi."""
    if not loc or not isinstance(loc, str):
        return ""
    loc = normalize_text(loc)
    # Coba cari di mapping (pakai lowercase key)
    loc_lower = loc.lower().strip()
    # Cek exact match
    if loc_lower in _LOCATION_MAP:
        return _LOCATION_MAP[loc_lower]
    # Cek partial match — cari kata kunci kota di string (longest key first)
    for key, canonical in sorted(_LOCATION_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if key in loc_lower:
            return canonical
    # Tidak ketemu → kembalikan dengan Title Case
    return loc.title().strip()


# ── Parsing Salary ────────────────────────────────────────────────────────────

def parse_salary(salary_str: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """
    Parse string gaji Indonesia ke angka.
    Contoh input: "Rp 5 jt-7 jt", "Rp 2,8 jt-3,5 jt", "Gaji Tidak Ditampilkan"
    Returns: (min_salary, max_salary) dalam Rupiah, atau (None, None).
    """
    if not salary_str or not isinstance(salary_str, str):
        return None, None

    s = salary_str.lower().strip()
    if "tidak" in s or "not" in s or "negotiable" in s:
        return None, None

    # Hapus prefix "rp" dan spasi
    s = re.sub(r"rp\s*", "", s)

    # Cari angka dengan format "X,Y jt" atau "X jt" atau "X rb"
    numbers = re.findall(r"([\d]+(?:[.,]\d+)?)\s*(jt|rb|juta|ribu)?", s)
    if not numbers:
        return None, None

    values = []
    for num_str, unit in numbers:
        num_str = num_str.replace(",", ".")
        try:
            val = float(num_str)
        except ValueError:
            continue
        if unit in ("jt", "juta"):
            val *= 1_000_000
        elif unit in ("rb", "ribu"):
            val *= 1_000
        values.append(int(val))

    if len(values) == 0:
        return None, None
    elif len(values) == 1:
        return values[0], values[0]
    else:
        return min(values), max(values)


# ── Skill Extraction dari Title ───────────────────────────────────────────────

# Daftar skill yang sering muncul di judul lowongan
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
    # Multi-word dulu
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


# ── Pipeline: Glints Scraping Data ────────────────────────────────────────────

def clean_glints_data(input_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Bersihkan data scraping Glints.

    Kolom input:  job_id, job_title, company_name, industry_category,
                  raw_description, location, posted_date, salary_range,
                  employment_type, job_url, source_platform,
                  extracted_job_skills, experience_level

    Kolom output: id, title, company, description, skills, location,
                  source_url, salary_min, salary_max, employment_type,
                  experience_level
    """
    if input_path is None:
        input_path = RAW_DIR / "glints_jobs.csv"

    if not input_path.exists():
        print(f"⚠️  File tidak ditemukan: {input_path}")
        return pd.DataFrame()

    df = pd.read_csv(input_path)
    original_count = len(df)
    print(f"📥 Loaded {original_count} rows from {input_path.name}")

    # 1. Hapus duplikat berdasarkan job_id
    df = df.drop_duplicates(subset=["job_id"], keep="first")
    dup_removed = original_count - len(df)
    if dup_removed:
        print(f"   Removed {dup_removed} duplicates")

    # 2. Hapus baris tanpa judul atau perusahaan
    df = df.dropna(subset=["job_title"])
    df = df[df["job_title"].str.strip() != ""]

    # 3. Normalisasi kolom
    df["title"] = df["job_title"].apply(normalize_title)
    df["company"] = df["company_name"].apply(normalize_text)
    df["description"] = df["raw_description"].apply(normalize_text)
    df["location"] = df["location"].apply(normalize_location)
    df["source_url"] = df["job_url"].apply(normalize_text)

    # 4. Parse salary
    salary_parsed = df["salary_range"].apply(parse_salary)
    df["salary_min"] = salary_parsed.apply(lambda x: x[0])
    df["salary_max"] = salary_parsed.apply(lambda x: x[1])

    # 5. Skill extraction — kalau kolom skill kosong, pakai title
    def _get_skills(row):
        raw = row.get("extracted_job_skills", "")
        if isinstance(raw, str) and raw.strip() and raw.strip() != "[]":
            try:
                import ast
                skills = ast.literal_eval(raw)
                if isinstance(skills, list) and skills:
                    return [s.strip().lower() for s in skills if s.strip()]
            except (ValueError, SyntaxError):
                pass
        return extract_skills_from_title(row.get("title", ""))

    df["skills"] = df.apply(_get_skills, axis=1)

    # 6. Normalisasi employment_type dan experience_level
    df["employment_type"] = df["employment_type"].apply(
        lambda x: normalize_text(x) if x != "Not specified" else ""
    )
    df["experience_level"] = df["experience_level"].apply(
        lambda x: normalize_text(x) if x != "Not specified" else ""
    )

    # 7. Generate UUID untuk id
    df["id"] = df.apply(lambda _: str(uuid.uuid4()), axis=1)

    # 8. Pilih kolom final
    result = df[[
        "id", "title", "company", "description", "skills", "location",
        "source_url", "salary_min", "salary_max", "employment_type",
        "experience_level",
    ]].copy()

    # 9. Buang baris tanpa title
    result = result[result["title"].str.len() > 0]

    print(f"✅ Cleaned: {len(result)} rows (dari {original_count})")
    return result


# ── Pipeline: AI Job Market Data ──────────────────────────────────────────────

def clean_ai_jobmarket(input_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Bersihkan data AI JobMarket_Preprocessed.csv.

    Kolom input:  job_id, job_title, extracted_job_skills, experienced_level,
                  extracted_job_skills_count, role_category,
                  extracted_requirements, extracted_responsibilities

    Kolom output: id, title, company, description, skills, location, source_url
    """
    if input_path is None:
        input_path = AI_DIR / "JobMarket_Preprocessed.csv"

    if not input_path.exists():
        print(f"⚠️  File tidak ditemukan: {input_path}")
        return pd.DataFrame()

    df = pd.read_csv(input_path)
    original_count = len(df)
    print(f"📥 Loaded {original_count} rows from {input_path.name}")

    # 1. Hapus duplikat
    df = df.drop_duplicates(subset=["job_id"], keep="first")

    # 2. Hapus baris tanpa judul
    df = df.dropna(subset=["job_title"])
    df = df[df["job_title"].str.strip() != ""]

    # 3. Normalisasi
    df["title"] = df["job_title"].apply(normalize_title)
    df["company"] = ""  # Dataset ini tidak punya company
    df["location"] = ""  # Dataset ini tidak punya location

    # 4. Gabungkan requirements + responsibilities → description
    df["description"] = df.apply(
        lambda r: normalize_text(
            f"{r.get('extracted_requirements', '')} "
            f"{r.get('extracted_responsibilities', '')}"
        ),
        axis=1,
    )

    # 5. Parse skills
    def _parse_skills(raw):
        if not raw or not isinstance(raw, str):
            return []
        return [s.strip().lower() for s in raw.split(",") if s.strip()]

    df["skills"] = df["extracted_job_skills"].apply(_parse_skills)

    # 6. Generate UUID
    df["id"] = df.apply(lambda _: str(uuid.uuid4()), axis=1)

    # 7. Kolom tambahan
    df["source_url"] = ""

    result = df[["id", "title", "company", "description", "skills",
                  "location", "source_url"]].copy()
    result = result[result["title"].str.len() > 0]

    print(f"✅ Cleaned: {len(result)} rows (dari {original_count})")
    return result


# ── Pipeline: AI CV Data ──────────────────────────────────────────────────────

def clean_ai_cv(input_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Bersihkan data AI CV.csv.

    Kolom input:  user_id, raw_cv_text, extracted_user_skills, last_role
    Kolom output: user_id, raw_cv_text, skills, last_role
    """
    if input_path is None:
        input_path = AI_DIR / "CV.csv"

    if not input_path.exists():
        print(f"⚠️  File tidak ditemukan: {input_path}")
        return pd.DataFrame()

    df = pd.read_csv(input_path)
    original_count = len(df)
    print(f"📥 Loaded {original_count} rows from {input_path.name}")

    # 1. Hapus duplikat
    df = df.drop_duplicates(subset=["user_id"], keep="first")

    # 2. Hapus baris tanpa teks CV
    df = df.dropna(subset=["raw_cv_text"])
    df = df[df["raw_cv_text"].str.strip() != ""]

    # 3. Normalisasi teks CV
    df["raw_cv_text"] = df["raw_cv_text"].apply(normalize_text)

    # 4. Parse skills
    def _parse(raw):
        if not raw or not isinstance(raw, str):
            return []
        return [s.strip().lower() for s in raw.split(",") if s.strip()]

    df["skills"] = df["extracted_user_skills"].apply(_parse)
    df["last_role"] = df["last_role"].apply(normalize_text)

    result = df[["user_id", "raw_cv_text", "skills", "last_role"]].copy()
    print(f"✅ Cleaned: {len(result)} rows (dari {original_count})")
    return result


# ── Export ────────────────────────────────────────────────────────────────────

def export_csv(df: pd.DataFrame, filename: str) -> Path:
    """Simpan DataFrame ke datasets/cleaned/."""
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CLEAN_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"💾 Saved to {output_path} ({len(df)} rows)")
    return output_path


# ── Insert ke Database (opsional) ─────────────────────────────────────────────

async def insert_jobs_to_db(df: pd.DataFrame):
    """Insert data lowongan yang sudah bersih ke database Supabase."""
    import json
    from app.database import async_session
    from app.db.models import Job

    async with async_session() as session:
        count = 0
        for _, row in df.iterrows():
            job = Job(
                id=row["id"],
                title=row["title"],
                company=row.get("company", ""),
                description=row.get("description", ""),
                skills=row.get("skills", []),
                location=row.get("location", None) or None,
                source_url=row.get("source_url", None) or None,
            )
            session.add(job)
            count += 1

        await session.commit()
        print(f"📦 Inserted {count} jobs to database")


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SkillScout Nusantara — Data Cleaning Pipeline"
    )
    parser.add_argument(
        "--source",
        choices=["glints", "ai", "cv", "all"],
        default="all",
        help="Sumber data yang akan dibersihkan",
    )
    parser.add_argument(
        "--insert",
        action="store_true",
        help="Insert data bersih ke database setelah cleaning",
    )
    args = parser.parse_args()

    print("🧹 SkillScout Data Cleaning Pipeline")
    print("=" * 50)

    if args.source in ("glints", "all"):
        df_glints = clean_glints_data()
        if not df_glints.empty:
            export_csv(df_glints, "glints_jobs_cleaned.csv")

    if args.source in ("ai", "all"):
        df_jobs = clean_ai_jobmarket()
        if not df_jobs.empty:
            export_csv(df_jobs, "jobmarket_cleaned.csv")

    if args.source in ("cv", "all"):
        df_cv = clean_ai_cv()
        if not df_cv.empty:
            export_csv(df_cv, "cv_cleaned.csv")

    if args.insert:
        import asyncio
        if args.source in ("glints", "all") and not df_glints.empty:
            asyncio.run(insert_jobs_to_db(df_glints))
        if args.source in ("ai", "all") and not df_jobs.empty:
            asyncio.run(insert_jobs_to_db(df_jobs))

    print("\n✅ Cleaning selesai!")


if __name__ == "__main__":
    main()
