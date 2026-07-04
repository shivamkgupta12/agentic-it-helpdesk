from typing import Any, TypedDict

from app.schemas.agents import AgentTraceStep, TriageResult


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    Each agent reads from and writes to this state.
    """

    user_message: str
    user_email: str
    user_id: str | None
    conversation_id: str | None
    db_session: Any

    triage: TriageResult | None
    next_agent: str | None

    clarification_question: str | None

    retrieved_context: str | None
    sources: list[dict[str, Any]]

    resolution: str | None
    final_summary: str | None

    ticket_required: bool
    sensitive_action: bool
    requires_approval: bool
    should_create_ticket: bool

    ticket_id: str | None
    ticket_number: str | None
    ticket_status: str | None

    agent_trace: list[AgentTraceStep]