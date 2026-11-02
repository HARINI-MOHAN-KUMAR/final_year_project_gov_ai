"""OCR API router – document upload, processing, and verification."""

import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.ocr.processor import process_document
from app.schemas.scheme import DocumentRead
from app.ml.eligibility_engine import user_to_profile_dict

router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

VALID_DOC_TYPES = {
    "aadhaar", "income_certificate", "community_certificate",
    "marksheet", "ration_card", "bank_passbook",
}


@router.post("/upload", response_model=DocumentRead, status_code=201,
             summary="Upload and verify a document via OCR")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    application_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document (JPG/PNG/PDF) for OCR verification.

    **Privacy Note**: Aadhaar numbers are automatically masked in all storage
    and responses. Only the last 4 digits are retained.

    Processing pipeline:
    1. Validate file type and size
    2. Preprocess image (grayscale, denoise, deskew)
    3. Run Tesseract OCR
    4. Extract fields via regex + NLP
    5. Validate against scheme requirements and user profile
    6. Return per-field status with suggested fixes
    """
    # Validate doc_type
    if doc_type not in VALID_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid doc_type. Must be one of: {', '.join(sorted(VALID_DOC_TYPES))}",
        )

    # Validate file type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type '{content_type}' not supported")

    # Read file and check size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum 10 MB allowed.")

    # Save file to disk
    ext = Path(file.filename or "upload").suffix or ".jpg"
    safe_filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / safe_filename
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Process OCR
    profile = user_to_profile_dict(current_user)
    profile["full_name"] = current_user.full_name

    ocr_result = await process_document(
        file_bytes=file_bytes,
        filename=file.filename or safe_filename,
        doc_type=doc_type,
        user_profile=profile,
    )

    # Persist to database
    doc = Document(
        user_id=current_user.id,
        application_id=application_id,
        doc_type=doc_type,
        original_filename=file.filename or safe_filename,
        file_path=str(file_path),
        **ocr_result,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return doc


@router.get("/", response_model=List[DocumentRead], summary="List all uploaded documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all documents uploaded by the current user."""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


@router.get("/{doc_id}", response_model=DocumentRead, summary="Get document details")
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get OCR results and validation status for a specific document."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204, summary="Delete a document")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document record and its file."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete physical file
    try:
        Path(doc.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    await db.delete(doc)
