"""
Tests: Data cleaning pipeline.
Tidak memerlukan database atau network — pure data transformation tests.
"""
import pytest

from app.cleaning.clean_raw_data import (
    normalize_text,
    normalize_title,
    normalize_location,
    parse_salary,
    extract_skills_from_title,
)


# ═════════════════════════════════════════════════════════════════
# normalize_text
# ═════════════════════════════════════════════════════════════════

class TestNormalizeText:

    def test_strips_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_collapses_multiple_spaces(self):
        assert normalize_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        assert normalize_text("hello\n\nworld") == "hello world"

    def test_removes_control_chars(self):
        assert normalize_text("hello\x00world") == "helloworld"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_none_returns_empty(self):
        assert normalize_text(None) == ""

    def test_non_string_returns_empty(self):
        assert normalize_text(123) == ""


# ═════════════════════════════════════════════════════════════════
# normalize_title
# ═════════════════════════════════════════════════════════════════

class TestNormalizeTitle:

    def test_strips_remote_suffix(self):
        result = normalize_title("Backend Engineer - Remote")
        assert "Remote" not in result
        assert "Backend Engineer" in result

    def test_strips_wfh_suffix(self):
        result = normalize_title("Data Analyst – WFH")
        assert "WFH" not in result

    def test_preserves_normal_title(self):
        assert normalize_title("Senior Python Developer") == "Senior Python Developer"

    def test_empty_input(self):
        assert normalize_title("") == ""


# ═════════════════════════════════════════════════════════════════
# normalize_location
# ═════════════════════════════════════════════════════════════════

class TestNormalizeLocation:

    def test_maps_jakarta_selatan(self):
        result = normalize_location("Jakarta Selatan, DKI Jakarta")
        assert "Jakarta Selatan" in result

    def test_maps_lowercase(self):
        assert normalize_location("jakarta selatan") == "Jakarta Selatan, DKI Jakarta"

    def test_maps_bandung(self):
        assert normalize_location("bandung") == "Bandung, Jawa Barat"

    def test_maps_surabaya(self):
        result = normalize_location("surabaya")
        assert "Surabaya" in result

    def test_unknown_location_title_cased(self):
        result = normalize_location("kota kecil baru")
        assert result == "Kota Kecil Baru"

    def test_empty_returns_empty(self):
        assert normalize_location("") == ""

    def test_none_returns_empty(self):
        assert normalize_location(None) == ""

    def test_partial_match(self):
        result = normalize_location("Kab. Tangerang, Banten")
        assert "Tangerang" in result


# ═════════════════════════════════════════════════════════════════
# parse_salary
# ═════════════════════════════════════════════════════════════════

class TestParseSalary:

    def test_rp_jt_range(self):
        mn, mx = parse_salary("Rp 5 jt-7 jt")
        assert mn == 5_000_000
        assert mx == 7_000_000

    def test_rp_jt_decimal(self):
        mn, mx = parse_salary("Rp 2,8 jt-3,5 jt")
        assert mn == 2_800_000
        assert mx == 3_500_000

    def test_single_value(self):
        mn, mx = parse_salary("Rp 10 jt")
        assert mn == 10_000_000
        assert mx == 10_000_000

    def test_tidak_ditampilkan(self):
        mn, mx = parse_salary("Gaji Tidak Ditampilkan")
        assert mn is None
        assert mx is None

    def test_not_specified(self):
        mn, mx = parse_salary("Not specified")
        assert mn is None
        assert mx is None

    def test_empty_string(self):
        mn, mx = parse_salary("")
        assert mn is None
        assert mx is None

    def test_none_input(self):
        mn, mx = parse_salary(None)
        assert mn is None
        assert mx is None

    def test_rb_unit(self):
        mn, mx = parse_salary("Rp 800 rb-1 jt")
        assert mn == 800_000
        assert mx == 1_000_000


# ═════════════════════════════════════════════════════════════════
# extract_skills_from_title
# ═════════════════════════════════════════════════════════════════

class TestExtractSkillsFromTitle:

    def test_python_in_title(self):
        skills = extract_skills_from_title("Python Developer")
        assert "python" in skills

    def test_multiple_skills(self):
        skills = extract_skills_from_title("Web Developer (Java, Golang + Rust)")
        assert "java" in skills
        assert "golang" in skills or "go" in skills
        assert "rust" in skills

    def test_multi_word_skill(self):
        skills = extract_skills_from_title("Machine Learning Engineer")
        assert "machine learning" in skills

    def test_data_analyst(self):
        skills = extract_skills_from_title("Data Analyst Intern")
        assert "data analyst" in skills

    def test_fullstack(self):
        skills = extract_skills_from_title("Full Stack Developer")
        assert "full stack" in skills

    def test_no_skills(self):
        skills = extract_skills_from_title("Office Manager")
        assert len(skills) == 0

    def test_empty_title(self):
        skills = extract_skills_from_title("")
        assert skills == []

    def test_returns_sorted(self):
        skills = extract_skills_from_title("Python React Docker AWS")
        assert skills == sorted(skills)
