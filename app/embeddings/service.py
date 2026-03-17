from openai import AsyncOpenAI

from app.config import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await _client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def embed_query(text: str) -> list[float]:
    results = await embed_texts([text])
    return results[0]
