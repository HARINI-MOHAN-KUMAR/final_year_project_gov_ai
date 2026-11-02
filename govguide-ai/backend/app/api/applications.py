"""Applications API router – scheme application tracking with status management."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scheme_app import SchemeApplication
from app.models.document import Document
from app.schemas.scheme import ApplicationCreate, ApplicationUpdate, ApplicationRead

router = APIRouter()

VALID_STATUSES = {"Planned", "In Progress", "Submitted", "Approved", "Rejected"}


@router.post("/", response_model=ApplicationRead, status_code=201,
             summary="Save a scheme application")
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a scheme to the user's application tracker."""
    # Prevent duplicate entries
    result = await db.execute(
        select(SchemeApplication).where(
            SchemeApplication.user_id == current_user.id,
            SchemeApplication.scheme_id == payload.scheme_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Application for this scheme already exists")

    app = SchemeApplication(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(app)
    await db.flush()
    await db.refresh(app)

    # Attach document count
    doc_count = await _get_doc_count(db, app.id)
    app_read = ApplicationRead.model_validate(app)
    app_read.document_count = doc_count
    return app_read


@router.get("/", response_model=List[ApplicationRead], summary="List all saved applications")
async def list_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all scheme applications for the current user with document counts."""
    result = await db.execute(
        select(SchemeApplication)
        .where(SchemeApplication.user_id == current_user.id)
        .order_by(SchemeApplication.updated_at.desc())
    )
    applications = result.scalars().all()

    out = []
    for app in applications:
        doc_count = await _get_doc_count(db, app.id)
        app_read = ApplicationRead.model_validate(app)
        app_read.document_count = doc_count
        out.append(app_read)
    return out


@router.get("/{app_id}", response_model=ApplicationRead, summary="Get a single application")
async def get_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = await _get_app_or_404(db, app_id, current_user.id)
    doc_count = await _get_doc_count(db, app.id)
    app_read = ApplicationRead.model_validate(app)
    app_read.document_count = doc_count
    return app_read


@router.put("/{app_id}", response_model=ApplicationRead, summary="Update application status/notes")
async def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status or notes of a tracked application."""
    app = await _get_app_or_404(db, app_id, current_user.id)

    if payload.status and payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    db.add(app)
    await db.flush()
    await db.refresh(app)

    doc_count = await _get_doc_count(db, app.id)
    app_read = ApplicationRead.model_validate(app)
    app_read.document_count = doc_count
    return app_read


@router.delete("/{app_id}", status_code=204, summary="Remove a saved application")
async def delete_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a scheme from the user's application tracker."""
    app = await _get_app_or_404(db, app_id, current_user.id)
    await db.delete(app)


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _get_app_or_404(db: AsyncSession, app_id: int, user_id: int) -> SchemeApplication:
    result = await db.execute(
        select(SchemeApplication).where(
            SchemeApplication.id == app_id,
            SchemeApplication.user_id == user_id,
        )
    )
    app = result.scalar_one_or_none()
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


async def _get_doc_count(db: AsyncSession, application_id: int) -> int:
    result = await db.execute(
        select(func.count(Document.id)).where(Document.application_id == application_id)
    )
    return result.scalar() or 0
