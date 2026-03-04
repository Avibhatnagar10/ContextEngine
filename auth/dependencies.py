from fastapi import Request, HTTPException, Depends
from jose import JWTError
from sqlalchemy.orm import Session

from db.database import get_db
from db.crud.user_crud import get_user_by_id
from auth.jwt_handler import verify_token


def get_current_user(request: Request, db: Session = Depends(get_db)):

    print("\n========== AUTH DEBUG ==========")

    # Check cookie token first
    token = request.cookies.get("access_token")

    print("Cookie token:", token)

    # If cookie not present, check Authorization header
    if not token:

        auth_header = request.headers.get("Authorization")
        print("Authorization header:", auth_header)

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            print("Token extracted from header")

    if not token:
        print("❌ No token found in cookies or headers")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        print("Verifying token...")

        payload = verify_token(token)

        print("Token payload:", payload)

        user_id = payload.get("user_id")

        if not user_id:
            print("❌ user_id missing in token")
            raise HTTPException(status_code=401, detail="Invalid token")

        print("Fetching user from DB:", user_id)

        user = get_user_by_id(db, user_id)

        if not user:
            print("❌ User not found in database")
            raise HTTPException(status_code=401, detail="User not found")

        print("✅ User authenticated:", user.email)
        print("Role:", getattr(user, "role", "user"))

        print("========== AUTH SUCCESS ==========\n")

        return user

    except JWTError as e:

        print("❌ JWT ERROR:", str(e))
        print("========== AUTH FAILED ==========\n")

        raise HTTPException(status_code=401, detail="Invalid or expired token")