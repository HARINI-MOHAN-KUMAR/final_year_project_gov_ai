"""
SQLAlchemy ORM model for Document (OCR verification results).
Stores upload metadata, extracted fields, and validation status.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    """
    Represents a document uploaded by a user for OCR verification.
    Privacy: Aadhaar numbers are masked before storage.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    application_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("scheme_applications.id"), nullable=True
    )

    # Document info
    doc_type: Mapped[str] = mapped_column(String(50))  # aadhaar | income | community | marksheet | ration | passbook
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))  # server-side storage path
    mime_type: Mapped[str] = mapped_column(String(50))

    # OCR results (privacy-safe: Aadhaar masked)
    extracted_fields: Mapped[Optional[dict]] = mapped_column(JSON)
    raw_text_excerpt: Mapped[Optional[str]] = mapped_column(Text)  # First 500 chars only

    # Validation
    status: Mapped[str] = mapped_column(String(20), default="Pending")  # Pending | Valid | Warning | Invalid
    validation_errors: Mapped[Optional[dict]] = mapped_column(JSON)
    suggested_fixes: Mapped[Optional[dict]] = mapped_column(JSON)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    # Expiry
    issue_date: Mapped[Optional[str]] = mapped_column(String(30))
    expiry_date: Mapped[Optional[str]] = mapped_column(String(30))
    is_expired: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    application: Mapped[Optional["SchemeApplication"]] = relationship(
        "SchemeApplication", back_populates="documents"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} type={self.doc_type} status={self.status}>"
