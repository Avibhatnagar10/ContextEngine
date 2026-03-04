from fastapi import Request, HTTPException
from jose import JWTError
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.crud.user_crud import get_user_by_id
from auth.jwt_handler import verify_token


async def auth_middleware(request: Request, call_next):

    print("\n====== AUTH MIDDLEWARE ======")
    print("Incoming path:", request.url.path)

    # Skip auth routes
    public_routes = [
        "/auth/login",
        "/auth/callback",
        "/docs",
        "/openapi.json"
    ]

    if any(request.url.path.startswith(route) for route in public_routes):
        print("Public route - skipping auth")
        return await call_next(request)

    token = None

    # 1️⃣ Check cookies
    token = request.cookies.get("access_token")

    print("Cookie token:", token)

    # 2️⃣ Check Authorization header if cookie not present
    if not token:

        auth_header = request.headers.get("Authorization")

        print("Authorization header:", auth_header)

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            print("Token extracted from header")

    if not token:
        print("❌ No token found")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:

        print("Verifying JWT token")

        payload = verify_token(token)

        print("Decoded payload:", payload)

        user_id = payload.get("user_id")

        if not user_id:
            print("❌ user_id missing from token")
            raise HTTPException(status_code=401, detail="Invalid token")

        db: Session = SessionLocal()

        print("Fetching user from DB:", user_id)

        user = get_user_by_id(db, user_id)

        if not user:
            print("❌ User not found in database")
            raise HTTPException(status_code=401, detail="User not found")

        print("✅ Authenticated user:", user.email)

        request.state.user = user

        db.close()

    except JWTError as e:

        print("❌ JWT verification failed:", str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    print("====== AUTH SUCCESS ======\n")

    response = await call_next(request)

    return response