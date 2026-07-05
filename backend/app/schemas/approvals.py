from datetime import datetime

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: str
    ticket_id: str | None = None
    conversation_id: str | None = None
    requested_by_user_id: str
    action_type: str
    reason: str
    status: str
    admin_comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ApprovalDecisionRequest(BaseModel):
    admin_comment: str | None = None


class ApprovalDecisionResponse(BaseModel):
    approval_id: str
    status: str
    message: str
    ticket_id: str | None = None
    ticket_number: str | None = None