import logging

from app.agents.state import AgentState
from app.agents.utils import add_trace_step
from app.services.vector_store import (
    VectorStoreError,
    format_documents_as_context,
    similarity_search,
)

logger = logging.getLogger(__name__)


def knowledge_retrieval_agent(state: AgentState) -> dict:
    """
    Retrieves relevant internal IT support knowledge base chunks.
    """

    user_message = state["user_message"]
    triage = state.get("triage")

    category = triage.category if triage else "General IT Query"

    query = f"{category}: {user_message}"

    try:
        documents = similarity_search(
            query=query,
            k=4,
        )

        context, sources = format_documents_as_context(documents)

        output_summary = (
            f"Retrieved {len(documents)} knowledge chunks for category={category}."
        )

        trace_update = add_trace_step(
            state=state,
            agent_name="Knowledge Retrieval Agent",
            input_summary=query,
            output_summary=output_summary,
            metadata={
                "source_count": len(sources),
                "sources": sources,
            },
        )

        return {
            "retrieved_context": context,
            "sources": sources,
            **trace_update,
        }

    except VectorStoreError as exc:
        logger.warning("Knowledge retrieval failed: %s", exc)

        trace_update = add_trace_step(
            state=state,
            agent_name="Knowledge Retrieval Agent",
            input_summary=query,
            output_summary="Knowledge retrieval failed. Continuing without RAG context.",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "retrieved_context": None,
            "sources": [],
            **trace_update,
        }

    except Exception as exc:
        logger.warning("Unexpected knowledge retrieval failure: %s", exc)

        trace_update = add_trace_step(
            state=state,
            agent_name="Knowledge Retrieval Agent",
            input_summary=query,
            output_summary="Unexpected retrieval failure. Continuing without RAG context.",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "retrieved_context": None,
            "sources": [],
            **trace_update,
        }