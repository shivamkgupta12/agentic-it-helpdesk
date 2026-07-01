from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocumentResponse

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeDocumentResponse])
def list_knowledge_documents(db: Session = Depends(get_db)) -> list[KnowledgeDocument]:
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()