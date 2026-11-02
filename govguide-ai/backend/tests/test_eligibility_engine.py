"""
Unit tests for the Rule-Based Eligibility Engine.

Tests every major criterion type: age, income, category, gender,
occupation, state, education, disability, marital status, residence, land.
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.eligibility_engine import check_scheme_eligibility, compute_profile_completeness


# ── Sample scheme fixtures ────────────────────────────────────────────────────

SCHEME_FARMER_INCOME = {
    "id": "TEST_FARMER",
    "name": "Test Farmer Scheme",
    "eligibility_rules": {
        "occupation": ["farmer"],
        "income_limit": 200000,
        "state": "all",
        "age_min": 18,
        "land_holding": True,
    },
}

SCHEME_WOMEN_WIDOW = {
    "id": "TEST_WIDOW",
    "name": "Test Widow Pension",
    "eligibility_rules": {
        "gender": "female",
        "marital_status": "widow",
        "age_min": 40,
        "age_max": 59,
        "income_limit": 120000,
        "state": "all",
    },
}

SCHEME_SC_STUDENT = {
    "id": "TEST_SC_STUDENT",
    "name": "Test SC Scholarship",
    "eligibility_rules": {
        "categories": ["SC", "ST"],
        "education": ["class_10", "class_11", "class_12"],
        "income_limit": 250000,
        "state": "all",
    },
}

SCHEME_DISABILITY = {
    "id": "TEST_DISABILITY",
    "name": "Test Disability Pension",
    "eligibility_rules": {
        "disability": True,
        "disability_percentage": 80,
        "income_limit": 120000,
        "age_min": 18,
        "state": "all",
    },
}

SCHEME_TN_ONLY = {
    "id": "TEST_TN",
    "name": "Test TN Scheme",
    "eligibility_rules": {
        "state": "Tamil Nadu",
    },
}

SCHEME_UNIVERSAL = {
    "id": "TEST_UNIVERSAL",
    "name": "Test Universal Scheme",
    "eligibility_rules": {},
}


# ── Base profiles ─────────────────────────────────────────────────────────────

BASE_FARMER = {
    "age": 35,
    "gender": "male",
    "annual_income": 150000,
    "education": "class_10",
    "occupation": "farmer",
    "category": "OBC",
    "state": "Tamil Nadu",
    "disability": False,
    "disability_percentage": 0,
    "marital_status": "married",
    "residence": "rural",
    "land_holding": True,
    "bank_account": True,
}

BASE_WIDOW = {
    "age": 45,
    "gender": "female",
    "annual_income": 80000,
    "occupation": "housewife",
    "category": "General",
    "state": "Maharashtra",
    "disability": False,
    "marital_status": "widow",
    "residence": "rural",
    "land_holding": False,
    "bank_account": True,
}

BASE_SC_STUDENT = {
    "age": 17,
    "gender": "female",
    "annual_income": 100000,
    "education": "class_11",
    "occupation": "student",
    "category": "SC",
    "state": "Karnataka",
    "disability": False,
    "marital_status": "single",
    "residence": "rural",
    "land_holding": False,
    "bank_account": True,
}


# ── Eligibility Engine Tests ──────────────────────────────────────────────────

class TestFarmerScheme:
    def test_eligible_farmer(self):
        passed, criteria = check_scheme_eligibility(BASE_FARMER, SCHEME_FARMER_INCOME)
        assert passed is True
        assert criteria["occupation"]["passed"] is True
        assert criteria["income_limit"]["passed"] is True
        assert criteria["land_holding"]["passed"] is True

    def test_ineligible_wrong_occupation(self):
        profile = {**BASE_FARMER, "occupation": "employee"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert passed is False
        assert criteria["occupation"]["passed"] is False

    def test_ineligible_over_income(self):
        profile = {**BASE_FARMER, "annual_income": 300000}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert passed is False
        assert criteria["income_limit"]["passed"] is False

    def test_ineligible_under_age(self):
        profile = {**BASE_FARMER, "age": 16}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert passed is False
        assert criteria["age_min"]["passed"] is False

    def test_ineligible_no_land(self):
        profile = {**BASE_FARMER, "land_holding": False}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert passed is False
        assert criteria["land_holding"]["passed"] is False

    def test_exactly_at_income_limit(self):
        profile = {**BASE_FARMER, "annual_income": 200000}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert criteria["income_limit"]["passed"] is True


class TestWidowPension:
    def test_eligible_widow(self):
        passed, criteria = check_scheme_eligibility(BASE_WIDOW, SCHEME_WOMEN_WIDOW)
        assert passed is True
        assert criteria["gender"]["passed"] is True
        assert criteria["marital_status"]["passed"] is True

    def test_ineligible_male(self):
        profile = {**BASE_WIDOW, "gender": "male"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_WOMEN_WIDOW)
        assert passed is False
        assert criteria["gender"]["passed"] is False

    def test_ineligible_not_widow(self):
        profile = {**BASE_WIDOW, "marital_status": "married"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_WOMEN_WIDOW)
        assert passed is False
        assert criteria["marital_status"]["passed"] is False

    def test_ineligible_too_young(self):
        profile = {**BASE_WIDOW, "age": 35}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_WOMEN_WIDOW)
        assert passed is False
        assert criteria["age_min"]["passed"] is False

    def test_ineligible_too_old(self):
        profile = {**BASE_WIDOW, "age": 65}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_WOMEN_WIDOW)
        assert passed is False
        assert criteria["age_max"]["passed"] is False


class TestSCScholarship:
    def test_eligible_sc_student(self):
        passed, criteria = check_scheme_eligibility(BASE_SC_STUDENT, SCHEME_SC_STUDENT)
        assert passed is True
        assert criteria["category"]["passed"] is True
        assert criteria["education"]["passed"] is True

    def test_eligible_st_student(self):
        profile = {**BASE_SC_STUDENT, "category": "ST"}
        passed, _ = check_scheme_eligibility(profile, SCHEME_SC_STUDENT)
        assert passed is True

    def test_ineligible_obc(self):
        profile = {**BASE_SC_STUDENT, "category": "OBC"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_SC_STUDENT)
        assert passed is False
        assert criteria["category"]["passed"] is False

    def test_ineligible_graduate(self):
        profile = {**BASE_SC_STUDENT, "education": "graduate"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_SC_STUDENT)
        assert passed is False
        assert criteria["education"]["passed"] is False


class TestDisabilityScheme:
    def test_eligible_with_disability(self):
        profile = {
            **BASE_FARMER,
            "disability": True,
            "disability_percentage": 85,
            "annual_income": 100000,
        }
        passed, criteria = check_scheme_eligibility(profile, SCHEME_DISABILITY)
        assert passed is True
        assert criteria["disability"]["passed"] is True

    def test_ineligible_low_disability_percentage(self):
        profile = {**BASE_FARMER, "disability": True, "disability_percentage": 50, "annual_income": 100000}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_DISABILITY)
        assert passed is False
        assert criteria["disability"]["passed"] is False

    def test_ineligible_no_disability(self):
        profile = {**BASE_FARMER, "disability": False, "disability_percentage": 0, "annual_income": 100000}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_DISABILITY)
        assert passed is False


class TestStateScheme:
    def test_eligible_tn_resident(self):
        profile = {**BASE_FARMER, "state": "Tamil Nadu"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_TN_ONLY)
        assert passed is True
        assert criteria["state"]["passed"] is True

    def test_ineligible_other_state(self):
        profile = {**BASE_FARMER, "state": "Maharashtra"}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_TN_ONLY)
        assert passed is False
        assert criteria["state"]["passed"] is False


class TestUniversalScheme:
    def test_everyone_eligible(self):
        for profile in [BASE_FARMER, BASE_WIDOW, BASE_SC_STUDENT]:
            passed, criteria = check_scheme_eligibility(profile, SCHEME_UNIVERSAL)
            assert passed is True


class TestProfileCompleteness:
    def test_complete_profile(self):
        completeness, missing = compute_profile_completeness(BASE_FARMER)
        assert completeness > 0.8
        assert len(missing) < 3

    def test_empty_profile(self):
        completeness, missing = compute_profile_completeness({})
        assert completeness == 0.0
        assert len(missing) > 0

    def test_partial_profile(self):
        partial = {"age": 30, "gender": "female"}
        completeness, missing = compute_profile_completeness(partial)
        assert 0.0 < completeness < 0.5
        assert "annual_income" in missing
        assert "category" in missing


class TestCriteriaDetails:
    def test_criteria_has_required_fields(self):
        """Each criterion must have passed, reason, user_value, required."""
        _, criteria = check_scheme_eligibility(BASE_FARMER, SCHEME_FARMER_INCOME)
        for key, detail in criteria.items():
            assert "passed" in detail, f"Missing 'passed' in criterion '{key}'"
            assert "reason" in detail, f"Missing 'reason' in criterion '{key}'"
            assert "user_value" in detail, f"Missing 'user_value' in criterion '{key}'"
            assert "required" in detail, f"Missing 'required' in criterion '{key}'"

    def test_missing_profile_value_fails_criterion(self):
        """A None profile field should fail the criterion gracefully."""
        profile = {**BASE_FARMER, "age": None}
        passed, criteria = check_scheme_eligibility(profile, SCHEME_FARMER_INCOME)
        assert criteria["age_min"]["passed"] is False
