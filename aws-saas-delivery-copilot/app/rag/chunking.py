from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    tenant_id: str
    source_file: str
    chunk_id: str
    text: str


def chunk_text(
    text: str,
    tenant_id: str,
    source_file: str,
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized_text = " ".join(text.split())
    if not normalized_text:
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(normalized_text):
        end = min(start + chunk_size, len(normalized_text))
        chunk_body = normalized_text[start:end].strip()
        if chunk_body:
            chunks.append(
                TextChunk(
                    tenant_id=tenant_id,
                    source_file=source_file,
                    chunk_id=f"{source_file}:{index}",
                    text=chunk_body,
                )
            )

        if end == len(normalized_text):
            break

        start = end - overlap
        index += 1

    return chunks
