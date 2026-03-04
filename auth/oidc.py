from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

from db.database import get_db
from db.crud.user_crud import get_user_by_email, create_user
from db.crud.session_crud import create_session, get_valid_session, delete_session

from .config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ADMIN_EMAIL
from .jwt_handler import create_access_token, create_refresh_token
from .schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


# -----------------------------
# STEP 1 — Redirect to Google
# -----------------------------
@router.get("/login")
async def login(request: Request):

    print("\n=== GOOGLE LOGIN START ===")

    redirect_uri = request.url_for("auth_callback")

    print("Redirect URI:", redirect_uri)

    return await oauth.google.authorize_redirect(request, redirect_uri)


# -----------------------------
# STEP 2 — OAuth Callback
# -----------------------------
@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):

    print("\n=== GOOGLE CALLBACK ===")

    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    email = user_info["email"]
    name = user_info.get("name")

    print("User email:", email)

    # -----------------------------
    # Get or create user
    # -----------------------------
    user = get_user_by_email(db, email)

    if not user:

        role = "admin" if email == ADMIN_EMAIL else "user"

        print("Creating new user with role:", role)

        user = create_user(
            db=db,
            name=name,
            email=email,
            password_hash="GOOGLE_AUTH",
            role=role
        )

    print("User ID:", user.id)

    # -----------------------------
    # Create tokens
    # -----------------------------
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    print("Access + refresh tokens created")

    # -----------------------------
    # Store refresh token in DB
    # -----------------------------
    expires_at = datetime.utcnow() + timedelta(days=7)

    create_session(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=expires_at
    )

    print("Session stored in DB")

    # -----------------------------
    # Redirect to dashboard
    # -----------------------------
    response = RedirectResponse(
        url=f"{FRONTEND_URL}/dashboard"
    )

    # ACCESS TOKEN COOKIE
    response.set_cookie(
    key=ACCESS_COOKIE_NAME,
    value=access_token,
    httponly=True,
    secure=True,
    samesite="none",
    # domain="quiana-sulphuric-overenthusiastically.ngrok-free.dev",
    max_age=15 * 60,
    path="/"
)

    # REFRESH TOKEN COOKIE
    response.set_cookie(
    key=REFRESH_COOKIE_NAME,
    value=refresh_token,
    httponly=True,
    secure=True,
    samesite="none",
    # domain="quiana-sulphuric-overenthusiastically.ngrok-free.dev",
    max_age=7 * 24 * 60 * 60,
    path="/"
)

    print("Cookies set successfully")
    print("=== LOGIN COMPLETE ===\n")

    return response


# -----------------------------
# REFRESH TOKEN
# -----------------------------
@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(request: Request, db: Session = Depends(get_db)):

    print("\n=== REFRESH TOKEN ===")

    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)

    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    session = get_valid_session(db, refresh_cookie)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    payload = {
        "user_id": str(session.user_id),
        "role": session.user.role
    }

    access_token = create_access_token(payload)
    new_refresh = create_refresh_token(payload)

    print("Tokens rotated")

    delete_session(db, refresh_cookie)

    create_session(
        db=db,
        user_id=session.user_id,
        refresh_token=new_refresh,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )

    response.set_cookie(
    key=REFRESH_COOKIE_NAME,
    value=new_refresh,
    httponly=True,
    secure=True,
    samesite="none",
    # domain="quiana-sulphuric-overenthusiastically.ngrok-free.dev",
    max_age=7 * 24 * 60 * 60,
    path="/"
)

    return response


# -----------------------------
# LOGOUT
# -----------------------------
@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):

    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)

    if refresh_cookie:
        delete_session(db, refresh_cookie)

    response = JSONResponse({"message": "Logged out"})

    response.delete_cookie(
        ACCESS_COOKIE_NAME,
        path="/",
        # domain="quiana-sulphuric-overenthusiastically.ngrok-free.dev",
        secure=True,
        samesite="none"
    )

    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/",
        # domain="quiana-sulphuric-overenthusiastically.ngrok-free.dev",
        secure=True,
        samesite="none"
    )

    return response