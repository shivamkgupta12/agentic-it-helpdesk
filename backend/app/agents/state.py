from typing import Any, TypedDict

from app.schemas.agents import AgentTraceStep, TriageResult


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    Each agent reads from and writes to this state.
    """

    user_message: str
    user_email: str
    conversation_id: str | None

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

    agent_trace: list[AgentTraceStep]