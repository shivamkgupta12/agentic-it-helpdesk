import logging

from pydantic import ValidationError

from app.agents.state import AgentState
from app.agents.utils import add_trace_step, extract_json_object, keyword_triage_fallback
from app.schemas.agents import TriageResult
from app.services.azure_openai_client import AzureOpenAIConfigError, AzureOpenAIService

logger = logging.getLogger(__name__)


TRIAGE_SYSTEM_PROMPT = """
You are the Triage Agent for an enterprise IT helpdesk.

Classify the user's IT issue into exactly one of these categories:
- Network / VPN
- Password / Account
- Software Request
- Hardware Issue
- Email / Outlook
- Access Request
- Security Incident
- Cloud / Account Access
- General IT Query

Return ONLY valid JSON with this exact schema:
{
  "category": "...",
  "priority": "Low | Medium | High | Critical",
  "urgency": "Low | Medium | High | Critical",
  "needs_clarification": true,
  "clarifying_question": "...",
  "ticket_required": true,
  "sensitive_action": false
}

Rules:
- Password reset requests must be category "Password / Account".
- Password reset requests must set sensitive_action=true.
- Password reset requests must set ticket_required=true.
- Password reset requests must set needs_clarification=false.
- Account unlock requests must set sensitive_action=true.
- Access changes and permission changes must set sensitive_action=true.
- Security incident escalation must set sensitive_action=true.
- For sensitive actions, do not block the workflow with clarification. Approval will handle verification.
- VPN issues usually need a ticket if unresolved.
- Software installation requests usually need a ticket.
- If a non-sensitive message is vague, set needs_clarification=true and ask one short clarifying question.
- Do not include markdown.
- Do not include explanation.
"""


def triage_agent(state: AgentState) -> dict:
    user_message = state["user_message"]

    try:
        service = AzureOpenAIService()

        raw_response = service.generate_chat_response(
            user_message=user_message,
            system_message=TRIAGE_SYSTEM_PROMPT,
        )

        parsed_json = extract_json_object(raw_response)
        triage = TriageResult(**parsed_json)

        output_summary = (
            f"Classified as {triage.category}, priority={triage.priority}, "
            f"sensitive_action={triage.sensitive_action}, "
            f"needs_clarification={triage.needs_clarification}."
        )

        trace_update = add_trace_step(
            state=state,
            agent_name="Triage Agent",
            input_summary=user_message,
            output_summary=output_summary,
            metadata=triage.model_dump(),
        )

        return {
            "triage": triage,
            "ticket_required": triage.ticket_required,
            "sensitive_action": triage.sensitive_action,
            "requires_approval": triage.sensitive_action,
            **trace_update,
        }

    except (AzureOpenAIConfigError, RuntimeError, ValidationError, ValueError) as exc:
        logger.warning("Triage Agent fallback triggered: %s", exc)

        fallback = keyword_triage_fallback(user_message)
        triage = TriageResult(**fallback)

        trace_update = add_trace_step(
            state=state,
            agent_name="Triage Agent",
            input_summary=user_message,
            output_summary=(
                f"Used fallback triage. Classified as {triage.category}, "
                f"sensitive_action={triage.sensitive_action}."
            ),
            metadata={
                "fallback": True,
                "reason": str(exc),
                **triage.model_dump(),
            },
        )

        return {
            "triage": triage,
            "ticket_required": triage.ticket_required,
            "sensitive_action": triage.sensitive_action,
            "requires_approval": triage.sensitive_action,
            **trace_update,
        }