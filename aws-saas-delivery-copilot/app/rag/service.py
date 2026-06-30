from pathlib import Path

from app.core.tenant_loader import PROJECT_ROOT, get_tenant_path, read_documents
from app.models.schemas import RagAskResponse, RagIngestResponse, RagSource, RetrievedChunk
from app.rag.chunking import TextChunk, chunk_text
from app.rag.vector_store import LocalVectorStore


DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120


def ingest_tenant_documents(tenant_id: str) -> RagIngestResponse:
    chunks = _load_tenant_document_chunks(tenant_id)
    indexed_count = LocalVectorStore().index_chunks(tenant_id, chunks)

    return RagIngestResponse(
        tenant_id=tenant_id,
        document_count=len({chunk.source_file for chunk in chunks}),
        chunk_count=indexed_count,
        indexed_files=sorted({chunk.source_file for chunk in chunks}),
    )


def ask_tenant_question(tenant_id: str, question: str, top_k: int = 3) -> RagAskResponse:
    safe_top_k = max(1, min(top_k, 10))
    matches = LocalVectorStore().search(tenant_id, question, safe_top_k)

    if not matches:
        ingest_tenant_documents(tenant_id)
        matches = LocalVectorStore().search(tenant_id, question, safe_top_k)

    retrieved_chunks = [
        RetrievedChunk(
            source_file=match["source_file"],
            chunk_id=match["chunk_id"],
            text=match["text"],
            score=round(float(match["score"]), 4),
        )
        for match in matches
    ]
    sources = _unique_sources(retrieved_chunks)

    return RagAskResponse(
        answer=_build_extractive_answer(retrieved_chunks),
        tenant_id=tenant_id,
        question=question,
        sources=sources,
        retrieved_chunks=retrieved_chunks,
        top_k=safe_top_k,
    )


def _load_tenant_document_chunks(tenant_id: str) -> list[TextChunk]:
    documents = read_documents(tenant_id)
    chunks = []
    tenant_path = get_tenant_path(tenant_id)

    for document in documents:
        document_path = tenant_path / "documents" / document.file_name
        text = _read_text_file(document_path)
        chunks.extend(
            chunk_text(
                text=text,
                tenant_id=tenant_id,
                source_file=document.file_name,
                chunk_size=DEFAULT_CHUNK_SIZE,
                overlap=DEFAULT_CHUNK_OVERLAP,
            )
        )

    return chunks


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _unique_sources(chunks: list[RetrievedChunk]) -> list[RagSource]:
    sources = []
    seen = set()

    for chunk in chunks:
        if chunk.source_file in seen:
            continue
        seen.add(chunk.source_file)
        sources.append(
            RagSource(
                source_file=chunk.source_file,
                chunk_id=chunk.chunk_id,
                score=chunk.score,
            )
        )

    return sources


def _build_extractive_answer(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return (
            "No local evidence was found for this tenant. Run ingestion and check "
            "whether tenant documents exist."
        )

    excerpts = [chunk.text for chunk in chunks[:2]]
    joined_excerpts = " ".join(excerpts)
    return (
        "Extractive draft answer based only on retrieved local sources. "
        f"{joined_excerpts}"
    )
