from datetime import datetime

from pydantic import BaseModel


class TicketCreate(BaseModel):
    user_email: str = "employee@example.com"
    title: str
    description: str
    category: str = "General IT Query"
    priority: str = "Medium"
    urgency: str = "Medium"


class TicketResponse(BaseModel):
    id: str
    ticket_number: str | None
    title: str
    description: str
    category: str
    priority: str
    urgency: str
    status: str
    source: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }