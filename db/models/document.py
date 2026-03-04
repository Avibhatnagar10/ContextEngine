import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    file_name = Column(String(255), nullable=True)

    file_type = Column(String(50), nullable=True)

    chroma_collection = Column(String(255), nullable=True)

    total_chunks = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationship with chunks
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete"
    )