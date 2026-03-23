# Directory Structure

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
