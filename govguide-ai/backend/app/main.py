"""
GovGuide AI – Main FastAPI Application Entry Point
Initializes the app, middleware, routers, and startup events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, profile, schemes, ocr, chat, applications, admin
from app.scheduler.tasks import start_scheduler, stop_scheduler

# Configure structured logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("🚀 Starting GovGuide AI backend...")

    # Create database tables if they don't exist
    await create_tables()
    logger.info("✅ Database tables ready")

    # Start background scheduler (reminders, expiry checks)
    start_scheduler()
    logger.info("✅ Scheduler started")

    yield  # Application is running

    logger.info("🛑 Shutting down GovGuide AI backend...")
    stop_scheduler()


def create_app() -> FastAPI:
    """Application factory – creates and configures the FastAPI app."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Intelligent Decision Support System for Government Scheme "
            "Recommendation, Eligibility Verification, and Application Assistance. "
            "\n\n⚠️ **Disclaimer**: This is an advisory platform only and is NOT an "
            "official government service. Always verify information on official portals."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(auth.router,         prefix=f"{api_prefix}/auth",         tags=["Authentication"])
    app.include_router(profile.router,      prefix=f"{api_prefix}/profile",      tags=["Profile"])
    app.include_router(schemes.router,      prefix=f"{api_prefix}/schemes",      tags=["Schemes"])
    app.include_router(ocr.router,          prefix=f"{api_prefix}/ocr",          tags=["OCR"])
    app.include_router(chat.router,         prefix=f"{api_prefix}/chat",         tags=["Chatbot"])
    app.include_router(applications.router, prefix=f"{api_prefix}/applications", tags=["Applications"])
    app.include_router(admin.router,        prefix=f"{api_prefix}/admin",        tags=["Admin"])

    # ── Health Check ────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0",
            "disclaimer": "Advisory only – not an official government service.",
        }

    # ── Serve Built Frontend SPA (Fast Mode) ─────────────────────────────────
    from fastapi.responses import FileResponse
    dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    if os.path.exists(dist_path):
        assets_path = os.path.join(dist_path, "assets")
        if os.path.exists(assets_path):
            app.mount("/assets", StaticFiles(directory=assets_path), name="frontend_assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            # Avoid masking API or docs
            if full_path.startswith("api") or full_path.startswith("health"):
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Not Found")
            file_path = os.path.join(dist_path, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(dist_path, "index.html"))

    return app


app = create_app()
