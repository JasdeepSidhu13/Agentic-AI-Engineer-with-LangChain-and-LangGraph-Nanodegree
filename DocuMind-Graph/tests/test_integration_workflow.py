from langchain_core.messages import AIMessage

from src.agent import create_workflow
from src.schemas import UpdateMemoryResponse, UserIntent


class StubLLM:
    """Minimal stub to satisfy structured outputs without real network calls."""

    def __init__(self):
        self.intent_output = UserIntent(
            intent_type="qa",
            confidence=0.9,
            reasoning="route to qa for testing",
        )
        self.memory_output = UpdateMemoryResponse(
            summary="Stubbed conversation summary",
            document_ids=["DOC-42"],
        )

    def with_structured_output(self, schema):
        output = self.intent_output if schema is UserIntent else self.memory_output

        class StructuredStub:
            def __init__(self, structured_output):
                self.structured_output = structured_output

            def invoke(self, _prompt):
                return self.structured_output

        return StructuredStub(output)

    def bind_tools(self, tools):  # noqa: ARG002 - part of the LLM interface
        return self


def test_workflow_routes_tools_and_updates_memory(monkeypatch):
    stub_llm = StubLLM()
    fake_tools_used = ["document_search"]

    def fake_invoke_react_agent(response_schema, messages, llm, tools):  # noqa: ARG002
        return {"messages": [AIMessage(content="Here is your answer")]}, fake_tools_used

    monkeypatch.setattr("src.agent.invoke_react_agent", fake_invoke_react_agent)

    workflow = create_workflow(stub_llm, tools=[])

    initial_state = {
        "messages": [],
        "user_input": "How much is the invoice?",
        "intent": None,
        "next_step": "classify_intent",
        "conversation_summary": "",
        "active_documents": [],
        "current_response": None,
        "tools_used": [],
        "session_id": "session-123",
        "user_id": "user-456",
        "actions_taken": [],
    }
    config = {
        "configurable": {
            "thread_id": "session-123",
            "llm": stub_llm,
            "tools": [],
        }
    }

    final_state = workflow.invoke(initial_state, config=config)

    assert final_state["actions_taken"] == [
        "classify_intent",
        "qa_agent",
        "update_memory",
    ]
    assert final_state["tools_used"] == fake_tools_used
    assert final_state["conversation_summary"] == "Stubbed conversation summary"
    assert final_state["active_documents"] == ["DOC-42"]
