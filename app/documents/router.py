import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.documents.models import Document
from app.documents.schemas import DocumentStatusResponse, DocumentUploadResponse
from app.documents.service import compute_hash, parse_pdf, process_document

router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/upload', response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    file: Optional[UploadFile] = File(default=None),
    text: Optional[str] = Form(default=None),
    filename: Optional[str] = Form(default=None),
):
    if file is None and text is None:
        raise HTTPException(status_code=422, detail="Provide either 'file' or 'text'")

    if file is not None:
        file_bytes = await file.read()
        doc_filename = file.filename or 'upload.pdf'
        content_hash = compute_hash(file_bytes)
        raw_text = parse_pdf(file_bytes, doc_filename)
    else:
        raw_text = text
        doc_filename = filename or 'paste.txt'
        content_hash = compute_hash(text.encode())

    doc = Document(filename=doc_filename, content_hash=content_hash, status='processing')
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    background_tasks.add_task(process_document, doc.id, raw_text)

    return DocumentUploadResponse(document_id=doc.id, filename=doc.filename, status=doc.status)


@router.get('/{document_id}', response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    doc = await db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail='Document not found')
    return DocumentStatusResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        created_at=doc.created_at,
    )
