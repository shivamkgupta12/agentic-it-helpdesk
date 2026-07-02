from app.agents.state import AgentState
from app.agents.utils import add_trace_step


def clarification_agent(state: AgentState) -> dict:
    triage = state.get("triage")

    question = (
        triage.clarifying_question
        if triage and triage.clarifying_question
        else "Can you provide more details about the IT issue you are facing?"
    )

    trace_update = add_trace_step(
        state=state,
        agent_name="Clarification Agent",
        input_summary=state.get("user_message"),
        output_summary=question,
        metadata={
            "needs_clarification": True,
        },
    )

    return {
        "clarification_question": question,
        "final_summary": question,
        **trace_update,
    }