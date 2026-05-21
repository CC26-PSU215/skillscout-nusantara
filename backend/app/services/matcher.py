"""
Service: local TF-IDF matcher (fallback jika ML service tidak tersedia).
Menggunakan scikit-learn TfidfVectorizer + cosine similarity.

Catatan: ini adalah fallback lokal. Pipeline utama yang memenuhi
checklist Deep Learning (TensorFlow) ada di ML service terpisah
(Railway/Render).
"""
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank_jobs(
    cv_text: str,
    cv_skills: list[str],
    jobs: list,
    top_k: int = 10,
) -> list[dict]:
    """
    Ranking sederhana berbasis TF-IDF cosine similarity
    digabung dengan skill overlap scoring.

    Args:
        cv_text: teks mentah dari CV
        cv_skills: list skill yang sudah diekstrak dari CV
        jobs: list ORM Job objects
        top_k: jumlah top hasil yang dikembalikan

    Returns:
        List of dicts dengan keys: job_id, title, company,
        score, matched_skills, gap_skills
    """
    if not jobs:
        return []

    # ── TF-IDF Cosine Similarity ────────────────────────────
    job_texts = [f"{j.title} {j.description}" for j in jobs]
    corpus = [cv_text] + job_texts

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Cosine similarity antara CV (index 0) dan semua job
    cv_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(cv_vector, job_vectors).flatten()

    # ── Skill Overlap Scoring ───────────────────────────────
    cv_skill_set = set(s.lower() for s in cv_skills)

    results = []
    for idx, job in enumerate(jobs):
        job_skill_set = set(s.lower() for s in (job.skills or []))

        matched = cv_skill_set & job_skill_set
        gap = job_skill_set - cv_skill_set

        # Skill overlap ratio (0-1)
        skill_score = len(matched) / max(len(job_skill_set), 1)

        # Gabungkan: 60% TF-IDF + 40% skill overlap
        combined_score = 0.6 * similarities[idx] + 0.4 * skill_score

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "score": round(float(combined_score), 4),
            "matched_skills": sorted(matched),
            "gap_skills": sorted(gap),
        })

    # Sort by score descending, ambil top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
