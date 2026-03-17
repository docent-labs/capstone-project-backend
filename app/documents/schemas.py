import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    created_at: datetime
