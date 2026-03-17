import hashlib
import uuid
from pathlib import Path

import tiktoken
from docling.document_converter import DocumentConverter

from app.config import settings
from app.db import AsyncSessionLocal
from app.documents.models import Chunk, Document
from app.embeddings.service import embed_texts


class Chunker:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP):
        self.enc = tiktoken.get_encoding('cl100k_base')
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[tuple[str, int]]:
        tokens = self.enc.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.enc.decode(chunk_tokens)
            chunks.append((chunk_text, len(chunk_tokens)))
            if end == len(tokens):
                break
            start += self.chunk_size - self.overlap
        return chunks


async def process_document(document_id: uuid.UUID, text: str) -> None:
    chunker = Chunker()
    raw_chunks = chunker.split(text)
    chunk_texts = [c[0] for c in raw_chunks]
    embeddings = await embed_texts(chunk_texts)

    async with AsyncSessionLocal() as db:
        chunks = [
            Chunk(
                document_id=document_id,
                content=chunk_text,
                embedding=emb,
                chunk_index=i,
                token_count=token_count,
            )
            for i, ((chunk_text, token_count), emb) in enumerate(zip(raw_chunks, embeddings))
        ]
        db.add_all(chunks)
        doc = await db.get(Document, document_id)
        doc.status = 'ready'
        await db.commit()


def parse_pdf(file_bytes: bytes, filename: str) -> str:
    tmp_path = Path(f'/tmp/{filename}')
    tmp_path.write_bytes(file_bytes)
    converter = DocumentConverter()
    result = converter.convert(str(tmp_path))
    tmp_path.unlink(missing_ok=True)
    return result.document.export_to_markdown()


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
