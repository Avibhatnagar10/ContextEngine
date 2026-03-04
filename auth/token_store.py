import hashlib
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from db.crud.session_crud import (
    create_session,
    get_valid_session,
    delete_session
)


REFRESH_TOKEN_EXPIRE_DAYS = 7


def generate_refresh_token(user_id: str, db: Session, request=None):

    print("\n=== GENERATE REFRESH TOKEN ===")

    raw_token = str(uuid.uuid4())

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    print("Token generated for user:", user_id)

    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    create_session(
        db=db,
        user_id=user_id,
        refresh_token=token_hash,
        user_agent=request.headers.get("user-agent") if request else None,
        ip_address=request.client.host if request else None,
        expires_at=expires_at
    )

    print("Refresh token stored in DB")

    return raw_token


def validate_refresh_token(raw_token: str, db: Session):

    print("\n=== VALIDATE REFRESH TOKEN ===")

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    session = get_valid_session(db, token_hash)

    if not session:
        print("❌ Invalid refresh token")
        return None

    print("Refresh token valid for user:", session.user_id)

    # rotation → invalidate old token
    delete_session(db, token_hash)

    print("Old refresh token revoked")

    return session.user_id