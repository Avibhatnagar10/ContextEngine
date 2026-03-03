from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from uuid import uuid4
from datetime import datetime
from .config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from .jwt_handler import create_access_token
from .token_store import generate_refresh_token, validate_refresh_token
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

# Temporary store (replace with DB later)
fake_users = {}

FRONTEND_URL = "http://localhost:3000"
ACCESS_COOKIE_NAME = "access_token" 
REFRESH_COOKIE_NAME = "refresh_token"


# 🔐 STEP 1 — Redirect to Google
@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# 🔐 STEP 2 — Callback from Google
@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    email = user_info["email"]

    if email not in fake_users:
        fake_users[email] = {
            "id": str(uuid4()),
            "email": email,
            "role": "admin",
            "created_at": datetime.utcnow(),
        }

    user = fake_users[email]

    access_token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
    })

    refresh_token = generate_refresh_token(user["id"])

    # 🔥 Redirect to frontend instead of returning JSON
    response = RedirectResponse(
        url=f"{FRONTEND_URL}/dashboard"
    )

    response.set_cookie( 
        key=ACCESS_COOKIE_NAME, 
        value=access_token,
        httponly=True,
        secure=True, # MUST be True in production (HTTPS) 
        samesite="lax", 
        max_age=900, # 15 min
        )
    response.set_cookie( 
        key=REFRESH_COOKIE_NAME, 
        value=refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="lax", 
        max_age=7 * 24 * 60 * 60, # 7 days 
        )

    return response


# 🔄 Refresh Access Token (Rotation)
@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(request: Request):
    refresh_cookie = request.cookies.get("refresh_token")

    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    user_id = validate_refresh_token(refresh_cookie)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token({
        "user_id": user_id,
        "role": "user"
    })

    new_refresh = generate_refresh_token(user_id)

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return response


# 🚪 Logout
@router.post("/logout")
def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("refresh_token")
    return response