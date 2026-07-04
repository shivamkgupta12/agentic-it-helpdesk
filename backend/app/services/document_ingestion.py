import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.models.database_models import KnowledgeDocument
from app.services.vector_store import add_documents_to_vector_store, reset_vector_store

logger = logging.getLogger(__name__)


DEFAULT_KB_PATH = Path("../sample-knowledge-base")


def infer_title_from_filename(path: Path) -> str:
    title = path.stem.replace("-", " ").replace("_", " ").title()

    replacements = {
        "Vpn": "VPN",
        "It": "IT",
        "Mfa": "MFA",
        "Ai": "AI",
        "Kb": "KB",
        "Outlook Teams": "Outlook and Teams",
    }

    for old, new in replacements.items():
        title = title.replace(old, new)

    return title


def load_markdown_documents(kb_path: Path = DEFAULT_KB_PATH) -> list[Document]:
    """
    Loads markdown files from the sample knowledge base folder.
    """

    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base path not found: {kb_path}")

    documents: list[Document] = []

    for file_path in sorted(kb_path.glob("*.md")):
        title = infer_title_from_filename(file_path)
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "title": title,
                    "source": str(file_path),
                    "filename": file_path.name,
                },
            )
        )

    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Splits documents into chunks suitable for RAG.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{chunk.metadata.get('filename', 'doc')}-{index}"

    return chunks


def sync_knowledge_document_rows(
    db: Session,
    documents: list[Document],
    chunk_count: int,
) -> None:
    """
    Stores metadata in the relational database.

    For MVP simplicity, this clears existing KB metadata and recreates it.
    ChromaDB stores the actual chunks and embeddings.
    """

    db.query(KnowledgeDocument).delete()

    chunk_count_by_filename: dict[str, int] = {}

    for document in documents:
        filename = document.metadata["filename"]
        chunk_count_by_filename[filename] = 0

    for filename in chunk_count_by_filename:
        matching_chunks = [
            chunk
            for chunk in range(chunk_count)
        ]
        _ = matching_chunks

    # Simpler and more useful: calculate by source documents after chunking externally.
    for document in documents:
        filename = document.metadata["filename"]
        title = document.metadata["title"]

        row = KnowledgeDocument(
            filename=filename,
            title=title,
            source_type="sample",
            status="indexed",
            chunk_count=0,
        )

        db.add(row)

    db.commit()


def reindex_sample_knowledge_base(db: Session) -> dict:
    """
    Rebuilds ChromaDB from sample markdown files.
    """

    source_documents = load_markdown_documents()
    chunks = chunk_documents(source_documents)

    reset_vector_store()
    added_count = add_documents_to_vector_store(chunks)

    db.query(KnowledgeDocument).delete()

    for source_doc in source_documents:
        filename = source_doc.metadata["filename"]
        title = source_doc.metadata["title"]

        chunk_count_for_doc = sum(
            1 for chunk in chunks if chunk.metadata.get("filename") == filename
        )

        row = KnowledgeDocument(
            filename=filename,
            title=title,
            source_type="sample",
            status="indexed",
            chunk_count=chunk_count_for_doc,
        )

        db.add(row)

    db.commit()

    return {
        "source_document_count": len(source_documents),
        "chunk_count": added_count,
    }