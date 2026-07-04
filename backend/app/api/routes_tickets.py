from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Ticket
from app.schemas.tickets import (
    TicketCreate,
    TicketDetailResponse,
    TicketResponse,
    TicketStatusResponse,
    TicketUpdate,
)
from app.services.ticket_service import (
    TicketCreateInput,
    TicketService,
    TicketServiceError,
    get_or_create_user_for_ticket,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(
    user_email: str | None = None,
    db: Session = Depends(get_db),
) -> list[Ticket]:
    query = db.query(Ticket)

    if user_email:
        user = get_or_create_user_for_ticket(db, user_email)
        query = query.filter(Ticket.user_id == user.id)

    return query.order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    return ticket


@router.post("", response_model=TicketResponse)
def create_ticket(
    request: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    user = get_or_create_user_for_ticket(db, request.user_email)

    service = TicketService(db)

    try:
        ticket = service.create_ticket(
            TicketCreateInput(
                user_id=user.id,
                conversation_id=request.conversation_id,
                title=request.title,
                description=request.description,
                category=request.category,
                priority=request.priority,
                urgency=request.urgency,
            )
        )

        return ticket

    except TicketServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    request: TicketUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    service = TicketService(db)

    try:
        return service.update_ticket(
            ticket=ticket,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            urgency=request.urgency,
            status=request.status,
        )

    except TicketServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status/{ticket_number}", response_model=TicketStatusResponse)
def get_ticket_status(
    ticket_number: str,
    db: Session = Depends(get_db),
) -> dict:
    service = TicketService(db)

    try:
        return service.get_ticket_status(ticket_number)

    except TicketServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc