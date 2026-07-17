from __future__ import annotations

import os
from pathlib import Path

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge"


class KnowledgeRetriever:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.vectors: list[list[float]] = []
        self._load()

    def _load(self) -> None:
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            text = path.read_text()
            for chunk in splitter.split_text(text):
                self.chunks.append(chunk)
                self.sources.append(path.name)
        if self.chunks:
            self.vectors = self.embeddings.embed_documents(self.chunks)

    def search(self, query: str, k: int = 3) -> list[dict]:
        if not self.chunks:
            return []
        query_vec = self.embeddings.embed_query(query)
        scored = []
        for idx, vec in enumerate(self.vectors):
            score = _cosine_similarity(query_vec, vec)
            scored.append((score, idx))
        scored.sort(reverse=True)
        results = []
        for score, idx in scored[:k]:
            results.append(
                {
                    "source": self.sources[idx],
                    "content": self.chunks[idx],
                    "score": round(score, 4),
                }
            )
        return results


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


_RETRIEVER: KnowledgeRetriever | None = None


def get_retriever() -> KnowledgeRetriever:
    global _RETRIEVER
    if _RETRIEVER is None:
        _RETRIEVER = KnowledgeRetriever()
    return _RETRIEVER


@tool
def retrieve_domain_knowledge(query: str) -> str:
    """Retrieve relevant battery operations and market trading knowledge passages."""
    import json

    results = get_retriever().search(query)
    return json.dumps({"results": results})
