import hashlib
from datetime import datetime, timedelta
import uuid

refresh_store = {}

def generate_refresh_token(user_id):
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    refresh_store[token_hash] = {
        "user_id": user_id,
        "expires": datetime.utcnow() + timedelta(days=7),
        "revoked": False
    }

    return raw_token

def validate_refresh_token(raw_token):
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token_data = refresh_store.get(token_hash)

    if not token_data:
        return None

    if token_data["revoked"]:
        return None

    if token_data["expires"] < datetime.utcnow():
        return None

    # rotation
    token_data["revoked"] = True

    return token_data["user_id"]