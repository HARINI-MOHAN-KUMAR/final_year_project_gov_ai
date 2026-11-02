"""Admin API router – scheme management, analytics, and RAG re-indexing."""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.user import User
from app.models.scheme_app import SchemeApplication
from app.models.document import Document
from app.models.chat import ChatSession
from app.schemas.scheme import AnalyticsResponse
from app.ml.eligibility_engine import get_schemes, _schemes_cache
from app.rag.engine import get_rag
from app.core.config import settings

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse, summary="Admin analytics dashboard")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Return platform analytics for the admin dashboard."""
    # Totals
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_apps = (await db.execute(select(func.count(SchemeApplication.id)))).scalar() or 0
    total_docs = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    total_chats = (await db.execute(select(func.count(ChatSession.id)))).scalar() or 0

    # Top recommended schemes (by application count)
    top_schemes_result = await db.execute(
        select(SchemeApplication.scheme_id, SchemeApplication.scheme_name, func.count(SchemeApplication.id).label("count"))
        .group_by(SchemeApplication.scheme_id, SchemeApplication.scheme_name)
        .order_by(func.count(SchemeApplication.id).desc())
        .limit(10)
    )
    top_schemes = [
        {"scheme_id": r.scheme_id, "scheme_name": r.scheme_name, "count": r.count}
        for r in top_schemes_result.all()
    ]

    # Users by category
    cat_result = await db.execute(
        select(User.category, func.count(User.id).label("count"))
        .where(User.category.isnot(None))
        .group_by(User.category)
    )
    users_by_category = {r.category: r.count for r in cat_result.all()}

    # OCR status breakdown
    ocr_result = await db.execute(
        select(Document.status, func.count(Document.id).label("count"))
        .group_by(Document.status)
    )
    ocr_breakdown = {r.status: r.count for r in ocr_result.all()}

    # Application status breakdown
    app_status_result = await db.execute(
        select(SchemeApplication.status, func.count(SchemeApplication.id).label("count"))
        .group_by(SchemeApplication.status)
    )
    app_status_breakdown = {r.status: r.count for r in app_status_result.all()}

    return AnalyticsResponse(
        total_users=total_users,
        total_applications=total_apps,
        total_documents=total_docs,
        total_chat_sessions=total_chats,
        top_recommended_schemes=top_schemes,
        users_by_category=users_by_category,
        ocr_status_breakdown=ocr_breakdown,
        application_status_breakdown=app_status_breakdown,
    )


@router.post("/reindex-rag", summary="Re-build FAISS RAG index from current schemes")
async def reindex_rag(admin: User = Depends(get_current_admin)):
    """
    Trigger a rebuild of the RAG FAISS index.
    Call this after adding/modifying schemes in schemes.json.
    """
    global _schemes_cache
    _schemes_cache = None  # Clear scheme cache

    from app.rag.engine import _rag_instance
    import app.rag.engine as rag_module

    schemes = get_schemes()
    rag_instance = rag_module._rag_instance
    if rag_instance is None:
        rag_instance = rag_module.GovGuideRAG(model_name=settings.EMBEDDINGS_MODEL)
        rag_module._rag_instance = rag_instance

    rag_instance.build_index(schemes)
    rag_instance.save_index(settings.FAISS_INDEX_PATH)

    return {"message": f"RAG index rebuilt with {len(schemes)} schemes"}


@router.get("/schemes", summary="Admin: list all schemes with metadata")
async def admin_list_schemes(admin: User = Depends(get_current_admin)):
    """Return all schemes for admin management."""
    schemes = get_schemes()
    return {"total": len(schemes), "schemes": schemes}


@router.get("/users", summary="Admin: list all users")
async def admin_list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Return all registered users (admin only)."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(100)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "category": u.category,
            "state": u.state,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/create-admin", summary="Promote a user to admin")
async def create_admin(
    email: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Promote an existing user to admin role."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.add(user)
    return {"message": f"User {email} promoted to admin"}
