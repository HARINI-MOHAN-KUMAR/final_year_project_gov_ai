"""
API integration tests for GovGuide AI backend.
Tests auth, profile, schemes, and application endpoints.
"""

import sys
from pathlib import Path
import pytest
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def noop_lifespan(a):
    yield

app.router.lifespan_context = noop_lifespan


# ── Test Database Setup ──────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_govguide.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create all tables in the test database."""
    from app.models import user, scheme_app, document, chat  # noqa
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    try:
        Path("./test_govguide.db").unlink(missing_ok=True)
    except Exception:
        pass


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client):
    """Register a test user and return auth headers."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    if resp.status_code == 400:
        # Already registered, login instead
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123",
        })
    assert resp.status_code in (200, 201)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Health Check Tests ────────────────────────────────────────────────────────

class TestHealth:
    async def test_health_endpoint(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "disclaimer" in data


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client, auth_headers):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Duplicate User",
        })
        assert resp.status_code == 400

    async def test_login_success(self, client, auth_headers):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_demo_login(self, client):
        resp = await client.post("/api/v1/auth/demo-login")
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_unauthorized_access(self, client):
        resp = await client.get("/api/v1/profile/")
        assert resp.status_code in (401, 403)


# ── Profile Tests ─────────────────────────────────────────────────────────────

class TestProfile:
    async def test_get_profile(self, client, auth_headers):
        resp = await client.get("/api/v1/profile/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"

    async def test_update_profile(self, client, auth_headers):
        resp = await client.put("/api/v1/profile/", headers=auth_headers, json={
            "age": 28,
            "gender": "female",
            "annual_income": 150000,
            "category": "SC",
            "state": "Tamil Nadu",
            "occupation": "farmer",
            "education": "graduate",
            "residence": "rural",
            "land_holding": True,
            "bank_account": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["age"] == 28
        assert data["category"] == "SC"

    async def test_invalid_category(self, client, auth_headers):
        resp = await client.put("/api/v1/profile/", headers=auth_headers, json={
            "category": "INVALID_CATEGORY",
        })
        assert resp.status_code == 422


# ── Schemes Tests ─────────────────────────────────────────────────────────────

class TestSchemes:
    async def test_list_schemes(self, client):
        resp = await client.get("/api/v1/schemes/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 40

    async def test_get_scheme_by_id(self, client):
        resp = await client.get("/api/v1/schemes/PM_KISAN")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "PM_KISAN"
        assert "eligibility_rules" in data

    async def test_scheme_not_found(self, client):
        resp = await client.get("/api/v1/schemes/NONEXISTENT_SCHEME")
        assert resp.status_code == 404

    async def test_filter_by_category(self, client):
        resp = await client.get("/api/v1/schemes/?category=Education")
        assert resp.status_code == 200
        data = resp.json()
        assert all(s["category"] == "Education" for s in data)

    async def test_categories_endpoint(self, client):
        resp = await client.get("/api/v1/schemes/categories")
        assert resp.status_code == 200
        assert "categories" in resp.json()

    async def test_recommendations(self, client, auth_headers):
        # First set up a profile
        await client.put("/api/v1/profile/", headers=auth_headers, json={
            "age": 30,
            "gender": "male",
            "annual_income": 100000,
            "category": "SC",
            "occupation": "farmer",
            "state": "Tamil Nadu",
            "residence": "rural",
            "land_holding": True,
            "bank_account": True,
        })
        resp = await client.post(
            "/api/v1/schemes/recommend",
            headers=auth_headers,
            json={"top_n": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendations" in data
        assert "profile_completeness" in data
        assert "disclaimer" in data
        assert len(data["recommendations"]) <= 5


# ── Applications Tests ────────────────────────────────────────────────────────

class TestApplications:
    async def test_create_application(self, client, auth_headers):
        resp = await client.post("/api/v1/applications/", headers=auth_headers, json={
            "scheme_id": "PM_KISAN",
            "scheme_name": "PM-KISAN",
            "status": "Planned",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scheme_id"] == "PM_KISAN"
        assert data["status"] == "Planned"

    async def test_list_applications(self, client, auth_headers):
        resp = await client.get("/api/v1/applications/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_update_application_status(self, client, auth_headers):
        # Create first
        create_resp = await client.post("/api/v1/applications/", headers=auth_headers, json={
            "scheme_id": "MUDRA_SHISHU",
            "scheme_name": "MUDRA Loan Shishu",
            "status": "Planned",
        })
        app_id = create_resp.json()["id"]

        # Update status
        resp = await client.put(
            f"/api/v1/applications/{app_id}",
            headers=auth_headers,
            json={"status": "In Progress"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "In Progress"

    async def test_invalid_status(self, client, auth_headers):
        create_resp = await client.post("/api/v1/applications/", headers=auth_headers, json={
            "scheme_id": "APY",
            "scheme_name": "Atal Pension Yojana",
            "status": "Planned",
        })
        app_id = create_resp.json()["id"]

        resp = await client.put(
            f"/api/v1/applications/{app_id}",
            headers=auth_headers,
            json={"status": "INVALID_STATUS"},
        )
        assert resp.status_code == 400
