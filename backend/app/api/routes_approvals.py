from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Approval
from app.schemas.approvals import ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse])
def list_approvals(db: Session = Depends(get_db)) -> list[Approval]:
    return db.query(Approval).order_by(Approval.created_at.desc()).all()