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

    Current flow:
    START
      → Triage Agent
      → Supervisor Agent
      → either Clarification Agent or Resolution Agent
      → Summary Agent
      → END
    """

    graph = StateGraph(AgentState)

    graph.add_node("triage", triage_agent)
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("clarification", clarification_agent)
    graph.add_node("resolution", resolution_agent)
    graph.add_node("summary", summary_agent)

    graph.add_edge(START, "triage")
    graph.add_edge("triage", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "clarification": "clarification",
            "resolution": "resolution",
        },
    )

    graph.add_edge("clarification", "summary")
    graph.add_edge("resolution", "summary")
    graph.add_edge("summary", END)

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