from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentResponse(BaseModel):
    id: str
    filename: str
    title: str
    source_type: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }