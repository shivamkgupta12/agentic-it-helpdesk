import logging

from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.utils import add_trace_step
from app.services.approval_service import (
    ApprovalCreateInput,
    ApprovalService,
    ApprovalServiceError,
)

logger = logging.getLogger(__name__)


def infer_action_type(state: AgentState) -> str:
    triage = state.get("triage")
    user_message = state.get("user_message", "").lower()

    if "password" in user_message:
        return "Password Reset"

    if "unlock" in user_message:
        return "Account Unlock"

    if triage and triage.category == "Access Request":
        return "Access Change"

    if triage and triage.category == "Security Incident":
        return "Security Incident Escalation"

    if "permission" in user_message or "access" in user_message:
        return "Access Change"

    return "Sensitive IT Action"


def build_approval_reason(state: AgentState) -> str:
    triage = state.get("triage")
    resolution = state.get("resolution") or ""

    return (
        f"User requested a sensitive IT action.\n\n"
        f"Original user message:\n{state.get('user_message')}\n\n"
        f"Triage category:\n{triage.category if triage else 'Unknown'}\n\n"
        f"Priority:\n{triage.priority if triage else 'Medium'}\n\n"
        f"Urgency:\n{triage.urgency if triage else 'Medium'}\n\n"
        f"AI guidance provided:\n{resolution}\n\n"
        "This action requires human approval before a ticket or operational change is created."
    )


def human_approval_agent(state: AgentState) -> dict:
    """
    Creates an approval request for sensitive actions.

    This agent does not approve anything by itself.
    It only pauses the workflow and creates an approval request for an admin.
    """

    triage = state.get("triage")

    if not triage or not triage.sensitive_action:
        trace_update = add_trace_step(
            state=state,
            agent_name="Human Approval Agent",
            input_summary=state.get("user_message"),
            output_summary="No approval required.",
            metadata={
                "approval_created": False,
                "reason": "sensitive_action=false",
            },
        )

        return {
            "requires_approval": False,
            "approval_id": None,
            "approval_status": None,
            **trace_update,
        }

    db: Session | None = state.get("db_session")
    user_id = state.get("user_id")

    if db is None or not user_id:
        message = "Approval request could not be created because db_session or user_id is missing."

        trace_update = add_trace_step(
            state=state,
            agent_name="Human Approval Agent",
            input_summary=state.get("user_message"),
            output_summary=message,
            metadata={
                "approval_created": False,
                "error": message,
            },
        )

        return {
            "requires_approval": True,
            "approval_id": None,
            "approval_status": None,
            **trace_update,
        }

    action_type = infer_action_type(state)
    reason = build_approval_reason(state)

    try:
        service = ApprovalService(db)

        approval = service.create_approval_request(
            ApprovalCreateInput(
                requested_by_user_id=user_id,
                conversation_id=state.get("conversation_id"),
                action_type=action_type,
                reason=reason,
            )
        )

        output_summary = (
            f"Created approval request {approval.id} for action type: {action_type}."
        )

        trace_update = add_trace_step(
            state=state,
            agent_name="Human Approval Agent",
            input_summary=state.get("user_message"),
            output_summary=output_summary,
            metadata={
                "approval_created": True,
                "approval_id": approval.id,
                "approval_status": approval.status.value,
                "action_type": action_type,
            },
        )

        return {
            "requires_approval": True,
            "approval_id": approval.id,
            "approval_status": approval.status.value,
            "approval_action_type": action_type,
            **trace_update,
        }

    except ApprovalServiceError as exc:
        logger.warning("Approval request creation failed: %s", exc)

        trace_update = add_trace_step(
            state=state,
            agent_name="Human Approval Agent",
            input_summary=state.get("user_message"),
            output_summary=f"Approval request creation failed: {exc}",
            metadata={
                "approval_created": False,
                "error": str(exc),
            },
        )

        return {
            "requires_approval": True,
            "approval_id": None,
            "approval_status": None,
            **trace_update,
        }