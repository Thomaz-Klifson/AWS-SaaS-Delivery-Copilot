import json
from pathlib import Path
from typing import Any

from app.core.tenant_loader import PROJECT_ROOT
from app.rag.chunking import TextChunk
from app.rag.embeddings import HashingEmbedder, cosine_similarity


STORE_ROOT = PROJECT_ROOT / ".local" / "vector_store"


class LocalVectorStore:
    def __init__(self, store_root: Path = STORE_ROOT, embedder: HashingEmbedder | None = None):
        self.store_root = store_root
        self.embedder = embedder or HashingEmbedder()

    def index_chunks(self, tenant_id: str, chunks: list[TextChunk]) -> int:
        self.store_root.mkdir(parents=True, exist_ok=True)
        records = []

        for chunk in chunks:
            records.append(
                {
                    "tenant_id": chunk.tenant_id,
                    "source_file": chunk.source_file,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "embedding": self.embedder.embed(chunk.text),
                }
            )

        self._tenant_store_path(tenant_id).write_text(
            json.dumps(records, indent=2),
            encoding="utf-8",
        )
        return len(records)

    def search(self, tenant_id: str, question: str, top_k: int = 3) -> list[dict[str, Any]]:
        records = self._load_tenant_records(tenant_id)
        if not records:
            return []

        query_embedding = self.embedder.embed(question)
        ranked = []
        for record in records:
            score = cosine_similarity(query_embedding, record["embedding"])
            ranked.append(
                {
                    "tenant_id": record["tenant_id"],
                    "source_file": record["source_file"],
                    "chunk_id": record["chunk_id"],
                    "text": record["text"],
                    "score": score,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:top_k]

    def _load_tenant_records(self, tenant_id: str) -> list[dict[str, Any]]:
        store_path = self._tenant_store_path(tenant_id)
        if not store_path.exists():
            return []

        return json.loads(store_path.read_text(encoding="utf-8"))

    def _tenant_store_path(self, tenant_id: str) -> Path:
        return self.store_root / f"{tenant_id}.json"
