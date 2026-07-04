from pathlib import Path

from langchain_core.documents import Document

from app.services.document_ingestion import chunk_documents, infer_title_from_filename


def test_infer_title_from_filename() -> None:
    title = infer_title_from_filename(Path("vpn-troubleshooting-guide.md"))

    assert title == "Vpn Troubleshooting Guide"


def test_chunk_documents_creates_chunks() -> None:
    documents = [
        Document(
            page_content=(
                "# VPN Troubleshooting Guide\n\n"
                "VPN disconnects frequently. Restart VPN client. Check MFA."
            ),
            metadata={
                "title": "VPN Troubleshooting Guide",
                "filename": "vpn-troubleshooting-guide.md",
                "source": "sample",
            },
        )
    ]

    chunks = chunk_documents(documents)

    assert len(chunks) >= 1
    assert chunks[0].metadata["filename"] == "vpn-troubleshooting-guide.md"
    assert "chunk_id" in chunks[0].metadata