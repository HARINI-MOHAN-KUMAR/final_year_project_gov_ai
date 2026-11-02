"""Schemes API router – list, detail, and AI-powered recommendations."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.models.user import User
from app.ml.eligibility_engine import (
    get_schemes, check_scheme_eligibility,
    compute_profile_completeness, user_to_profile_dict
)
from app.ml.recommender import get_recommender
from app.schemas.scheme import (
    SchemeFull, SchemeRecommendation, RecommendationRequest, RecommendationResponse
)

router = APIRouter()


@router.get("/", response_model=List[SchemeFull], summary="List all schemes")
async def list_schemes(
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """
    Return all schemes, optionally filtered by category, state, or search keyword.
    """
    schemes = get_schemes()

    if category:
        schemes = [s for s in schemes if s.get("category", "").lower() == category.lower()]
    if state:
        schemes = [s for s in schemes if
                   s.get("state_applicability", "All India").lower() in ("all india", state.lower())]
    if search:
        q = search.lower()
        schemes = [s for s in schemes if
                   q in s.get("name", "").lower() or
                   q in s.get("description", "").lower() or
                   any(q in tag for tag in s.get("tags", []))]

    return schemes


@router.get("/categories", summary="List all scheme categories")
async def list_categories():
    """Return the list of distinct scheme categories."""
    schemes = get_schemes()
    categories = sorted(set(s["category"] for s in schemes))
    return {"categories": categories}


@router.get("/{scheme_id}", response_model=SchemeFull, summary="Get a specific scheme by ID")
async def get_scheme(scheme_id: str):
    """Return full details for a single scheme."""
    schemes = get_schemes()
    for s in schemes:
        if s["id"] == scheme_id:
            return s
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")


@router.post("/recommend", response_model=RecommendationResponse,
             summary="Get personalized scheme recommendations")
async def recommend_schemes(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Hybrid recommendation engine:
    1. Rule-based eligibility check (pass/fail per criterion)
    2. Random Forest ranking score
    Returns top-N schemes sorted by combined match score with explanations.
    """
    profile = user_to_profile_dict(current_user)
    completeness, missing_fields = compute_profile_completeness(profile)
    schemes = get_schemes()
    recommender = get_recommender()

    recommendations = []
    for scheme in schemes:
        # Apply optional state filter
        if request.state_filter:
            state_app = scheme.get("state_applicability", "All India")
            if request.state_filter.lower() not in state_app.lower() and state_app != "All India":
                continue

        # Rule-based check
        rule_passed, criteria = check_scheme_eligibility(profile, scheme)

        # ML score
        ml_score = recommender.predict_score(profile, scheme) if recommender.model else 0.5

        # Combined score: 60% ML + 40% rule eligibility
        rule_score = sum(1 for c in criteria.values() if c["passed"]) / max(len(criteria), 1)
        combined_score = round(0.6 * ml_score + 0.4 * rule_score, 4)

        # Feature importance
        feature_importance = recommender.get_feature_importance(profile, scheme)

        # Missing profile info that could unlock this scheme
        missing_info = [
            k for k, v in criteria.items()
            if not v["passed"] and v.get("user_value") is None
        ]

        recommendations.append(
            SchemeRecommendation(
                scheme=scheme,
                match_score=combined_score,
                rule_passed=rule_passed,
                criteria_details=criteria,
                feature_importance=feature_importance,
                missing_info=missing_info,
            )
        )

    # Sort by score descending, then by rule_passed (eligible first)
    recommendations.sort(key=lambda r: (r.rule_passed, r.match_score), reverse=True)

    return RecommendationResponse(
        recommendations=recommendations[: request.top_n],
        profile_completeness=completeness,
        missing_profile_fields=missing_fields,
    )
