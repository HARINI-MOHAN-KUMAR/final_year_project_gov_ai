"""
SQLAlchemy ORM models for SchemeApplication and related tracking.
Tracks application lifecycle from Planned → Submitted → Approved/Rejected.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Text, Float, Boolean, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SchemeApplication(Base):
    """
    Tracks a user's application for a government scheme.
    Status transitions: Planned → In Progress → Submitted → Approved | Rejected
    """

    __tablename__ = "scheme_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # from schemes.json
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(30), default="Planned"
    )  # Planned | In Progress | Submitted | Approved | Rejected

    # Match info
    match_score: Mapped[Optional[float]] = mapped_column(Float)
    eligibility_passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    criteria_details: Mapped[Optional[dict]] = mapped_column(JSON)  # per-criterion pass/fail

    # Notes and reminders
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deadline: Mapped[Optional[str]] = mapped_column(String(100))
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    documents: Mapped[list] = relationship(
        "Document", back_populates="application", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SchemeApplication id={self.id} scheme={self.scheme_id} status={self.status}>"
