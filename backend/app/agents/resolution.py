import logging

from app.agents.state import AgentState
from app.agents.utils import add_trace_step
from app.services.azure_openai_client import AzureOpenAIConfigError, AzureOpenAIService

logger = logging.getLogger(__name__)


RESOLUTION_SYSTEM_PROMPT = """
You are the Resolution Agent for an enterprise IT helpdesk.

Generate safe, practical troubleshooting guidance for the user's issue.

Rules:
- Use the retrieved internal knowledge base context when available.
- Give clear numbered steps.
- Mention source titles naturally when useful.
- Do not invent policy details that are not in the context.
- Do not claim that a ticket was created.
- Do not claim that you reset a password, changed access, installed software, or performed admin actions.
- If the issue is sensitive, explain that admin approval or identity verification is required.
- If the issue may remain unresolved, say that a support ticket may be needed.
- Keep the answer concise.
"""


def build_fallback_resolution(category: str, sensitive_action: bool) -> str:
    if sensitive_action:
        return (
            "This request may involve a sensitive IT action, so it requires admin approval "
            "or identity verification before any change can be made.\n\n"
            "Next steps:\n"
            "1. Confirm your work email and device/user account details.\n"
            "2. Wait for an IT admin to approve or verify the request.\n"
            "3. After approval, IT support can proceed with the required action."
        )

    if category == "Network / VPN":
        return (
            "Try these VPN troubleshooting steps:\n"
            "1. Disconnect and reconnect to the VPN.\n"
            "2. Restart the VPN client and confirm your internet connection is stable.\n"
            "3. Check whether MFA approval is completing successfully.\n"
            "4. Restart your laptop if the VPN client keeps disconnecting.\n\n"
            "If the issue continues, a support ticket should be created for IT investigation."
        )

    if category == "Software Request":
        return (
            "For a software installation request:\n"
            "1. Confirm the software name, business purpose, and device type.\n"
            "2. Check whether the software is approved by company policy.\n"
            "3. If approval is required, submit the request for IT/admin review.\n\n"
            "A support request may be needed before installation."
        )

    return (
        "Here are general IT troubleshooting steps:\n"
        "1. Restart the affected application or device.\n"
        "2. Check whether the issue happens on another network or browser.\n"
        "3. Capture the exact error message or screenshot.\n"
        "4. If the issue continues, create a support ticket for IT review."
    )


def resolution_agent(state: AgentState) -> dict:
    user_message = state["user_message"]
    triage = state.get("triage")

    category = triage.category if triage else "General IT Query"
    sensitive_action = triage.sensitive_action if triage else False

    retrieved_context = state.get("retrieved_context") or "No retrieved knowledge base context available."

    prompt = (
        f"User issue: {user_message}\n\n"
        f"Triage category: {category}\n"
        f"Priority: {triage.priority if triage else 'Medium'}\n"
        f"Urgency: {triage.urgency if triage else 'Medium'}\n"
        f"Sensitive action: {sensitive_action}\n"
        f"Ticket likely required: {triage.ticket_required if triage else False}\n\n"
        f"Retrieved internal knowledge base context:\n"
        f"{retrieved_context}\n\n"
        "Generate the response using the internal context where relevant."
    )

    try:
        service = AzureOpenAIService()

        resolution = service.generate_chat_response(
            user_message=prompt,
            system_message=RESOLUTION_SYSTEM_PROMPT,
        )

        if not resolution or "empty visible response" in resolution.lower():
            raise RuntimeError(resolution)

    except (AzureOpenAIConfigError, RuntimeError) as exc:
        logger.warning("Resolution Agent fallback triggered: %s", exc)

        resolution = build_fallback_resolution(
            category=category,
            sensitive_action=sensitive_action,
        )

    trace_update = add_trace_step(
        state=state,
        agent_name="Resolution Agent",
        input_summary=f"Category={category}; sensitive_action={sensitive_action}",
        output_summary=resolution[:500],
        metadata={
        "category": category,
        "sensitive_action": sensitive_action,
        "used_rag_context": bool(state.get("retrieved_context")),
        "source_count": len(state.get("sources", [])),
    },
    )

    return {
        "resolution": resolution,
        **trace_update,
    }