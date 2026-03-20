# API Reference

All routes are prefixed with `/api`. The server runs at `http://localhost:8000`.

---

### POST `/api/documents/upload`

Accepts a PDF file or plain text. Immediately returns a document ID and kicks off background processing (chunking + embedding). Poll `GET /api/documents/{id}` until `status` is `"ready"` before calling the chat endpoint.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `file` | `UploadFile` | one of `file` or `text` | PDF file to parse |
| `text` | `string` (form field) | one of `file` or `text` | Plain text to ingest |
| `filename` | `string` (form field) | no | Display name when using `text`; defaults to `"paste.txt"` |

Exactly one of `file` or `text` must be provided. Sending neither returns `422`.

**Response:** `202 Accepted`

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "my-doc.pdf",
  "status": "processing"
}
```

---

### GET `/api/documents/{document_id}`

Returns the current processing status of a document.

**Path param:** `document_id` — UUID string

**Response:** `200 OK`

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "my-doc.pdf",
  "status": "ready",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**`status` values:**

| Value | Meaning |
| --- | --- |
| `"processing"` | Chunking and embedding in progress (background task) |
| `"ready"` | Document is fully embedded; safe to call chat endpoint |

Returns `404` if the document ID is not found.

---

### POST `/api/chat/stream`

Streams an answer to a question grounded in the uploaded document. Returns a **Server-Sent Events (SSE)** stream (`text/event-stream`). The document must be `"ready"` before calling this endpoint.

**Request:** `application/json`

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What are the key findings?",
  "chat_history": [
    { "role": "user", "content": "Previous question" },
    { "role": "assistant", "content": "Previous answer" }
  ]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `document_id` | `string` (UUID) | yes | Must match an existing document with `status: "ready"` |
| `question` | `string` | yes | The user's current question |
| `chat_history` | `Message[]` | no | Prior turns for multi-turn context; defaults to `[]` |

`Message` shape: `{ "role": "user" | "assistant", "content": string }`

**Response:** `text/event-stream`

Each SSE event is a `data:` line containing a JSON object. Three event types are emitted in order:

**1. Token events** (one per streamed token, many per response):
```
data: {"type": "token", "content": "The "}
data: {"type": "token", "content": "key "}
```

**2. Sources event** (one, after all tokens):
```
data: {"type": "sources", "chunks": [
  {"content": "...chunk text...", "chunk_index": 0},
  {"content": "...chunk text...", "chunk_index": 3}
]}
```

**3. Done event** (one, signals end of stream):
```
data: {"type": "done"}
```

The frontend should accumulate `token` content into the displayed answer, then display `sources` chunks as citations, and stop reading on `done`.

**Error responses (before streaming begins):**

| Status | Detail | Cause |
| --- | --- | --- |
| `404` | `"Document not found"` | Unknown `document_id` |
| `409` | `"Document is still processing"` | Document `status` is not `"ready"` |
