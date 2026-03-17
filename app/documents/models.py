import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default='processing')
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    chunks: Mapped[list['Chunk']] = relationship('Chunk', back_populates='document', cascade='all, delete-orphan')


class Chunk(Base):
    __tablename__ = 'chunks'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    document: Mapped[Document] = relationship('Document', back_populates='chunks')
