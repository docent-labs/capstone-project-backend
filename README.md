# Backend Architecture
## Context

Greenfield FastAPI backend for a RAG (Retrieval-Augmented Generation) capstone project.
Users upload a PDF or paste text, ask questions in a chat UI, and receive cited, token-streamed answers.
The backend defines an API contract synced with a Next.js + React 18 frontend.
No auth, no multi-document sessions for MVP.

---

## Directory Structure

```
capstone-project-backend/
├── app/
│   ├── documents/
│   │   ├── router.py       # POST /api/documents/upload, GET /api/documents/{id}
│   │   ├── service.py      # PDF parsing (Docling), chunking (tiktoken), embedding storage
│   │   ├── models.py       # SQLAlchemy: Document, Chunk
│   │   └── schemas.py      # Pydantic: DocumentUploadResponse, DocumentStatusResponse
│   ├── chat/
│   │   ├── router.py       # POST /api/chat/stream (SSE)
│   │   ├── service.py      # Vector retrieval, prompt construction, OpenAI streaming
│   │   └── schemas.py      # Pydantic: ChatRequest, Message
│   ├── embeddings/
│   │   └── service.py      # OpenAI embeddings client (text-embedding-3-small)
│   ├── db.py               # SQLAlchemy async engine + get_session dependency
│   ├── config.py           # pydantic-settings BaseSettings
│   └── main.py             # FastAPI app factory, router mounting, CORS middleware
├── alembic/
│   └── versions/           # Migration files
├── tests/
├── alembic.ini
├── pyproject.toml
├── docker-compose.yml      # DB only (pgvector/pgvector:pg16)
├── Dockerfile
└── .env.example
```

---

## Running Locally

**Start the database:**

```bash
docker compose up -d
```

**Run the backend:**

```bash
uv run uvicorn app.main:app --reload
```

**Run migrations:**

```bash
uv run alembic upgrade head
```

---

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/documents/upload` | Upload PDF or plain text |
| GET | `/api/documents/{id}` | Get document processing status |
| POST | `/api/chat/stream` | SSE chat stream with cited answers |

## Infrastructure

- **Database:** PostgreSQL 16 with PGVector extension, run via Docker (`docker-compose.yml`)
- **Backend:** Run locally with `uv`; intended for cloud deployment (not containerized locally)
- **Embeddings:** `text-embedding-3-small` via OpenAI API
- **Chat:** `gpt-4o-mini` streaming via OpenAI API