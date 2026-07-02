from langgraph.graph import END, START, StateGraph

from app.agents.clarification import clarification_agent
from app.agents.resolution import resolution_agent
from app.agents.state import AgentState
from app.agents.summary import summary_agent
from app.agents.supervisor import route_after_supervisor, supervisor_agent
from app.agents.triage import triage_agent


def build_helpdesk_graph():
    """
    Builds the Phase 3 LangGraph workflow.

    Node names intentionally use *_agent suffixes so they do not conflict
    with AgentState keys like 'triage' or 'resolution'.
    """

    graph = StateGraph(AgentState)

    graph.add_node("triage_agent", triage_agent)
    graph.add_node("supervisor_agent", supervisor_agent)
    graph.add_node("clarification_agent", clarification_agent)
    graph.add_node("resolution_agent", resolution_agent)
    graph.add_node("summary_agent", summary_agent)

    graph.add_edge(START, "triage_agent")
    graph.add_edge("triage_agent", "supervisor_agent")

    graph.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor,
        {
            "clarification": "clarification_agent",
            "resolution": "resolution_agent",
        },
    )

    graph.add_edge("clarification_agent", "summary_agent")
    graph.add_edge("resolution_agent", "summary_agent")
    graph.add_edge("summary_agent", END)

    return graph.compile()


helpdesk_graph = build_helpdesk_graph()


def run_helpdesk_graph(
    user_message: str,
    user_email: str,
    conversation_id: str | None = None,
) -> AgentState:
    initial_state: AgentState = {
        "user_message": user_message,
        "user_email": user_email,
        "conversation_id": conversation_id,
        "triage": None,
        "next_agent": None,
        "clarification_question": None,
        "resolution": None,
        "final_summary": None,
        "ticket_required": False,
        "sensitive_action": False,
        "requires_approval": False,
        "sources": [],
        "agent_trace": [],
    }

    result = helpdesk_graph.invoke(initial_state)

    return result