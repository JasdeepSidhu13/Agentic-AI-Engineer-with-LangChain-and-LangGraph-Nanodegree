import pytest

from src.retrieval import SimulatedRetriever
from src.tools import ToolLogger


@pytest.fixture
def retriever():
    return SimulatedRetriever()


@pytest.fixture
def logger(tmp_path):
    logs_dir = tmp_path / "logs"
    return ToolLogger(logs_dir=str(logs_dir))
