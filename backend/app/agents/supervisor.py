from app.agents.state import AgentState
from app.agents.utils import add_trace_step


def supervisor_agent(state: AgentState) -> dict:
    """
    Decides which agent should act next.

    Routing priority:
    1. Sensitive actions should NOT stop at clarification.
       They should go through knowledge + resolution + approval.
    2. Vague non-sensitive issues can go to clarification.
    3. All other issues go to knowledge retrieval.
    """

    triage = state.get("triage")

    if triage and triage.sensitive_action:
        next_agent = "knowledge"
        decision = (
            "Selected Knowledge Retrieval Agent because the request is sensitive "
            "and must proceed toward human approval."
        )

    elif triage and triage.needs_clarification:
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
            "sensitive_action": triage.sensitive_action if triage else False,
            "needs_clarification": triage.needs_clarification if triage else False,
        },
    )

    return {
        "next_agent": next_agent,
        **trace_update,
    }


def route_after_supervisor(state: AgentState) -> str:
    return state.get("next_agent") or "knowledge"