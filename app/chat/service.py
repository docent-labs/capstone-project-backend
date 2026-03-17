import uuid
from typing import AsyncIterator

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.schemas import Message
from app.config import settings
from app.documents.models import Chunk
from app.embeddings.service import embed_query

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the provided context. "
    "If the context doesn't contain the answer, say so. Always cite specific parts of the context."
)


async def retrieve_chunks(
    db: AsyncSession,
    document_id: uuid.UUID,
    question_embedding: list[float],
) -> list[Chunk]:
    result = await db.execute(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.embedding.cosine_distance(question_embedding))
        .limit(settings.TOP_K_CHUNKS)
    )
    return list(result.scalars().all())


async def stream_chat(
    db: AsyncSession,
    document_id: uuid.UUID,
    question: str,
    chat_history: list[Message],
) -> AsyncIterator[dict]:
    question_embedding = await embed_query(question)
    chunks = await retrieve_chunks(db, document_id, question_embedding)

    context = '\n\n'.join(
        f'[{i}] {c.content}' for i, c in enumerate(chunks)
    )

    messages = [
        {'role': 'system', 'content': f'{SYSTEM_PROMPT}\n\nContext:\n{context}'},
        *[{'role': m.role, 'content': m.content} for m in chat_history],
        {'role': 'user', 'content': question},
    ]

    stream = await _client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {'type': 'token', 'content': delta.content}

    yield {'type': 'sources', 'chunks': [{'content': c.content, 'chunk_index': c.chunk_index} for c in chunks]}
    yield {'type': 'done'}
