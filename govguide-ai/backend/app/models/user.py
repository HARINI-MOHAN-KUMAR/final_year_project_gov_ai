"""
SQLAlchemy ORM model for User.
Stores authentication credentials and user profile data.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Represents a registered user of GovGuide AI."""

    __tablename__ = "users"

    # ── Identity ──────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # ── Roles ─────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Profile Fields ────────────────────────────────────────────────────
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(20))          # male / female / other
    annual_income: Mapped[Optional[float]] = mapped_column(Float)
    education: Mapped[Optional[str]] = mapped_column(String(50))       # class_10, graduate, etc.
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(20))        # General/OBC/SC/ST/EWS
    state: Mapped[Optional[str]] = mapped_column(String(100))
    disability: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    disability_percentage: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    marital_status: Mapped[Optional[str]] = mapped_column(String(30))  # single/married/widow/divorced
    residence: Mapped[Optional[str]] = mapped_column(String(10))       # rural / urban
    land_holding: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    bank_account: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(String(10), default="en")

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    applications: Mapped[list] = relationship("SchemeApplication", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[list] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
