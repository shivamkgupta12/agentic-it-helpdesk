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
- Ticket Recommendation
- Approval Requirement if sensitive
- Sources Used if sources are available

Do not claim a ServiceNow ticket was created unless a ticket number is provided.
Keep it clear and professional.
"""


def build_fallback_summary(state: AgentState) -> str:
    triage = state.get("triage")
    resolution = state.get("resolution") or state.get("clarification_question") or ""
    sources = state.get("sources", [])

    if not triage:
        return resolution

    approval_note = ""
    if triage.sensitive_action:
        approval_note = (
            "\n\nApproval Requirement:\n"
            "This request involves a sensitive IT action and requires admin approval "
            "or identity verification before it can proceed."
        )

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
        f"Recommended Steps:\n{resolution}\n\n"
        f"Ticket Recommendation:\n"
        f"{'A support ticket is recommended if the issue remains unresolved.' if triage.ticket_required else 'A ticket is not required yet.'}"
        f"{approval_note}"
        f"{sources_note}"
    )


def summary_agent(state: AgentState) -> dict:
    triage = state.get("triage")
    resolution = state.get("resolution") or state.get("clarification_question") or ""

    sources = state.get("sources", [])

    prompt = (
        f"User issue: {state['user_message']}\n\n"
        f"Triage result: {triage.model_dump() if triage else {}}\n\n"
        f"Resolution or clarification:\n{resolution}\n\n"
        f"Sources:\n{sources}\n\n"
        "Create the final response. If sources are available, include a short 'Sources Used' section."
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