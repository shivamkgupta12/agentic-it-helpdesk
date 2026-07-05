import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.database_models import (
    Approval,
    ApprovalStatus,
    Ticket,
)
from app.services.ticket_service import (
    TicketCreateInput,
    TicketService,
    TicketServiceError,
)

logger = logging.getLogger(__name__)


class ApprovalServiceError(RuntimeError):
    """Raised when approval workflow operations fail."""


@dataclass
class ApprovalCreateInput:
    requested_by_user_id: str
    conversation_id: str | None
    action_type: str
    reason: str
    ticket_id: str | None = None


class ApprovalService:
    """
    Handles human-in-the-loop approval workflow.

    Sensitive actions:
    - Password reset
    - Account unlock
    - Access changes
    - Permission changes
    - Security escalation
    - Ticket closure or sensitive field update
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_approval_request(self, data: ApprovalCreateInput) -> Approval:
        approval = Approval(
            ticket_id=data.ticket_id,
            conversation_id=data.conversation_id,
            requested_by_user_id=data.requested_by_user_id,
            action_type=data.action_type,
            reason=data.reason,
            status=ApprovalStatus.pending,
            admin_comment=None,
        )

        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        logger.info("Created approval request %s for %s", approval.id, data.action_type)

        return approval

    def get_approval(self, approval_id: str) -> Approval:
        approval = (
            self.db.query(Approval)
            .filter(Approval.id == approval_id)
            .first()
        )

        if not approval:
            raise ApprovalServiceError(f"Approval request not found: {approval_id}")

        return approval

    def approve(
        self,
        approval_id: str,
        admin_comment: str | None = None,
    ) -> tuple[Approval, Ticket]:
        """
        Approves a sensitive action.

        For this MVP, approval creates a ticket after approval.
        In real mode, this ticket becomes a ServiceNow incident.
        """

        approval = self.get_approval(approval_id)

        if approval.status != ApprovalStatus.pending:
            raise ApprovalServiceError(
                f"Approval request is not pending. Current status: {approval.status.value}"
            )

        ticket = self._create_ticket_after_approval(approval)

        approval.status = ApprovalStatus.approved
        approval.admin_comment = admin_comment
        approval.ticket_id = ticket.id

        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        logger.info(
            "Approved request %s and created ticket %s",
            approval.id,
            ticket.ticket_number,
        )

        return approval, ticket

    def reject(
        self,
        approval_id: str,
        admin_comment: str | None = None,
    ) -> Approval:
        approval = self.get_approval(approval_id)

        if approval.status != ApprovalStatus.pending:
            raise ApprovalServiceError(
                f"Approval request is not pending. Current status: {approval.status.value}"
            )

        approval.status = ApprovalStatus.rejected
        approval.admin_comment = admin_comment

        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        logger.info("Rejected approval request %s", approval.id)

        return approval

    def request_more_information(
        self,
        approval_id: str,
        admin_comment: str | None = None,
    ) -> Approval:
        approval = self.get_approval(approval_id)

        if approval.status != ApprovalStatus.pending:
            raise ApprovalServiceError(
                f"Approval request is not pending. Current status: {approval.status.value}"
            )

        approval.status = ApprovalStatus.needs_more_info
        approval.admin_comment = admin_comment

        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        logger.info("Requested more information for approval request %s", approval.id)

        return approval

    def _create_ticket_after_approval(self, approval: Approval) -> Ticket:
        """
        Creates a support ticket after admin approval.

        This uses TicketService, so it automatically supports:
        - SERVICENOW_MODE=mock
        - SERVICENOW_MODE=real
        """

        title, category, priority, urgency = self._ticket_fields_for_action(
            approval.action_type
        )

        description = (
            f"Sensitive action approved by IT admin.\n\n"
            f"Action type:\n{approval.action_type}\n\n"
            f"Approval reason:\n{approval.reason}\n\n"
            f"Admin comment:\n{approval.admin_comment or 'No admin comment provided.'}\n\n"
            f"Approval ID:\n{approval.id}\n\n"
            "Created by Agentic IT Helpdesk after human approval."
        )

        service = TicketService(self.db)

        try:
            return service.create_ticket(
                TicketCreateInput(
                    user_id=approval.requested_by_user_id,
                    conversation_id=approval.conversation_id,
                    title=title,
                    description=description,
                    category=category,
                    priority=priority,
                    urgency=urgency,
                )
            )

        except TicketServiceError as exc:
            raise ApprovalServiceError(
                f"Approval succeeded, but ticket creation failed: {exc}"
            ) from exc

    def _ticket_fields_for_action(
        self,
        action_type: str,
    ) -> tuple[str, str, str, str]:
        normalized = action_type.lower()

        if "password" in normalized:
            return (
                "Password reset request",
                "Password / Account",
                "Medium",
                "Medium",
            )

        if "unlock" in normalized:
            return (
                "Account unlock request",
                "Password / Account",
                "Medium",
                "Medium",
            )

        if "access" in normalized or "permission" in normalized:
            return (
                "Access change request",
                "Access Request",
                "Medium",
                "Medium",
            )

        if "security" in normalized:
            return (
                "Security incident escalation",
                "Security Incident",
                "Critical",
                "Critical",
            )

        return (
            "Sensitive IT support request",
            "General IT Query",
            "Medium",
            "Medium",
        )