import pytest

from src.retrieval.rag import _cosine_similarity


def test_cosine_similarity_identical():
    vec = [1.0, 0.0, 0.0]
    assert _cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert _cosine_similarity(a, b) == pytest.approx(0.0)
