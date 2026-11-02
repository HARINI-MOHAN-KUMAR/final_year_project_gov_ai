"""Authentication API router – register and login endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201,
             summary="Register a new user")
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Create a new user account. Returns JWT access token."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
    )
    db.add(user)
    await db.flush()  # Get user.id before commit
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=Token, summary="Login with email + password")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return JWT access token."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/demo-login", response_model=Token, summary="Demo login (creates/returns demo user)")
async def demo_login(db: AsyncSession = Depends(get_db)):
    """
    Demo login endpoint – creates a demo user if it doesn't exist.
    Credentials: demo@govguide.ai / demo1234
    """
    demo_email = "demo@govguide.ai"
    result = await db.execute(select(User).where(User.email == demo_email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=demo_email,
            hashed_password=hash_password("demo1234"),
            full_name="Demo User",
            age=28,
            gender="male",
            annual_income=180000,
            education="graduate",
            occupation="farmer",
            category="OBC",
            state="Tamil Nadu",
            disability=False,
            marital_status="married",
            residence="rural",
            land_holding=True,
            bank_account=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )
