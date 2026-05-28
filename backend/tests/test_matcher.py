"""
Tests: Local TF-IDF matcher service.
Tidak memerlukan database atau network — menggunakan mock Job objects.
"""
import pytest
from types import SimpleNamespace

from app.services.matcher import rank_jobs


def _make_job(id: str, title: str, company: str, description: str, skills: list):
    """Helper: buat mock Job object (duck-typed)."""
    return SimpleNamespace(
        id=id, title=title, company=company,
        description=description, skills=skills,
    )


# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_JOBS = [
    _make_job("j1", "Data Scientist", "Gojek",
              "Build machine learning models using Python and TensorFlow",
              ["python", "machine learning", "tensorflow", "sql"]),
    _make_job("j2", "Frontend Developer", "Tokopedia",
              "Create user interfaces with React and TypeScript",
              ["react", "typescript", "javascript", "css"]),
    _make_job("j3", "Backend Engineer", "Bukalapak",
              "Develop RESTful APIs using Go and PostgreSQL",
              ["go", "postgresql", "docker", "rest api"]),
    _make_job("j4", "DevOps Engineer", "Traveloka",
              "Manage cloud infrastructure on AWS with Kubernetes",
              ["aws", "kubernetes", "docker", "linux"]),
    _make_job("j5", "Mobile Developer", "Shopee",
              "Build Android apps using Kotlin and Jetpack",
              ["kotlin", "android", "java", "git"]),
]


# ═════════════════════════════════════════════════════════════════
# Basic functionality
# ═════════════════════════════════════════════════════════════════

class TestRankJobsBasic:
    """Test basic matching behavior."""

    def test_returns_list(self):
        results = rank_jobs("python data science", ["python"], SAMPLE_JOBS)
        assert isinstance(results, list)

    def test_returns_correct_keys(self):
        results = rank_jobs("python", ["python"], SAMPLE_JOBS)
        assert len(results) > 0
        for r in results:
            assert "job_id" in r
            assert "title" in r
            assert "company" in r
            assert "score" in r
            assert "matched_skills" in r
            assert "gap_skills" in r

    def test_scores_between_0_and_1(self):
        results = rank_jobs("python machine learning", ["python"], SAMPLE_JOBS)
        for r in results:
            assert 0 <= r["score"] <= 1, f"Score {r['score']} out of range"

    def test_results_sorted_by_score_descending(self):
        results = rank_jobs("python react docker", ["python", "react", "docker"], SAMPLE_JOBS)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_k_limits_results(self):
        results = rank_jobs("python", ["python"], SAMPLE_JOBS, top_k=2)
        assert len(results) <= 2

    def test_top_k_default_returns_all_when_less(self):
        results = rank_jobs("python", ["python"], SAMPLE_JOBS, top_k=100)
        assert len(results) == len(SAMPLE_JOBS)

    def test_empty_jobs_returns_empty(self):
        results = rank_jobs("python", ["python"], [], top_k=5)
        assert results == []


# ═════════════════════════════════════════════════════════════════
# Skill matching
# ═════════════════════════════════════════════════════════════════

class TestRankJobsSkillMatching:
    """Test skill overlap dan gap analysis."""

    def test_matched_skills_correct(self):
        results = rank_jobs(
            "I know python and tensorflow",
            ["python", "tensorflow"],
            SAMPLE_JOBS,
        )
        # Cari hasil untuk Data Scientist (j1)
        ds_result = next(r for r in results if r["job_id"] == "j1")
        assert "python" in ds_result["matched_skills"]
        assert "tensorflow" in ds_result["matched_skills"]

    def test_gap_skills_correct(self):
        results = rank_jobs(
            "I know python",
            ["python"],
            SAMPLE_JOBS,
        )
        ds_result = next(r for r in results if r["job_id"] == "j1")
        # python matched, tapi ml, tf, sql harusnya gap
        assert "python" not in ds_result["gap_skills"]
        assert len(ds_result["gap_skills"]) > 0

    def test_no_skill_overlap(self):
        results = rank_jobs(
            "I study philosophy and literature",
            ["philosophy"],
            SAMPLE_JOBS,
        )
        for r in results:
            assert len(r["matched_skills"]) == 0

    def test_full_skill_overlap_gets_higher_score(self):
        # CV yang punya semua skill Data Scientist
        results_full = rank_jobs(
            "python machine learning tensorflow sql",
            ["python", "machine learning", "tensorflow", "sql"],
            SAMPLE_JOBS,
        )
        # CV tanpa skill relevan
        results_none = rank_jobs(
            "cooking baking pastry",
            [],
            SAMPLE_JOBS,
        )
        ds_full = next(r for r in results_full if r["job_id"] == "j1")
        ds_none = next(r for r in results_none if r["job_id"] == "j1")
        assert ds_full["score"] > ds_none["score"]


# ═════════════════════════════════════════════════════════════════
# Relevance ranking
# ═════════════════════════════════════════════════════════════════

class TestRankJobsRelevance:
    """Test bahwa ranking masuk akal."""

    def test_python_cv_ranks_data_scientist_high(self):
        results = rank_jobs(
            "python machine learning tensorflow data science",
            ["python", "machine learning", "tensorflow"],
            SAMPLE_JOBS,
            top_k=3,
        )
        top_ids = [r["job_id"] for r in results]
        # Data Scientist (j1) harus di top 3
        assert "j1" in top_ids

    def test_react_cv_ranks_frontend_high(self):
        results = rank_jobs(
            "react typescript javascript css frontend development",
            ["react", "typescript", "javascript"],
            SAMPLE_JOBS,
            top_k=3,
        )
        top_ids = [r["job_id"] for r in results]
        assert "j2" in top_ids

    def test_docker_aws_ranks_devops_high(self):
        results = rank_jobs(
            "docker kubernetes aws cloud infrastructure linux",
            ["docker", "kubernetes", "aws", "linux"],
            SAMPLE_JOBS,
            top_k=3,
        )
        top_ids = [r["job_id"] for r in results]
        assert "j4" in top_ids
