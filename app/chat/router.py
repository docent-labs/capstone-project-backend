import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.schemas import ChatRequest
from app.chat.service import stream_chat
from app.db import get_session
from app.documents.models import Document

router = APIRouter(prefix='/chat', tags=['chat'])


@router.post('/stream')
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
):
    document_id = uuid.UUID(request.document_id)
    doc = await db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail='Document not found')
    if doc.status != 'ready':
        raise HTTPException(status_code=409, detail='Document is still processing')

    async def event_generator():
        async for event in stream_chat(db, document_id, request.question, request.chat_history):
            yield f'data: {json.dumps(event)}\n\n'

    return StreamingResponse(event_generator(), media_type='text/event-stream')
