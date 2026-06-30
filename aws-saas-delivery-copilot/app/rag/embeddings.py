import hashlib
import math
import re
from collections import Counter


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


class HashingEmbedder:
    """Small local embedding fallback for Stage 2.

    This is intentionally API-key free and dependency-light. It can be replaced
    later by Bedrock embeddings or sentence-transformers without changing the
    RAG service contract.
    """

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = tokenize(text)
        counts = Counter(tokens)

        for token, count in counts.items():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign * float(count)

        return normalize(vector)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right))
