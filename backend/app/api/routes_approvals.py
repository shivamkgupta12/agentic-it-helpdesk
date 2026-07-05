from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Approval, ApprovalStatus
from app.schemas.approvals import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalResponse,
)
from app.services.approval_service import ApprovalService, ApprovalServiceError

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse])
def list_approvals(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Approval]:
    query = db.query(Approval)

    if status:
        try:
            status_enum = ApprovalStatus(status)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid approval status: {status}",
            ) from exc

        query = query.filter(Approval.status == status_enum)

    return query.order_by(Approval.created_at.desc()).all()


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(
    approval_id: str,
    db: Session = Depends(get_db),
) -> Approval:
    service = ApprovalService(db)

    try:
        return service.get_approval(approval_id)

    except ApprovalServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{approval_id}/approve", response_model=ApprovalDecisionResponse)
def approve_request(
    approval_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
) -> ApprovalDecisionResponse:
    service = ApprovalService(db)

    try:
        approval, ticket = service.approve(
            approval_id=approval_id,
            admin_comment=request.admin_comment,
        )

        return ApprovalDecisionResponse(
            approval_id=approval.id,
            status=approval.status.value,
            message="Approval request approved and ticket created.",
            ticket_id=ticket.id,
            ticket_number=ticket.ticket_number,
        )

    except ApprovalServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{approval_id}/reject", response_model=ApprovalDecisionResponse)
def reject_request(
    approval_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
) -> ApprovalDecisionResponse:
    service = ApprovalService(db)

    try:
        approval = service.reject(
            approval_id=approval_id,
            admin_comment=request.admin_comment,
        )

        return ApprovalDecisionResponse(
            approval_id=approval.id,
            status=approval.status.value,
            message="Approval request rejected.",
            ticket_id=None,
            ticket_number=None,
        )

    except ApprovalServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{approval_id}/request-more-info", response_model=ApprovalDecisionResponse)
def request_more_information(
    approval_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
) -> ApprovalDecisionResponse:
    service = ApprovalService(db)

    try:
        approval = service.request_more_information(
            approval_id=approval_id,
            admin_comment=request.admin_comment,
        )

        return ApprovalDecisionResponse(
            approval_id=approval.id,
            status=approval.status.value,
            message="More information requested from the user.",
            ticket_id=None,
            ticket_number=None,
        )

    except ApprovalServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc