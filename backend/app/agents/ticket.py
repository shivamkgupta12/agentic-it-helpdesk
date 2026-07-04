import logging

from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.utils import add_trace_step
from app.services.ticket_service import TicketCreateInput, TicketService, TicketServiceError

logger = logging.getLogger(__name__)


def user_is_asking_for_ticket(user_message: str) -> bool:
    text = user_message.lower()

    ticket_phrases = [
        "create ticket",
        "raise ticket",
        "open ticket",
        "log ticket",
        "submit ticket",
        "create a ticket",
        "raise a ticket",
        "open a ticket",
        "log a ticket",
    ]

    unresolved_phrases = [
        "still not working",
        "still doesn't work",
        "still does not work",
        "not resolved",
        "unresolved",
        "still disconnecting",
        "keeps disconnecting",
        "issue continues",
        "problem continues",
        "tried the steps",
    ]

    return any(phrase in text for phrase in ticket_phrases + unresolved_phrases)


def should_create_ticket_now(state: AgentState) -> bool:
    triage = state.get("triage")

    if not triage:
        return False

    if triage.needs_clarification:
        return False

    if triage.sensitive_action:
        # Phase 7 will handle approval before ticket creation.
        return False

    if not triage.ticket_required:
        return False

    user_message = state["user_message"]

    if triage.category == "Software Request":
        return True

    if user_is_asking_for_ticket(user_message):
        return True

    return False


def build_ticket_title(state: AgentState) -> str:
    triage = state.get("triage")
    category = triage.category if triage else "General IT Query"

    if category == "Network / VPN":
        return "VPN connectivity issue"

    if category == "Software Request":
        return "Software installation request"

    if category == "Email / Outlook":
        return "Email or Outlook support issue"

    if category == "Hardware Issue":
        return "Hardware support issue"

    return f"{category} support request"


def build_ticket_description(state: AgentState) -> str:
    triage = state.get("triage")
    resolution = state.get("resolution") or ""
    sources = state.get("sources", [])

    source_titles = []
    for source in sources:
        title = source.get("title", "Unknown source")
        if title not in source_titles:
            source_titles.append(title)

    source_text = ", ".join(source_titles) if source_titles else "No sources retrieved"

    return (
        f"User issue:\n{state['user_message']}\n\n"
        f"Category:\n{triage.category if triage else 'General IT Query'}\n\n"
        f"Priority:\n{triage.priority if triage else 'Medium'}\n\n"
        f"Urgency:\n{triage.urgency if triage else 'Medium'}\n\n"
        f"AI troubleshooting guidance:\n{resolution}\n\n"
        f"Knowledge sources used:\n{source_text}\n\n"
        "Created by Agentic IT Helpdesk mock ticket workflow."
    )


def ticket_agent(state: AgentState) -> dict:
    """
    Creates a local mock ticket when appropriate.

    Phase 5:
    - Creates local DB ticket in mock mode.
    - Does not call real ServiceNow.
    - Does not create sensitive-action tickets yet.
    """

    create_now = should_create_ticket_now(state)

    if not create_now:
        reason = (
            "Ticket was not created. Either the request is sensitive, needs clarification, "
            "or the user has not asked to create a ticket yet."
        )

        trace_update = add_trace_step(
            state=state,
            agent_name="Ticket Agent",
            input_summary=state.get("user_message"),
            output_summary=reason,
            metadata={
                "ticket_created": False,
                "sensitive_action": state.get("sensitive_action", False),
                "ticket_required": state.get("ticket_required", False),
            },
        )

        return {
            "should_create_ticket": False,
            "ticket_id": None,
            "ticket_number": None,
            "ticket_status": None,
            **trace_update,
        }

    db: Session | None = state.get("db_session")
    user_id = state.get("user_id")

    if db is None or not user_id:
        error_message = "Ticket could not be created because database session or user_id is missing."

        trace_update = add_trace_step(
            state=state,
            agent_name="Ticket Agent",
            input_summary=state.get("user_message"),
            output_summary=error_message,
            metadata={
                "ticket_created": False,
                "error": error_message,
            },
        )

        return {
            "should_create_ticket": True,
            "ticket_id": None,
            "ticket_number": None,
            "ticket_status": None,
            **trace_update,
        }

    triage = state.get("triage")

    try:
        service = TicketService(db)

        ticket = service.create_ticket(
            TicketCreateInput(
                user_id=user_id,
                conversation_id=state.get("conversation_id"),
                title=build_ticket_title(state),
                description=build_ticket_description(state),
                category=triage.category if triage else "General IT Query",
                priority=triage.priority if triage else "Medium",
                urgency=triage.urgency if triage else "Medium",
            )
        )

        output_summary = (
            f"Created mock ticket {ticket.ticket_number} with status {ticket.status.value}."
        )

        trace_update = add_trace_step(
            state=state,
            agent_name="Ticket Agent",
            input_summary=state.get("user_message"),
            output_summary=output_summary,
            metadata={
                "ticket_created": True,
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status.value,
                "source": ticket.source,
            },
        )

        return {
            "should_create_ticket": True,
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "ticket_status": ticket.status.value,
            **trace_update,
        }

    except TicketServiceError as exc:
        logger.warning("Ticket creation failed: %s", exc)

        trace_update = add_trace_step(
            state=state,
            agent_name="Ticket Agent",
            input_summary=state.get("user_message"),
            output_summary=f"Ticket creation failed: {exc}",
            metadata={
                "ticket_created": False,
                "error": str(exc),
            },
        )

        return {
            "should_create_ticket": True,
            "ticket_id": None,
            "ticket_number": None,
            "ticket_status": None,
            **trace_update,
        }