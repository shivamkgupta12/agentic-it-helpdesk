from datetime import datetime

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: str
    action_type: str
    reason: str
    status: str
    admin_comment: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ApprovalDecisionRequest(BaseModel):
    admin_comment: str | None = None