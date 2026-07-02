from app.agents.state import AgentState
from app.agents.utils import add_trace_step


def supervisor_agent(state: AgentState) -> dict:
    """
    Decides which agent should act next.

    Phase 3 routing:
    - If clarification is needed: go to Clarification Agent.
    - Otherwise: go to Resolution Agent.

    Later phases:
    - Sensitive action: Human Approval Agent.
    - RAG required: Knowledge Retrieval Agent.
    - Ticket required: Ticket Agent.
    """

    triage = state.get("triage")

    if triage and triage.needs_clarification:
        next_agent = "clarification"
        decision = "Selected Clarification Agent because the issue is vague."

    else:
        next_agent = "resolution"
        decision = "Selected Resolution Agent because the issue can be handled directly."

    trace_update = add_trace_step(
        state=state,
        agent_name="Supervisor Agent",
        input_summary="Reviewed triage result.",
        output_summary=decision,
        metadata={
            "next_agent": next_agent,
        },
    )

    return {
        "next_agent": next_agent,
        **trace_update,
    }


def route_after_supervisor(state: AgentState) -> str:
    """
    Conditional edge function for LangGraph.
    """

    return state.get("next_agent") or "resolution"