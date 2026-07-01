from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        conversation_id=request.conversation_id or "phase-1-placeholder",
        response=(
            "Phase 1 backend is running. "
            "LangGraph, Azure OpenAI, RAG, tickets, and approvals will be added in later phases."
        ),
        ticket_number=None,
        requires_approval=False,
        sources=[],
    )