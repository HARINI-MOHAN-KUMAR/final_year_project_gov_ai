"""
Pydantic schemas for User authentication and profile management.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    """Schema for registering a new user."""
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    full_name: str = Field(min_length=2, max_length=100)
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: Optional[str] = None
    is_admin: bool = False


# ── Profile Schemas ─────────────────────────────────────────────────────────

VALID_CATEGORIES = {"General", "OBC", "SC", "ST", "EWS"}
VALID_EDUCATION = {
    "class_8_pass", "class_9", "class_10", "class_11", "class_12",
    "diploma", "graduate", "postgraduate", "mphil", "phd", "dropout", "illiterate"
}
VALID_OCCUPATION = {
    "farmer", "laborer", "employee", "self_employed", "entrepreneur",
    "student", "unorganized_worker", "artisan", "craftsperson",
    "small_business", "retired", "unemployed", "housewife"
}
VALID_GENDER = {"male", "female", "other"}
VALID_MARITAL = {"single", "married", "widow", "widower", "divorced", "separated"}
VALID_RESIDENCE = {"rural", "urban"}


class ProfileUpdate(BaseModel):
    """Schema for updating user profile data."""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    annual_income: Optional[float] = Field(None, ge=0)
    education: Optional[str] = None
    occupation: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    disability: Optional[bool] = None
    disability_percentage: Optional[int] = Field(None, ge=0, le=100)
    marital_status: Optional[str] = None
    residence: Optional[str] = None
    land_holding: Optional[bool] = None
    bank_account: Optional[bool] = None
    preferred_language: Optional[str] = Field(None, pattern="^(en|ta|hi)$")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v and v not in VALID_GENDER:
            raise ValueError(f"gender must be one of {VALID_GENDER}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v

    @field_validator("education")
    @classmethod
    def validate_education(cls, v):
        if v and v not in VALID_EDUCATION:
            raise ValueError(f"education must be one of {VALID_EDUCATION}")
        return v

    @field_validator("marital_status")
    @classmethod
    def validate_marital(cls, v):
        if v and v not in VALID_MARITAL:
            raise ValueError(f"marital_status must be one of {VALID_MARITAL}")
        return v

    @field_validator("residence")
    @classmethod
    def validate_residence(cls, v):
        if v and v not in VALID_RESIDENCE:
            raise ValueError(f"residence must be one of {VALID_RESIDENCE}")
        return v


class ProfileRead(BaseModel):
    """Full user profile read response."""
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    annual_income: Optional[float]
    education: Optional[str]
    occupation: Optional[str]
    category: Optional[str]
    state: Optional[str]
    disability: Optional[bool]
    disability_percentage: Optional[int]
    marital_status: Optional[str]
    residence: Optional[str]
    land_holding: Optional[bool]
    bank_account: Optional[bool]
    preferred_language: Optional[str]
    is_admin: bool

    model_config = {"from_attributes": True}
