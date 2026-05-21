"""
Service: ekstraksi teks PDF dan deteksi skill dari CV.
Menangani CV bilingual (Bahasa Indonesia + Inggris).
"""
import io
import re
from typing import List

import pdfplumber
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


# ── Inisialisasi (dijalankan sekali saat module di-import) ────────────────────

_stemmer = StemmerFactory().create_stemmer()

# Gazetteer skill — diperluas oleh AI Engineer
SKILL_GAZETTEER = {
    # Bahasa pemrograman
    "python", "javascript", "typescript", "java", "kotlin", "go", "rust",
    "c++", "c#", "php", "ruby", "swift",
    # Framework & library
    "react", "vue", "fastapi", "flask", "django", "express", "nextjs",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    # Database
    "postgresql", "mysql", "mongodb", "redis", "supabase",
    # Tools & lain-lain
    "docker", "kubernetes", "git", "github", "aws", "gcp", "azure",
    "linux", "rest api", "graphql", "nlp", "machine learning", "deep learning",
    # Skill non-teknis (relevan untuk pasar Indonesia)
    "kepemimpinan", "leadership", "manajemen proyek", "project management",
    "komunikasi", "communication", "analisis data", "data analysis",
    "mengelola tim", "team management", "presentasi",
}

# Normalisasi sinonim skill Indonesia → English canonical
SYNONYM_MAP = {
    "mengelola tim":       "leadership",
    "kepemimpinan":        "leadership",
    "analisis data":       "data analysis",
    "manajemen proyek":    "project management",
    "kecerdasan buatan":   "machine learning",
    "pembelajaran mesin":  "machine learning",
    "jaringan syaraf":     "deep learning",
}


# ── Fungsi publik ─────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Ekstrak semua teks dari PDF bytes menggunakan pdfplumber."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_skills(text: str) -> List[str]:
    """
    Deteksi skill dari teks CV menggunakan dictionary-based matching.
    Menangani sinonim dan variasi bahasa Indonesia.
    """
    text_lower = text.lower()

    # Normalisasi sinonim
    for indo, canonical in SYNONYM_MAP.items():
        text_lower = text_lower.replace(indo, canonical)

    found: set[str] = set()

    # Cari multi-word skill dulu (prioritas lebih tinggi)
    multi_word = sorted([s for s in SKILL_GAZETTEER if " " in s], key=len, reverse=True)
    for skill in multi_word:
        if skill in text_lower:
            found.add(skill)

    # Cari single-word skill dengan word boundary
    single_word = [s for s in SKILL_GAZETTEER if " " not in s]
    for skill in single_word:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)

    return sorted(found)
