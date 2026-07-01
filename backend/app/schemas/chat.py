from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    user_email: str = "employee@example.com"


class SourceCitation(BaseModel):
    title: str
    source: str
    chunk_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    ticket_number: str | None = None
    requires_approval: bool = False
    approval_id: str | None = None
    sources: list[SourceCitation] = []