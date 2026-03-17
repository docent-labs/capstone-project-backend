from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    document_id: str
    question: str
    chat_history: list[Message] = []
