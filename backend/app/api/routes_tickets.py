from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Ticket
from app.schemas.tickets import TicketResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()