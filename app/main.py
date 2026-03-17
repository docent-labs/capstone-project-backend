from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.chat.router import router as chat_router
from app.documents.router import router as documents_router

app = FastAPI(title="Capstone RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
