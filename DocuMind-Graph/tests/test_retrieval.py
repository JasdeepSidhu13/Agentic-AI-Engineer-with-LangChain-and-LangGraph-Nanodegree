import pytest
from pytest import approx

from src.retrieval import SimulatedRetriever


def test_retrieve_by_keyword_matches_title_and_metadata(retriever):
    results = retriever.retrieve_by_keyword("acme")

    assert results
    ids = [chunk.doc_id for chunk in results]
    assert "INV-001" in ids


def test_retrieve_by_amount_range_filters_and_orders(retriever):
    results = retriever.retrieve_by_amount_range(min_amount=100000)

    ids = [chunk.doc_id for chunk in results]
    assert ids == ["INV-003", "CON-001"]


def test_retrieve_by_exact_amount_matches_within_tolerance(retriever):
    results = retriever.retrieve_by_exact_amount(2450)

    assert len(results) == 1
    assert results[0].doc_id == "CLM-001"


def test_parse_and_retrieve_by_amount_understands_over_keyword(retriever):
    results = retriever._parse_and_retrieve_by_amount("Show invoices over $200,000")

    assert results
    assert results[0].doc_id == "INV-003"


def test_get_statistics_calculates_amounts(retriever):
    stats = retriever.get_statistics()

    assert stats["total_documents"] == 5
    assert stats["documents_with_amounts"] == 4
    assert stats["total_amount"] == approx(466250)
    assert stats["average_amount"] == approx(116562.5)
    assert stats["min_amount"] == approx(2450)
    assert stats["max_amount"] == approx(214500)
    assert stats["document_types"]["invoice"] == 3
