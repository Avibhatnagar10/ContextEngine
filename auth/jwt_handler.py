from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException

from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


def create_access_token(data: dict):
    print("\n=== CREATE ACCESS TOKEN ===")

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    print("Payload:", to_encode)

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    print("Access token generated")

    return token


def create_refresh_token(data: dict):
    print("\n=== CREATE REFRESH TOKEN ===")

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    print("Payload:", to_encode)

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    print("Refresh token generated")

    return token


def verify_token(token: str):
    print("\n=== VERIFY TOKEN ===")

    if not token:
        print("❌ No token provided")
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print("Decoded payload:", payload)

        token_type = payload.get("type")

        if not token_type:
            print("❌ Token type missing")
            raise HTTPException(status_code=401, detail="Invalid token")

        print("Token type:", token_type)

        return payload

    except JWTError as e:
        print("❌ JWT verification failed:", str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")