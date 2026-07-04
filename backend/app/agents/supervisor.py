from app.agents.state import AgentState
from app.agents.utils import add_trace_step


def supervisor_agent(state: AgentState) -> dict:
    """
    Decides which agent should act next.

    Phase 4 routing:
    - If clarification is needed: go to Clarification Agent.
    - Otherwise: go to Knowledge Retrieval Agent.
    """

    triage = state.get("triage")

    if triage and triage.needs_clarification:
        next_agent = "clarification"
        decision = "Selected Clarification Agent because the issue is vague."

    else:
        next_agent = "knowledge"
        decision = "Selected Knowledge Retrieval Agent to search internal IT documents."

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
    return state.get("next_agent") or "knowledge"