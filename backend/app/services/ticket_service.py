import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.database_models import (
    Ticket,
    TicketEvent,
    TicketStatus,
    User,
)
from app.services.servicenow_client import (
    ServiceNowAPIError,
    ServiceNowClient,
    ServiceNowConfigError,
    ServiceNowIncidentCreateInput,
)

logger = logging.getLogger(__name__)


@dataclass
class TicketCreateInput:
    user_id: str
    conversation_id: str | None
    title: str
    description: str
    category: str
    priority: str
    urgency: str


class TicketServiceError(RuntimeError):
    """Raised when ticket operations fail."""


class TicketService:
    """
    Ticket service used by the Ticket Agent and ticket API routes.

    Supports:
    - Mock local tickets
    - Real ServiceNow incidents
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def generate_mock_ticket_number(self) -> str:
        existing_count = self.db.query(Ticket).count()
        next_number = 1001 + existing_count

        while True:
            ticket_number = f"MOCK{next_number:06d}"

            existing = (
                self.db.query(Ticket)
                .filter(Ticket.ticket_number == ticket_number)
                .first()
            )

            if not existing:
                return ticket_number

            next_number += 1

    def create_ticket(self, data: TicketCreateInput) -> Ticket:
        if self.settings.servicenow_mode == "real":
            return self._create_real_servicenow_ticket(data)

        return self._create_mock_ticket(data)

    def _create_mock_ticket(self, data: TicketCreateInput) -> Ticket:
        ticket_number = self.generate_mock_ticket_number()

        ticket = Ticket(
            user_id=data.user_id,
            conversation_id=data.conversation_id,
            ticket_number=ticket_number,
            servicenow_sys_id=None,
            title=data.title,
            description=data.description,
            category=data.category,
            priority=data.priority,
            urgency=data.urgency,
            status=TicketStatus.open,
            source="mock",
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="created",
            description=f"Mock ticket {ticket.ticket_number} created by AI Ticket Agent.",
            metadata_json=None,
        )

        self.db.add(event)
        self.db.commit()

        logger.info("Created mock ticket %s", ticket.ticket_number)

        return ticket

    def _create_real_servicenow_ticket(self, data: TicketCreateInput) -> Ticket:
        try:
            client = ServiceNowClient()

            sn_category = client.map_category_to_servicenow(data.category)
            impact, urgency = client.map_priority_to_impact_urgency(
                priority=data.priority,
                urgency=data.urgency,
            )

            incident = client.create_incident(
                ServiceNowIncidentCreateInput(
                    short_description=data.title,
                    description=data.description,
                    category=sn_category,
                    impact=impact,
                    urgency=urgency,
                    comments="Created by Agentic IT Helpdesk AI Ticket Agent.",
                    work_notes=(
                        "AI triage completed. "
                        f"Category={data.category}; Priority={data.priority}; Urgency={data.urgency}."
                    ),
                )
            )

            ticket = Ticket(
                user_id=data.user_id,
                conversation_id=data.conversation_id,
                ticket_number=incident.number,
                servicenow_sys_id=incident.sys_id,
                title=data.title,
                description=data.description,
                category=data.category,
                priority=data.priority,
                urgency=data.urgency,
                status=TicketStatus.open,
                source="servicenow",
            )

            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)

            event = TicketEvent(
                ticket_id=ticket.id,
                event_type="created",
                description=f"ServiceNow incident {incident.number} created by AI Ticket Agent.",
                metadata_json=None,
            )

            self.db.add(event)
            self.db.commit()

            logger.info("Created ServiceNow incident %s", incident.number)

            return ticket

        except (ServiceNowConfigError, ServiceNowAPIError) as exc:
            logger.exception("ServiceNow ticket creation failed")
            raise TicketServiceError(f"ServiceNow ticket creation failed: {exc}") from exc

    def get_ticket_by_number(self, ticket_number: str) -> Ticket | None:
        return (
            self.db.query(Ticket)
            .filter(Ticket.ticket_number == ticket_number)
            .first()
        )

    def get_ticket_status(self, ticket_number: str) -> dict:
        ticket = self.get_ticket_by_number(ticket_number)

        if not ticket:
            raise TicketServiceError(f"Ticket not found: {ticket_number}")

        if self.settings.servicenow_mode == "real" and ticket.servicenow_sys_id:
            try:
                client = ServiceNowClient()
                incident = client.get_incident_by_sys_id(ticket.servicenow_sys_id)

                latest_update = (
                    f"ServiceNow incident {incident.number} currently has "
                    f"state={incident.state}, priority={incident.priority}."
                )

                return {
                    "ticket_number": incident.number,
                    "status": incident.state or ticket.status.value,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "urgency": ticket.urgency,
                    "latest_update": latest_update,
                }

            except (ServiceNowConfigError, ServiceNowAPIError) as exc:
                logger.warning("Could not fetch real ServiceNow status: %s", exc)

        latest_event = (
            self.db.query(TicketEvent)
            .filter(TicketEvent.ticket_id == ticket.id)
            .order_by(TicketEvent.created_at.desc())
            .first()
        )

        return {
            "ticket_number": ticket.ticket_number,
            "status": ticket.status.value if hasattr(ticket.status, "value") else str(ticket.status),
            "category": ticket.category,
            "priority": ticket.priority,
            "urgency": ticket.urgency,
            "latest_update": latest_event.description if latest_event else None,
        }

    def update_ticket(
        self,
        ticket: Ticket,
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        urgency: str | None = None,
        status: str | None = None,
    ) -> Ticket:
        if title is not None:
            ticket.title = title

        if description is not None:
            ticket.description = description

        if category is not None:
            ticket.category = category

        if priority is not None:
            ticket.priority = priority

        if urgency is not None:
            ticket.urgency = urgency

        if status is not None:
            try:
                ticket.status = TicketStatus(status)
            except ValueError as exc:
                raise TicketServiceError(f"Invalid ticket status: {status}") from exc

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="updated",
            description="Ticket updated locally.",
            metadata_json=None,
        )

        self.db.add(event)
        self.db.commit()

        return ticket

    def add_ticket_comment(
        self,
        ticket_number: str,
        comment: str,
        internal: bool = False,
    ) -> Ticket:
        ticket = self.get_ticket_by_number(ticket_number)

        if not ticket:
            raise TicketServiceError(f"Ticket not found: {ticket_number}")

        if self.settings.servicenow_mode == "real" and ticket.servicenow_sys_id:
            try:
                client = ServiceNowClient()

                if internal:
                    client.update_incident(
                        sys_id=ticket.servicenow_sys_id,
                        work_notes=comment,
                    )
                else:
                    client.update_incident(
                        sys_id=ticket.servicenow_sys_id,
                        comments=comment,
                    )

            except (ServiceNowConfigError, ServiceNowAPIError) as exc:
                logger.exception("ServiceNow ticket comment update failed")
                raise TicketServiceError(
                    f"ServiceNow ticket comment update failed: {exc}"
                ) from exc

        event = TicketEvent(
            ticket_id=ticket.id,
            event_type="comment_added",
            description=comment,
            metadata_json=None,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket


def get_or_create_user_for_ticket(
    db: Session,
    email: str,
) -> User:
    from app.models.database_models import UserRole

    user = db.query(User).filter(User.email == email).first()

    if user:
        return user

    user = User(
        email=email,
        name=email.split("@")[0],
        role=UserRole.employee,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user