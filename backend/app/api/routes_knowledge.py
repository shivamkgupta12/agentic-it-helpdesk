from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocumentResponse
from app.services.document_ingestion import reindex_sample_knowledge_base
from app.services.vector_store import VectorStoreError

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeDocumentResponse])
def list_knowledge_documents(db: Session = Depends(get_db)) -> list[KnowledgeDocument]:
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()


@router.post("/reindex")
def reindex_knowledge_base(db: Session = Depends(get_db)) -> dict:
    """
    Rebuilds the local ChromaDB index from sample markdown documents.
    """

    try:
        result = reindex_sample_knowledge_base(db)

        return {
            "status": "success",
            **result,
        }

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except VectorStoreError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reindex failed: {exc}") from exc


@router.delete("/{document_id}")
def delete_knowledge_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    MVP delete: removes document metadata row.

    Full vector deletion can be added later using stored chunk IDs.
    """

    document = (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    db.delete(document)
    db.commit()

    return {
        "status": "deleted",
        "document_id": document_id,
    }