"""
Tests: CV Parser service — skill extraction dan text processing.
Tidak memerlukan database atau network.
"""
import pytest

from app.services.cv_parser import extract_skills, SKILL_GAZETTEER, SYNONYM_MAP


# ═════════════════════════════════════════════════════════════════
# extract_skills — Bahasa Inggris
# ═════════════════════════════════════════════════════════════════

class TestExtractSkillsEnglish:
    """Test ekstraksi skill dari teks berbahasa Inggris."""

    def test_detects_single_word_skill(self):
        text = "Experienced in Python programming and Docker deployment"
        skills = extract_skills(text)
        assert "python" in skills
        assert "docker" in skills

    def test_detects_multi_word_skill(self):
        text = "Strong background in machine learning and data analysis"
        skills = extract_skills(text)
        assert "machine learning" in skills
        assert "data analysis" in skills

    def test_detects_framework_names(self):
        text = "Built APIs with FastAPI and frontend with React and Vue"
        skills = extract_skills(text)
        assert "fastapi" in skills
        assert "react" in skills
        assert "vue" in skills

    def test_detects_database_skills(self):
        text = "Managed PostgreSQL and Redis databases in production"
        skills = extract_skills(text)
        assert "postgresql" in skills
        assert "redis" in skills

    def test_detects_cloud_platforms(self):
        text = "Deployed on AWS and configured GCP services"
        skills = extract_skills(text)
        assert "aws" in skills
        assert "gcp" in skills

    def test_detects_tools(self):
        text = "Version control with Git and GitHub, containerized with Docker"
        skills = extract_skills(text)
        assert "git" in skills
        assert "github" in skills
        assert "docker" in skills

    def test_returns_sorted_list(self):
        text = "Python, React, Docker, AWS"
        skills = extract_skills(text)
        assert skills == sorted(skills)

    def test_no_duplicates(self):
        text = "Python python PYTHON Python"
        skills = extract_skills(text)
        assert skills.count("python") == 1


# ═════════════════════════════════════════════════════════════════
# extract_skills — Bahasa Indonesia
# ═════════════════════════════════════════════════════════════════

class TestExtractSkillsIndonesian:
    """Test ekstraksi skill dari teks berbahasa Indonesia."""

    def test_detects_indonesian_skills(self):
        text = "Memiliki kemampuan kepemimpinan dan komunikasi yang baik"
        skills = extract_skills(text)
        assert "leadership" in skills  # kepemimpinan → leadership (synonym)
        assert "komunikasi" in skills or "communication" in skills

    def test_synonym_normalization(self):
        text = "Berpengalaman dalam manajemen proyek besar"
        skills = extract_skills(text)
        assert "project management" in skills

    def test_kecerdasan_buatan_maps_to_ml(self):
        text = "Mendalami kecerdasan buatan dan pembelajaran mesin"
        skills = extract_skills(text)
        assert "machine learning" in skills

    def test_jaringan_syaraf_maps_to_dl(self):
        text = "Penelitian tentang jaringan syaraf tiruan"
        skills = extract_skills(text)
        assert "deep learning" in skills


# ═════════════════════════════════════════════════════════════════
# extract_skills — Edge cases
# ═════════════════════════════════════════════════════════════════

class TestExtractSkillsEdgeCases:
    """Test edge cases untuk extract_skills."""

    def test_empty_string(self):
        assert extract_skills("") == []

    def test_no_skills_found(self):
        text = "Saya suka makan nasi goreng di warung"
        skills = extract_skills(text)
        assert len(skills) == 0

    def test_case_insensitive(self):
        text = "PYTHON JavaScript Docker"
        skills = extract_skills(text)
        assert "python" in skills
        assert "javascript" in skills
        assert "docker" in skills

    def test_mixed_bilingual_text(self):
        text = "Saya berpengalaman 3 tahun menggunakan Python dan React untuk web development. Mampu leadership tim."
        skills = extract_skills(text)
        assert "python" in skills
        assert "react" in skills
        assert "leadership" in skills

    def test_skill_with_special_chars(self):
        """C++ dan C# harus terdeteksi dengan lookaround regex."""
        text = "Proficient in C++ and C# programming"
        skills = extract_skills(text)
        assert "c++" in skills
        assert "c#" in skills

    def test_rest_api_multi_word(self):
        text = "Built REST API services for mobile apps"
        skills = extract_skills(text)
        assert "rest api" in skills


# ═════════════════════════════════════════════════════════════════
# Gazetteer & Synonym integrity
# ═════════════════════════════════════════════════════════════════

class TestGazetteerIntegrity:
    """Validasi konsistensi data gazetteer dan synonym."""

    def test_gazetteer_is_not_empty(self):
        assert len(SKILL_GAZETTEER) > 20

    def test_gazetteer_all_lowercase(self):
        for skill in SKILL_GAZETTEER:
            assert skill == skill.lower(), f"Skill '{skill}' bukan lowercase"

    def test_synonym_keys_are_lowercase(self):
        for key in SYNONYM_MAP:
            assert key == key.lower(), f"Synonym key '{key}' bukan lowercase"

    def test_synonym_values_in_gazetteer(self):
        """Setiap canonical skill dari synonym harus ada di gazetteer."""
        for indo, canonical in SYNONYM_MAP.items():
            assert canonical in SKILL_GAZETTEER, (
                f"Synonym target '{canonical}' (dari '{indo}') "
                f"tidak ada di SKILL_GAZETTEER"
            )
