# Backend

A FastAPI backend that handles document ingestion, vector storage, and streaming AI responses. Built as part of a RAG (Retrieval-Augmented Generation) pipeline that powers a document chat application.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI (Python) |
| Database | PostgreSQL 16 + PGVector |
| ORM | SQLAlchemy (async) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Chat Model | OpenAI `gpt-4o-mini` |
| PDF Parsing | Docling |
| Tokenization | tiktoken (`cl100k_base`) |
| Migrations | Alembic |
| Runtime | Docker (database), uv (application) |

---

## How the RAG Pipeline Works

### Document Ingestion

When a document is uploaded, the backend immediately returns a `202 Accepted` response and hands off processing to a background task. This keeps the API non-blocking and responsive while heavy work runs asynchronously.

The background task runs the document through three stages:

1. **Parsing.** PDF files are converted to plain text using Docling. Plain text uploads skip this step.
2. **Chunking.** The text is split using a sliding window strategy. A fixed-size window of 512 tokens moves through the document, advancing by 448 tokens each step and leaving a 64-token overlap with the previous chunk. This overlap ensures that sentences or ideas that fall across a boundary are captured in both adjacent chunks rather than being cut off.
3. **Embedding.** Each chunk is sent to OpenAI's `text-embedding-3-small` model, which returns a 1536-dimensional vector representing the semantic meaning of that chunk. All vectors are stored in PostgreSQL alongside the chunk text using the PGVector extension.

Once all chunks are stored, the document status is updated to `ready`.

### Retrieval and Generation

When a question comes in, the backend embeds the question using the same model used during ingestion. It then runs a cosine similarity search against the stored chunk vectors using PGVector, retrieving the 5 most semantically relevant chunks.

Those chunks are assembled into a context block and passed to `gpt-4o-mini` along with the conversation history. The model is instructed to answer strictly from the provided context and to cite its sources, preventing hallucination outside the uploaded material.

The response is streamed back to the client over SSE (Server-Sent Events) token by token. A final event delivers the source chunk references so the frontend can display citations.

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload a PDF or plain text, returns a document ID |
| `GET` | `/api/documents/{id}` | Poll processing status (`processing` or `ready`) |
| `POST` | `/api/chat/stream` | Submit a question, streams back an SSE response |

---

## Additional Docs

- [Quickstart](documentation/quickstart.md)
- [Directory Structure](documentation/filestructure.md)
- [Detailed API](documentation/api.md)