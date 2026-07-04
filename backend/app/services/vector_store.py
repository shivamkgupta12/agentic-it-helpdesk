import logging
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreError(RuntimeError):
    """Raised when vector store operations fail."""


def get_embeddings() -> AzureOpenAIEmbeddings:
    settings = get_settings()

    if not settings.azure_openai_endpoint:
        raise VectorStoreError("AZURE_OPENAI_ENDPOINT is missing.")

    if not settings.azure_openai_api_key:
        raise VectorStoreError("AZURE_OPENAI_API_KEY is missing.")

    if not settings.azure_openai_embedding_deployment:
        raise VectorStoreError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT is missing.")

    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        azure_deployment=settings.azure_openai_embedding_deployment,
        openai_api_version=settings.azure_openai_api_version,
    )


def get_chroma_vector_store() -> Chroma:
    settings = get_settings()

    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )


def add_documents_to_vector_store(documents: list[Document]) -> int:
    if not documents:
        return 0

    vector_store = get_chroma_vector_store()
    vector_store.add_documents(documents)

    logger.info("Added %s chunks to ChromaDB.", len(documents))

    return len(documents)


def similarity_search(
    query: str,
    k: int = 4,
) -> list[Document]:
    vector_store = get_chroma_vector_store()

    return vector_store.similarity_search(
        query=query,
        k=k,
    )


def reset_vector_store() -> None:
    """
    Deletes and recreates the current Chroma collection.

    This is useful for MVP reindexing.
    """

    vector_store = get_chroma_vector_store()

    try:
        vector_store.reset_collection()
    except Exception as exc:
        logger.warning("Could not reset Chroma collection: %s", exc)
        raise VectorStoreError(str(exc)) from exc


def format_documents_as_context(documents: list[Document]) -> tuple[str, list[dict[str, Any]]]:
    """
    Converts retrieved documents into:
    - readable context for the LLM
    - source metadata for API response
    """

    context_blocks: list[str] = []
    sources: list[dict[str, Any]] = []

    for index, doc in enumerate(documents, start=1):
        title = doc.metadata.get("title", "Unknown document")
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", f"chunk-{index}")

        context_blocks.append(
            f"[Source {index}: {title}]\n"
            f"Source file: {source}\n"
            f"Content:\n{doc.page_content}"
        )

        sources.append(
            {
                "title": title,
                "source": source,
                "chunk_id": chunk_id,
            }
        )

    return "\n\n---\n\n".join(context_blocks), sources