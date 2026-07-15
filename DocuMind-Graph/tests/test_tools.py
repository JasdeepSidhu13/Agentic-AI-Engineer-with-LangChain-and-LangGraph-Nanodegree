from src.tools import (
    create_calculator_tool,
    create_document_search_tool,
    create_document_reader_tool,
    create_document_statistics_tool,
)


def test_calculator_tool_logs_and_returns_result(logger):
    calculator = create_calculator_tool(logger)

    result = calculator.invoke({"expression": "2 + 3 * 4"})

    assert result == "14"
    assert logger.logs[-1]["tool_name"] == "calculator"
    assert "'result': '14'" in logger.logs[-1]["output"]


def test_calculator_tool_handles_invalid_input(logger):
    calculator = create_calculator_tool(logger)

    result = calculator.invoke({"expression": "2 + not_a_number"})

    assert result.startswith("Error evaluating expression")
    assert "'error':" in logger.logs[-1]["output"]


def test_document_search_filters_by_type_and_amount(retriever, logger):
    search_tool = create_document_search_tool(retriever, logger)

    output = search_tool.invoke({
        "query": "high invoices",
        "search_type": "type",
        "doc_type": "invoice",
        "comparison": "over",
        "amount": 100000,
    })

    assert "INV-003" in output
    assert "INV-002" not in output
    assert logger.logs[-1]["tool_name"] == "document_search"


def test_document_search_all_returns_everything(retriever, logger):
    search_tool = create_document_search_tool(retriever, logger)

    output = search_tool.invoke({
        "query": "invoices",
        "search_type": "all",
    })

    assert "Found 5 document(s)" in output
    assert "CON-001" in output
    assert "CLM-001" in output
    assert "'results_count': 5" in logger.logs[-1]["output"]
    assert logger.logs[-1]["tool_name"] == "document_search"


def test_document_reader_returns_full_content(retriever, logger):
    reader_tool = create_document_reader_tool(retriever, logger)

    content = reader_tool.invoke({"doc_id": "INV-002"})

    assert "Document INV-002" in content
    assert logger.logs[-1]["tool_name"] == "document_reader"


def test_document_reader_handles_missing_id(retriever, logger):
    reader_tool = create_document_reader_tool(retriever, logger)

    content = reader_tool.invoke({"doc_id": "MISSING-ID"})

    assert "not found" in content.lower()
    assert logger.logs[-1]["tool_name"] == "document_reader"


def test_document_statistics_summarizes_collection(retriever, logger):
    stats_tool = create_document_statistics_tool(retriever, logger)

    summary = stats_tool.invoke({})

    assert "Total Documents: 5" in summary
    assert "Documents with Amounts: 4" in summary
    assert logger.logs[-1]["tool_name"] == "document_statistics"
