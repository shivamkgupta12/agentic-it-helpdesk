import json
import logging
import re
from typing import Any

from app.schemas.agents import AgentTraceStep

logger = logging.getLogger(__name__)


def add_trace_step(
    state: dict,
    agent_name: str,
    input_summary: str | None = None,
    output_summary: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """
    Adds a readable agent trace step to the state.
    These will later be saved into the agent_logs table.
    """

    trace = list(state.get("agent_trace", []))

    trace.append(
        AgentTraceStep(
            agent_name=agent_name,
            input_summary=input_summary,
            output_summary=output_summary,
            metadata=metadata or {},
        )
    )

    return {
        "agent_trace": trace,
    }


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extracts the first JSON object from an LLM response.

    Handles responses like:
    ```json
    {...}
    ```
    or text before/after JSON.
    """

    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

        if not match:
            raise

        return json.loads(match.group(0))


def keyword_triage_fallback(user_message: str) -> dict[str, Any]:
    """
    Deterministic fallback if Azure OpenAI fails to return valid JSON.

    This makes the portfolio demo stable even if the LLM response is malformed.
    """

    text = user_message.lower()

    if any(word in text for word in ["vpn", "network", "internet", "wifi", "wi-fi"]):
        return {
            "category": "Network / VPN",
            "priority": "Medium",
            "urgency": "Medium",
            "needs_clarification": False,
            "clarifying_question": None,
            "ticket_required": True,
            "sensitive_action": False,
        }

    if any(word in text for word in ["password", "reset password", "forgot password", "account unlock"]):
        return {
            "category": "Password / Account",
            "priority": "Medium",
            "urgency": "Medium",
            "needs_clarification": False,
            "clarifying_question": None,
            "ticket_required": True,
            "sensitive_action": True,
        }

    if any(word in text for word in ["install", "software", "figma", "application", "app"]):
        return {
            "category": "Software Request",
            "priority": "Low",
            "urgency": "Medium",
            "needs_clarification": False,
            "clarifying_question": None,
            "ticket_required": True,
            "sensitive_action": False,
        }

    if any(word in text for word in ["outlook", "email", "teams", "calendar"]):
        return {
            "category": "Email / Outlook",
            "priority": "Medium",
            "urgency": "Medium",
            "needs_clarification": False,
            "clarifying_question": None,
            "ticket_required": True,
            "sensitive_action": False,
        }

    if any(word in text for word in ["hacked", "phishing", "malware", "suspicious", "security"]):
        return {
            "category": "Security Incident",
            "priority": "Critical",
            "urgency": "Critical",
            "needs_clarification": False,
            "clarifying_question": None,
            "ticket_required": True,
            "sensitive_action": True,
        }

    if len(text.split()) < 5:
        return {
            "category": "General IT Query",
            "priority": "Medium",
            "urgency": "Medium",
            "needs_clarification": True,
            "clarifying_question": (
                "Can you confirm whether the issue is related to login, VPN, "
                "software, internet, email, access, or hardware?"
            ),
            "ticket_required": False,
            "sensitive_action": False,
        }

    return {
        "category": "General IT Query",
        "priority": "Medium",
        "urgency": "Medium",
        "needs_clarification": True,
        "clarifying_question": (
            "Can you provide more detail about what is not working and what error message you see?"
        ),
        "ticket_required": False,
        "sensitive_action": False,
    }