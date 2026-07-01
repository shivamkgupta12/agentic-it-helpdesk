from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import AgentLog
from app.schemas.logs import AgentLogResponse

router = APIRouter(prefix="/agent-logs", tags=["agent-logs"])


@router.get("", response_model=list[AgentLogResponse])
def list_agent_logs(db: Session = Depends(get_db)) -> list[AgentLog]:
    return db.query(AgentLog).order_by(AgentLog.created_at.desc()).all()