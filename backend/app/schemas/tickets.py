from datetime import datetime

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    user_email: str = "employee@example.com"
    conversation_id: str | None = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    category: str = "General IT Query"
    priority: str = "Medium"
    urgency: str = "Medium"


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None
    urgency: str | None = None
    status: str | None = None


class TicketStatusResponse(BaseModel):
    ticket_number: str
    status: str
    category: str
    priority: str
    urgency: str
    latest_update: str | None = None


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
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TicketDetailResponse(TicketResponse):
    servicenow_sys_id: str | None = None
    conversation_id: str | None = None