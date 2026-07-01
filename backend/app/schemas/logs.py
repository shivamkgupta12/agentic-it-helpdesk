from datetime import datetime

from pydantic import BaseModel


class AgentLogResponse(BaseModel):
    id: str
    conversation_id: str | None
    agent_name: str
    input_summary: str | None
    output_summary: str | None
    metadata_json: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }