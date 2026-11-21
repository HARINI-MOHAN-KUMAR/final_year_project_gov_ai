"""Authentication API router – register and login endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, ProfileRead

router = APIRouter()


@router.get("/me", response_model=ProfileRead, summary="Get current logged in user")
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


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
        category=payload.category or "General",
        state=payload.state or "All India",
        annual_income=payload.annual_income or 0.0,
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
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user and return JWT access token (supports JSON and form-urlencoded)."""
    email = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = body.get("email") or body.get("username")
                password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email/username and password are required",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again.",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated. Please contact support.")

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
