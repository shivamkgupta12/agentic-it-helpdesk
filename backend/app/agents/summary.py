import logging

from app.agents.state import AgentState
from app.agents.utils import add_trace_step
from app.services.azure_openai_client import AzureOpenAIConfigError, AzureOpenAIService

logger = logging.getLogger(__name__)


SUMMARY_SYSTEM_PROMPT = """
You are the Summary Agent for an enterprise IT helpdesk.

Create a concise user-facing final response.

Include:
- Issue Summary
- Category
- Recommended Steps
- Approval Status if approval is required
- Ticket Status if a ticket was created
- Ticket Recommendation only if no ticket was created and no approval is pending
- Sources Used if sources are available

Rules:
- Do not include a Ticket Recommendation section if a ticket was already created.
- Do not claim a ServiceNow ticket was created unless a ticket number is provided.
- If approval is required, clearly say the workflow is paused pending admin approval.
- If an approval ID exists, include it.
- If the ticket number starts with MOCK, clearly call it a mock/local demo ticket.
- If the ticket number starts with INC, call it a ServiceNow incident.
- Keep it clear and professional.
"""


def build_fallback_summary(state: AgentState) -> str:
    triage = state.get("triage")
    resolution = state.get("resolution") or state.get("clarification_question") or ""
    sources = state.get("sources", [])

    ticket_number = state.get("ticket_number")
    ticket_status = state.get("ticket_status")

    approval_id = state.get("approval_id")
    approval_status = state.get("approval_status")
    approval_action_type = state.get("approval_action_type")

    if not triage:
        return resolution

    approval_note = ""
    if triage.sensitive_action:
        if approval_id:
            approval_note = (
                "\n\nApproval Status:\n"
                f"This request requires human approval before any action can proceed.\n"
                f"Approval ID: {approval_id}\n"
                f"Action type: {approval_action_type or 'Sensitive IT Action'}\n"
                f"Current status: {approval_status or 'pending'}.\n"
                "An IT admin can approve, reject, or request more information."
            )
        else:
            approval_note = (
                "\n\nApproval Status:\n"
                "This request requires human approval or identity verification before it can proceed. "
                "The approval request could not be created automatically."
            )

    if ticket_number:
        if str(ticket_number).startswith("INC"):
            ticket_label = "ServiceNow incident"
        elif str(ticket_number).startswith("MOCK"):
            ticket_label = "local mock ticket"
        else:
            ticket_label = "ticket"

        ticket_note = (
            f"\n\nTicket Status:\n"
            f"A {ticket_label} has been created: {ticket_number}.\n"
            f"Current status: {ticket_status or 'Open'}."
        )
    else:
        if triage.sensitive_action:
            ticket_note = (
                "\n\nTicket Status:\n"
                "No ticket has been created yet. A ticket can be created after admin approval."
            )
        elif triage.ticket_required:
            ticket_note = (
                "\n\nTicket Recommendation:\n"
                "If the issue remains unresolved after these steps, a support ticket should be created."
            )
        else:
            ticket_note = "\n\nTicket Recommendation:\nA ticket is not required yet."

    sources_note = ""
    if sources:
        source_titles = []
        for source in sources:
            title = source.get("title", "Unknown source")
            if title not in source_titles:
                source_titles.append(title)

        sources_note = "\n\nSources Used:\n" + "\n".join(
            f"- {title}" for title in source_titles
        )

    return (
        f"Issue Summary:\n{state['user_message']}\n\n"
        f"Category:\n{triage.category}\n\n"
        f"Recommended Steps:\n{resolution}"
        f"{approval_note}"
        f"{ticket_note}"
        f"{sources_note}"
    )


def summary_agent(state: AgentState) -> dict:
    triage = state.get("triage")
    resolution = state.get("resolution") or state.get("clarification_question") or ""

    sources = state.get("sources", [])
    ticket_number = state.get("ticket_number")
    ticket_status = state.get("ticket_status")
    
    approval_id = state.get("approval_id")
    approval_status = state.get("approval_status")
    approval_action_type = state.get("approval_action_type")

    prompt = (
        f"User issue: {state['user_message']}\n\n"
        f"Triage result: {triage.model_dump() if triage else {}}\n\n"
        f"Resolution or clarification:\n{resolution}\n\n"
        f"Approval ID: {approval_id}\n"
        f"Approval status: {approval_status}\n"
        f"Approval action type: {approval_action_type}\n\n"
        f"Ticket number: {ticket_number}\n"
        f"Ticket status: {ticket_status}\n\n"
        f"Sources:\n{sources}\n\n"
        "Create the final response. "
        "If approval is pending, explain that the workflow is paused. "
        "If a ticket number exists, include it clearly. "
        "If sources are available, include a short 'Sources Used' section."
    )

    try:
        service = AzureOpenAIService()

        final_summary = service.generate_chat_response(
            user_message=prompt,
            system_message=SUMMARY_SYSTEM_PROMPT,
        )

        if not final_summary or "empty visible response" in final_summary.lower():
            raise RuntimeError(final_summary)

    except (AzureOpenAIConfigError, RuntimeError) as exc:
        logger.warning("Summary Agent fallback triggered: %s", exc)
        final_summary = build_fallback_summary(state)

    trace_update = add_trace_step(
        state=state,
        agent_name="Summary Agent",
        input_summary="Generated final user-facing summary.",
        output_summary=final_summary[:500],
        metadata={
            "has_triage": triage is not None,
        },
    )

    return {
        "final_summary": final_summary,
        **trace_update,
    }