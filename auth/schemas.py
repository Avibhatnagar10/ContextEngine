from pydantic import BaseModel
from typing import Optional


# -----------------------------
# Token Response
# -----------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# Refresh Request (Optional)
# -----------------------------
class RefreshRequest(BaseModel):
    refresh_token: str


# -----------------------------
# User Schema
# -----------------------------
class UserSchema(BaseModel):
    id: str
    email: str
    role: str
    name: Optional[str] = None

    class Config:
        from_attributes = True