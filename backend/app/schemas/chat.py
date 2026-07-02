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


class SimpleChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    user_email: str = "employee@example.com"


class SimpleChatResponse(BaseModel):
    conversation_id: str
    response: str
    provider: str = "azure_openai"
    model_deployment: str


class AzureOpenAIHealthResponse(BaseModel):
    provider: str
    endpoint_configured: bool
    api_key_configured: bool
    api_version: str
    chat_deployment: str
    embedding_deployment_configured: bool