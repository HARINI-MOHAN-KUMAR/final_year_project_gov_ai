"""
Pydantic schemas for Scheme recommendation, application tracking,
chat sessions, documents, and admin operations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ── Scheme Schemas ──────────────────────────────────────────────────────────

class SchemeBase(BaseModel):
    """Minimal scheme info."""
    id: str
    name: str
    category: str
    description: str
    benefits: str
    official_url: str
    deadline: str
    state_applicability: str
    tags: List[str] = []


class SchemeFull(SchemeBase):
    """Full scheme details including eligibility rules and documents."""
    eligibility_rules: Dict[str, Any]
    required_documents: List[str]


class SchemeRecommendation(BaseModel):
    """Recommendation result for a single scheme."""
    scheme: SchemeFull
    match_score: float = Field(ge=0.0, le=1.0)
    rule_passed: bool
    criteria_details: Dict[str, Any]  # per-criterion pass/fail
    feature_importance: Optional[Dict[str, float]] = None  # SHAP-style
    missing_info: List[str] = []


class RecommendationRequest(BaseModel):
    """Optional override profile for recommendation (uses saved profile by default)."""
    top_n: int = Field(default=10, ge=1, le=40)
    state_filter: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response containing ranked scheme recommendations."""
    recommendations: List[SchemeRecommendation]
    profile_completeness: float
    missing_profile_fields: List[str]
    disclaimer: str = (
        "This is an advisory tool only. Recommendations are based on the information "
        "you provided and may not be exhaustive. Please verify eligibility on official portals."
    )


# ── Application Schemas ─────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    """Create a new scheme application."""
    scheme_id: str
    scheme_name: str
    status: str = "Planned"
    notes: Optional[str] = None
    deadline: Optional[str] = None
    match_score: Optional[float] = None
    eligibility_passed: Optional[bool] = None
    criteria_details: Optional[Dict[str, Any]] = None


class ApplicationUpdate(BaseModel):
    """Update application status or notes."""
    status: Optional[str] = None
    notes: Optional[str] = None
    deadline: Optional[str] = None


class ApplicationRead(BaseModel):
    """Full application read response."""
    id: int
    scheme_id: str
    scheme_name: str
    status: str
    match_score: Optional[float]
    eligibility_passed: Optional[bool]
    criteria_details: Optional[Dict[str, Any]]
    notes: Optional[str]
    deadline: Optional[str]
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}


# ── Chat Schemas ────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field, model_validator

class ChatMessageCreate(BaseModel):
    """User sends a message to the chatbot."""
    content: Optional[str] = None
    message: Optional[str] = None
    session_id: Optional[int] = None
    language: str = Field(default="en", pattern="^(en|ta|hi|bn)$")

    @model_validator(mode="after")
    def populate_content(self):
        text = (self.content or self.message or "").strip()
        if not text:
            raise ValueError("Message content cannot be empty")
        self.content = text
        return self


class ChatMessageRead(BaseModel):
    """A single message in a chat session."""
    id: Optional[int] = 0
    role: str
    content: str
    response: Optional[str] = None
    sources: Optional[List[Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatSessionRead(BaseModel):
    """Chat session with messages."""
    id: int
    title: str
    language: str
    messages: List[ChatMessageRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Document Schemas ────────────────────────────────────────────────────────

class DocumentRead(BaseModel):
    """OCR document verification result."""
    id: int
    doc_type: str
    original_filename: str
    status: str
    extracted_fields: Optional[Dict[str, Any]]
    validation_errors: Optional[Dict[str, Any]]
    suggested_fixes: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    is_expired: Optional[bool]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ── Admin Schemas ───────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    """Admin analytics dashboard data."""
    total_users: int
    total_applications: int
    total_documents: int
    total_chat_sessions: int
    top_recommended_schemes: List[Dict[str, Any]]
    users_by_category: Dict[str, int]
    ocr_status_breakdown: Dict[str, int]
    application_status_breakdown: Dict[str, int]
