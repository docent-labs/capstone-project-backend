# Quickstart

## Running Locally

**Start the database:**

```bash
docker compose up -d
```

**Run migrations:**

```bash
uv run alembic upgrade head
```

**Run the backend:**

```bash
uv run uvicorn app.main:app --reload
```

---

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | — | PostgreSQL connection string (required) |
| `OPENAI_API_KEY` | — | OpenAI API key (required) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHAT_MODEL` | `gpt-4o-mini` | OpenAI chat model |
| `TOP_K_CHUNKS` | `5` | Number of chunks retrieved per question |
| `CHUNK_SIZE` | `512` | Tokens per chunk (tiktoken `cl100k_base`) |
| `CHUNK_OVERLAP` | `64` | Overlap tokens between adjacent chunks |

---

## Infrastructure

- **Database:** PostgreSQL 16 with PGVector extension, run via Docker (`docker-compose.yml`)
- **Backend:** Run locally with `uv`; intended for cloud deployment (not containerized locally)
- **Embeddings:** `text-embedding-3-small` via OpenAI API (1536-dimensional vectors)
- **Chat:** `gpt-4o-mini` streaming via OpenAI API
- **CORS:** All origins allowed (`*`) — suitable for local dev; restrict for production
