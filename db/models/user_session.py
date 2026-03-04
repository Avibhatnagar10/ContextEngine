import uuid
from sqlalchemy import Column, Text, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE")
    )

    refresh_token = Column(Text, nullable=False)

    user_agent = Column(Text)

    ip_address = Column(String(100))

    expires_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())