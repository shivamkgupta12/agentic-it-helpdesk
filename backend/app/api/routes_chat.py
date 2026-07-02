import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.database_models import Conversation, Message, MessageRole, User, UserRole
from app.schemas.chat import (
    AzureOpenAIHealthResponse,
    ChatRequest,
    ChatResponse,
    SimpleChatRequest,
    SimpleChatResponse,
)
from app.services.azure_openai_client import (
    AzureOpenAIConfigError,
    AzureOpenAIService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_or_create_demo_user(db: Session, email: str) -> User:
    """
    MVP demo-auth helper.

    Later, replace this with JWT/Supabase Auth.
    """

    user = db.query(User).filter(User.email == email).first()

    if user:
        return user

    role = UserRole.admin if email == get_settings().demo_admin_email else UserRole.employee

    user = User(
        email=email,
        name=email.split("@")[0],
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_conversation(
    db: Session,
    user: User,
    conversation_id: str | None,
    first_message: str,
) -> Conversation:
    if conversation_id:
        existing = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
            )
            .first()
        )

        if existing:
            return existing

    title = first_message[:60]

    conversation = Conversation(
        user_id=user.id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def save_message(
    db: Session,
    conversation_id: str,
    role: MessageRole,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/azure-health", response_model=AzureOpenAIHealthResponse)
def azure_openai_health() -> AzureOpenAIHealthResponse:
    """
    Checks whether Azure OpenAI config values are present.

    This endpoint does not call Azure.
    """

    try:
        service = AzureOpenAIService()
        return AzureOpenAIHealthResponse(**service.health_check())

    except AzureOpenAIConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/simple", response_model=SimpleChatResponse)
def simple_chat(
    request: SimpleChatRequest,
    db: Session = Depends(get_db),
) -> SimpleChatResponse:
    """
    Phase 2 endpoint.

    Sends the user message directly to Azure OpenAI.
    No LangGraph yet.
    No RAG yet.
    No ServiceNow yet.
    """

    user = get_or_create_demo_user(db=db, email=request.user_email)

    conversation = get_or_create_conversation(
        db=db,
        user=user,
        conversation_id=request.conversation_id,
        first_message=request.message,
    )

    save_message(
        db=db,
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=request.message,
    )

    try:
        service = AzureOpenAIService()

        response_text = service.generate_chat_response(
            user_message=request.message,
        )

    except AzureOpenAIConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except RuntimeError as exc:
        logger.exception("Simple chat request failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    save_message(
        db=db,
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=response_text,
    )

    return SimpleChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        provider="azure_openai",
        model_deployment=get_settings().azure_openai_chat_deployment,
    )


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Placeholder for the final LangGraph-powered chat endpoint.

    This will be replaced in Phase 3.
    """

    return ChatResponse(
        conversation_id=request.conversation_id or "phase-2-placeholder",
        response=(
            "Phase 2 is active. Use POST /api/chat/simple to test Azure OpenAI. "
            "The full LangGraph multi-agent workflow will be added in Phase 3."
        ),
        ticket_number=None,
        requires_approval=False,
        sources=[],
    )