from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agents.clarification import clarification_agent
from app.agents.knowledge import knowledge_retrieval_agent
from app.agents.resolution import resolution_agent
from app.agents.state import AgentState
from app.agents.summary import summary_agent
from app.agents.supervisor import route_after_supervisor, supervisor_agent
from app.agents.ticket import should_create_ticket_now, ticket_agent
from app.agents.triage import triage_agent


def route_after_resolution(state: AgentState) -> str:
    """
    Decide whether to run Ticket Agent before Summary Agent.
    """

    if should_create_ticket_now(state):
        return "ticket"

    return "summary"


def build_helpdesk_graph():
    """
    Builds the Phase 5 LangGraph workflow.

    Flow:
    START
      → Triage Agent
      → Supervisor Agent
      → Clarification Agent OR Knowledge Retrieval Agent
      → Resolution Agent
      → Ticket Agent if ticket should be created
      → Summary Agent
      → END
    """

    graph = StateGraph(AgentState)

    graph.add_node("triage_agent", triage_agent)
    graph.add_node("supervisor_agent", supervisor_agent)
    graph.add_node("clarification_agent", clarification_agent)
    graph.add_node("knowledge_agent", knowledge_retrieval_agent)
    graph.add_node("resolution_agent", resolution_agent)
    graph.add_node("ticket_agent", ticket_agent)
    graph.add_node("summary_agent", summary_agent)

    graph.add_edge(START, "triage_agent")
    graph.add_edge("triage_agent", "supervisor_agent")

    graph.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor,
        {
            "clarification": "clarification_agent",
            "knowledge": "knowledge_agent",
        },
    )

    graph.add_edge("clarification_agent", "summary_agent")
    graph.add_edge("knowledge_agent", "resolution_agent")

    graph.add_conditional_edges(
        "resolution_agent",
        route_after_resolution,
        {
            "ticket": "ticket_agent",
            "summary": "summary_agent",
        },
    )

    graph.add_edge("ticket_agent", "summary_agent")
    graph.add_edge("summary_agent", END)

    return graph.compile()


helpdesk_graph = build_helpdesk_graph()


def run_helpdesk_graph(
    user_message: str,
    user_email: str,
    conversation_id: str | None = None,
    user_id: str | None = None,
    db_session: Any | None = None,
) -> AgentState:
    initial_state: AgentState = {
        "user_message": user_message,
        "user_email": user_email,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "db_session": db_session,
        "triage": None,
        "next_agent": None,
        "clarification_question": None,
        "retrieved_context": None,
        "sources": [],
        "resolution": None,
        "final_summary": None,
        "ticket_required": False,
        "sensitive_action": False,
        "requires_approval": False,
        "should_create_ticket": False,
        "ticket_id": None,
        "ticket_number": None,
        "ticket_status": None,
        "agent_trace": [],
    }

    result = helpdesk_graph.invoke(initial_state)

    return result