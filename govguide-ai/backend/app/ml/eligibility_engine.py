"""
Rule-Based Eligibility Engine for GovGuide AI.

For each scheme's eligibility_rules, this engine checks every criterion
against the user's profile and returns a per-criterion pass/fail breakdown.
This forms the foundation for both direct filtering and ML training labels.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Load scheme data ─────────────────────────────────────────────────────────

_SCHEMES_PATH = Path(__file__).parent.parent.parent.parent / "data" / "schemes.json"


def load_schemes() -> List[Dict]:
    """Load schemes from JSON file. Cached after first load."""
    try:
        with open(_SCHEMES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"schemes.json not found at {_SCHEMES_PATH}. Returning empty list.")
        return []


# Lazy-loaded scheme list
_schemes_cache: Optional[List[Dict]] = None


def get_schemes() -> List[Dict]:
    global _schemes_cache
    if _schemes_cache is None:
        _schemes_cache = load_schemes()
    return _schemes_cache


# ── Core Eligibility Checker ─────────────────────────────────────────────────

def check_scheme_eligibility(
    profile: Dict[str, Any],
    scheme: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check a user profile against a scheme's eligibility rules.

    Returns:
        (overall_pass: bool, criteria_details: dict)
        criteria_details maps each criterion to:
          {"passed": bool, "reason": str, "user_value": any, "required": any}
    """
    rules = scheme.get("eligibility_rules", {})
    criteria: Dict[str, Any] = {}
    all_passed = True

    # ── Age checks ──────────────────────────────────────────────────────────
    user_age = profile.get("age")

    if "age_min" in rules:
        req = rules["age_min"]
        passed = user_age is not None and user_age >= req
        criteria["age_min"] = {
            "passed": passed,
            "reason": f"Minimum age {req} years required",
            "user_value": user_age,
            "required": f">= {req}",
        }
        if not passed:
            all_passed = False

    if "age_max" in rules:
        req = rules["age_max"]
        passed = user_age is not None and user_age <= req
        criteria["age_max"] = {
            "passed": passed,
            "reason": f"Maximum age {req} years allowed",
            "user_value": user_age,
            "required": f"<= {req}",
        }
        if not passed:
            all_passed = False

    # ── Income check ────────────────────────────────────────────────────────
    if "income_limit" in rules:
        req = rules["income_limit"]
        user_income = profile.get("annual_income")
        passed = user_income is not None and user_income <= req
        criteria["income_limit"] = {
            "passed": passed,
            "reason": f"Annual income must be ≤ ₹{req:,}",
            "user_value": user_income,
            "required": f"<= {req}",
        }
        if not passed:
            all_passed = False

    # ── Category check ──────────────────────────────────────────────────────
    if "categories" in rules:
        req_cats = rules["categories"]
        user_cat = profile.get("category")
        passed = user_cat in req_cats
        criteria["category"] = {
            "passed": passed,
            "reason": f"Category must be one of: {', '.join(req_cats)}",
            "user_value": user_cat,
            "required": req_cats,
        }
        if not passed:
            all_passed = False

    # ── Category OR Gender (e.g., Stand-Up India) ───────────────────────────
    if "categories_or_gender" in rules:
        cog = rules["categories_or_gender"]
        req_cats = cog.get("categories", [])
        req_gender = cog.get("gender")
        user_cat = profile.get("category")
        user_gender = profile.get("gender")
        passed = user_cat in req_cats or user_gender == req_gender
        criteria["categories_or_gender"] = {
            "passed": passed,
            "reason": f"Must be in categories {req_cats} OR gender={req_gender}",
            "user_value": {"category": user_cat, "gender": user_gender},
            "required": cog,
        }
        if not passed:
            all_passed = False

    # ── Gender check ────────────────────────────────────────────────────────
    if "gender" in rules:
        req_gender = rules["gender"]
        user_gender = profile.get("gender")
        passed = user_gender == req_gender
        criteria["gender"] = {
            "passed": passed,
            "reason": f"Scheme is for {req_gender} applicants",
            "user_value": user_gender,
            "required": req_gender,
        }
        if not passed:
            all_passed = False

    # ── Occupation check ────────────────────────────────────────────────────
    if "occupation" in rules:
        req_occs = rules["occupation"]
        user_occ = profile.get("occupation")
        passed = user_occ in req_occs
        criteria["occupation"] = {
            "passed": passed,
            "reason": f"Occupation must be one of: {', '.join(req_occs)}",
            "user_value": user_occ,
            "required": req_occs,
        }
        if not passed:
            all_passed = False

    # ── State check ─────────────────────────────────────────────────────────
    if "state" in rules:
        req_state = rules["state"]
        user_state = profile.get("state")
        if req_state == "all":
            passed = True
            criteria["state"] = {
                "passed": True,
                "reason": "Available in all states",
                "user_value": user_state,
                "required": "All India",
            }
        else:
            passed = user_state == req_state
            criteria["state"] = {
                "passed": passed,
                "reason": f"Scheme is only for residents of {req_state}",
                "user_value": user_state,
                "required": req_state,
            }
            if not passed:
                all_passed = False

    # ── Education check ─────────────────────────────────────────────────────
    if "education" in rules:
        req_edus = rules["education"]
        user_edu = profile.get("education")
        passed = user_edu in req_edus
        criteria["education"] = {
            "passed": passed,
            "reason": f"Education level must be one of: {', '.join(req_edus)}",
            "user_value": user_edu,
            "required": req_edus,
        }
        if not passed:
            all_passed = False

    # ── Disability check ────────────────────────────────────────────────────
    if "disability" in rules and rules["disability"] is True:
        user_dis = profile.get("disability", False)
        dis_pct = profile.get("disability_percentage", 0)
        req_pct = rules.get("disability_percentage", 0)
        passed = user_dis is True and dis_pct >= req_pct
        criteria["disability"] = {
            "passed": passed,
            "reason": f"Requires disability certificate with ≥{req_pct}% disability",
            "user_value": {"disability": user_dis, "percentage": dis_pct},
            "required": f"disability=True, >={req_pct}%",
        }
        if not passed:
            all_passed = False

    # ── Marital status check ────────────────────────────────────────────────
    if "marital_status" in rules:
        req_ms = rules["marital_status"]
        user_ms = profile.get("marital_status")
        passed = user_ms == req_ms
        criteria["marital_status"] = {
            "passed": passed,
            "reason": f"Marital status must be: {req_ms}",
            "user_value": user_ms,
            "required": req_ms,
        }
        if not passed:
            all_passed = False

    # ── Residence check ─────────────────────────────────────────────────────
    if "residence" in rules:
        req_res = rules["residence"]
        user_res = profile.get("residence")
        passed = user_res == req_res
        criteria["residence"] = {
            "passed": passed,
            "reason": f"Residence must be: {req_res}",
            "user_value": user_res,
            "required": req_res,
        }
        if not passed:
            all_passed = False

    # ── Land holding check ──────────────────────────────────────────────────
    if rules.get("land_holding") is True:
        user_land = profile.get("land_holding", False)
        passed = user_land is True
        criteria["land_holding"] = {
            "passed": passed,
            "reason": "Applicant must own/cultivate agricultural land",
            "user_value": user_land,
            "required": True,
        }
        if not passed:
            all_passed = False

    # ── Bank account check ──────────────────────────────────────────────────
    if rules.get("bank_account") is True:
        user_bank = profile.get("bank_account", True)
        passed = user_bank is True
        criteria["bank_account"] = {
            "passed": passed,
            "reason": "Applicant must have a bank account",
            "user_value": user_bank,
            "required": True,
        }
        if not passed:
            all_passed = False

    # ── Family head check ───────────────────────────────────────────────────
    if rules.get("family_head") is True:
        user_fh = profile.get("family_head", False)
        passed = user_fh is True
        criteria["family_head"] = {
            "passed": passed,
            "reason": "Applicant must be the head of the family",
            "user_value": user_fh,
            "required": True,
        }
        if not passed:
            all_passed = False

    # If no specific rules matched, scheme is universally applicable
    if not criteria:
        criteria["universal"] = {
            "passed": True,
            "reason": "No specific eligibility restrictions",
            "user_value": None,
            "required": None,
        }

    return all_passed, criteria


# ── Profile Completeness ─────────────────────────────────────────────────────

IMPORTANT_FIELDS = [
    "age", "gender", "annual_income", "education", "occupation",
    "category", "state", "disability", "marital_status", "residence",
    "land_holding", "bank_account",
]


def compute_profile_completeness(profile: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Returns (completeness_ratio, list_of_missing_fields).
    completeness_ratio is between 0.0 and 1.0.
    """
    missing = [f for f in IMPORTANT_FIELDS if profile.get(f) is None]
    ratio = 1.0 - len(missing) / len(IMPORTANT_FIELDS)
    return round(ratio, 2), missing


# ── Profile dict from User ORM object ────────────────────────────────────────

def user_to_profile_dict(user) -> Dict[str, Any]:
    """Convert a User ORM object to a plain dict for the eligibility engine."""
    return {
        "age": user.age,
        "gender": user.gender,
        "annual_income": user.annual_income,
        "education": user.education,
        "occupation": user.occupation,
        "category": user.category,
        "state": user.state,
        "disability": user.disability,
        "disability_percentage": user.disability_percentage,
        "marital_status": user.marital_status,
        "residence": user.residence,
        "land_holding": user.land_holding,
        "bank_account": user.bank_account,
    }
