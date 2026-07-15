# Document Assistant Project

## Overview

This project implements a document-processing assistant using **LangChain** and **LangGraph**. The assistant is designed to handle multiple types of user requests over financial and healthcare documents by routing each request to a specialized agent instead of relying on a single generic chain.

The system supports three main capabilities:

- **Question Answering** over document content
- **Summarization** of documents with key point extraction
- **Calculations** based on values found in documents

The workflow is built as a **multi-agent graph** where user input is first classified by intent, then routed to the most appropriate task-specific node, and finally passed through a memory update step before the interaction ends.

---

## Features

- Multi-agent workflow built with **LangGraph**
- Intent-based routing for different user requests
- Structured outputs using **Pydantic** schemas
- Support for:
  - document question answering
  - document summarization
  - document-based calculations
- Conversation-aware behavior through session tracking
- File-backed session persistence for saved conversations
- Tool usage logging for observability and debugging

---

## Project Structure

```text
doc_assistant_project/
├── src/
│   ├── schemas.py        # Pydantic models and session schemas
│   ├── retrieval.py      # Document retrieval logic
│   ├── tools.py          # Tool definitions and logging
│   ├── prompts.py        # Prompt templates
│   ├── agent.py          # LangGraph workflow and state
│   └── assistant.py      # Main assistant/session management
├── sessions/             # Saved session JSON files
├── logs/                 # Tool usage logs
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

---

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

Clone the project and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
cp .env.example .env
```

Then add your OpenAI API key to `.env`.

---

## Running the Project

Start the assistant with:

```bash
python main.py
```

If you are using the Udacity workspace, make sure your API key is configured correctly before running the project.

---

## Agent Architecture

The assistant is implemented as a **LangGraph workflow** with specialized nodes:

- `classify_intent`
- `qa_agent`
- `summarization_agent`
- `calculation_agent`
- `update_memory`

### Workflow Logic

The graph starts at `classify_intent`, which analyzes the user request and returns a `UserIntent` object. Based on `intent_type`, the workflow routes to the appropriate node:

- `qa` → `qa_agent`
- `summarization` → `summarization_agent`
- `calculation` → `calculation_agent`
- `unknown` → defaults to `qa_agent`

After the selected task node completes, the workflow always moves to `update_memory`, then terminates.

This design is stronger than a single generic chain because each request type is handled by a dedicated node with a clearer responsibility.

### High-Level Flow

```text
User Input
   ↓
classify_intent
   ↓
 ┌───────────────┬────────────────────┬───────────────────┐
 ↓               ↓                    ↓
qa_agent   summarization_agent   calculation_agent
 └───────────────┴────────────────────┴───────────────────┘
                         ↓
                  update_memory
                         ↓
                        End
```

---

## Implementation Decisions

A key design decision in this project was to use **specialized routing** rather than one general-purpose response chain.

### Why this approach?

Different user requests require different behaviors:

- A **Q&A** request should retrieve relevant content and answer precisely
- A **summarization** request should condense information and extract key points
- A **calculation** request should identify numeric values and compute results safely

By classifying intent first and routing to a dedicated node, the system becomes:

- easier to reason about
- easier to extend
- more reliable for downstream processing
- better aligned with agentic workflow design patterns

This also makes the graph architecture explicit and easier to debug.

---

## State and Memory

The system uses both **graph state** and **session persistence**, but these serve different purposes.

### AgentState

The LangGraph workflow operates on an `AgentState` object with the following fields:

- `user_input`
- `messages`
- `intent`
- `next_step`
- `conversation_summary`
- `active_documents`
- `current_response`
- `tools_used`
- `session_id`
- `user_id`
- `actions_taken`

The `messages` field uses `add_messages`, allowing message history to accumulate across graph steps.

### Memory Design

This project uses two layers of memory:

#### 1. LangGraph runtime memory

The graph uses `InMemorySaver` to maintain state during execution. This allows the workflow to preserve context for a given `thread_id` while the application is running.

In this project, `process_message()` uses the `session_id` as the LangGraph `thread_id`.

Important limitation: this is **runtime memory only**. It is not durable storage by itself and should not be described as permanent graph persistence.

#### 2. File-backed session persistence

Separate from LangGraph memory, the `DocumentAssistant` class saves session data as JSON files under `./sessions`.

The `start_session()` method creates or resumes a session, and `process_message()` appends each interaction to the saved session history. This provides persistence across runs in a way that the in-memory graph checkpointer alone does not.

### Session Tracking

Conversation history is stored as structured records, and document context is also preserved between turns:

- conversation history is appended as `TurnRecord`
- document context is stored in `SessionState.document_context`

The `update_memory` node creates a structured summary and updates the active document list so future turns can use prior context more effectively.

---

## Structured Outputs

The project uses **Pydantic models** to enforce structured outputs across the workflow.

### Core Response Schemas

#### `UserIntent`
Represents the result of intent classification.

Fields:
- `intent_type`
- `confidence`
- `reasoning`

#### `AnswerResponse`
Represents a question-answering result.

Fields:
- `question`
- `answer`
- `sources`
- `confidence`
- `timestamp`

#### `SummarizationResponse`
Represents a summarization result.

Fields:
- `original_length`
- `summary`
- `key_points`
- `document_ids`
- `timestamp`

#### `CalculationResponse`
Represents a calculation result.

Fields:
- `expression`
- `result`
- `explanation`
- `units`
- `timestamp`

#### `UpdateMemoryResponse`
Represents the memory update output.

Fields:
- `summary`
- `document_ids`

#### `DocumentChunk`
Represents retrieved document content in structured form.

### Session and History Schemas

#### `MessageRecord`
A JSON-safe representation of a message.

#### `TurnRecord`
Stores one interaction turn with:
- `user_input`
- `messages`
- `intent`
- `active_documents`
- `tools_used`
- `actions_taken`
- `timestamp`

#### `SessionState`
Stores session-level data:
- `session_id`
- `user_id`
- `conversation_history`
- `document_context`
- timestamps

### Why structured outputs matter

Using Pydantic models improves the system in several ways:

- validates model outputs
- enforces consistent response formats
- makes downstream routing and storage more predictable
- reduces ambiguity when passing data between nodes

This is especially useful in multi-step agent workflows where each node depends on clean, structured state.

---

## Tools

The assistant uses several tools defined with `@tool`:

- `calculator`
- `document_search`
- `document_reader`
- `document_statistics`

### `calculator`
Performs mathematical calculations safely.

Implementation notes:
- validates expressions using regex
- uses restricted `eval`
- designed to reduce unsafe execution risk

### `document_search`
Searches documents using multiple strategies, including:

- keyword search
- type-based search
- amount-based search
- range-based search
- full search across all documents

This tool also logs usage for observability.

### `document_reader`
Reads document content for downstream processing.

### `document_statistics`
Extracts or computes document-level statistics.

Together, these tools allow the specialized agents to interact with document content in a modular way.

---

## Logging and Observability

The project includes a `ToolLogger` for recording tool usage.

Tool activity is written as JSON logs under:

```text
./logs
```

In the current implementation, the logger is initialized as:

```python
ToolLogger(logs_dir="./logs")
```

Because of this, logs are written as timestamped files such as:

```text
logs/tool_usage_<timestamp>.json
```

This means the current implementation does **not** automatically create per-session log files like `logs/session_<SESSION_ID>.json` unless the code is changed to do so.

This logging is useful for:

- debugging tool behavior
- tracing which tools were used
- improving observability during development

---

## Example Interactions

Some examples based on interactions from the project workflow.

### 1. Invoice Calculation

**User:** What’s the total amount in invoice INV-001?
**System behavior:**
- classified the request as `calculation`
- used `document_reader` to inspect the invoice
- used `calculator` to compute the total
- returned the result: **$22,000**
- updated memory with active document `INV-001`

### 2. Contract Summarization

**User:** Summarize all contracts.
**System behavior:**
- classified the request as `summarization`
- used `document_search` to identify relevant contract documents
- used `document_reader` to retrieve content
- summarized contract `CON-001`, including:
  - Service Agreement
  - total value of **$180,000**
  - duration of **12 months**
  - **60-day termination notice**

### 3. Multi-Document Calculation

**User:** Calculate the sum of all invoice totals.
**System behavior:**
- classified the request as `calculation`
- used `document_search` to find invoice documents
- used `document_reader` to retrieve invoice values
- used `calculator` to compute the combined total
- returned the result: **$305,800**
- referenced documents `INV-001`, `INV-002`, and `INV-003`


---

## Design Strengths

Some strengths of this implementation include:

- clear separation of responsibilities across graph nodes
- explicit intent-based routing
- structured outputs for reliability
- support for session continuity
- modular tool design
- improved maintainability compared with a monolithic chain

---

## Limitations

This implementation also has some limitations:

- LangGraph memory is only in-memory during runtime
- long-term persistence depends on separate JSON session storage
- intent classification quality depends on model performance
- calculation behavior is limited to the supported parsing and tool logic
- the system can be extended further with stronger retrieval and evaluation methods

---

## Future Improvements

Possible next steps for improving the project include:

- replacing in-memory graph checkpointing with a more durable backend
- improving retrieval quality with embeddings or hybrid search
- adding stronger evaluation and observability workflows
- introducing better document chunk ranking
- expanding support for more document types and more advanced calculations
- creating per-session logging for easier traceability

---

## Conclusion

This project demonstrates how LangGraph can be used to build a structured multi-agent document assistant with specialized routing, tool use, session tracking, and structured outputs.

Instead of treating every request the same way, the system first identifies user intent and then routes the request to the most appropriate agent node. This makes the assistant more modular, easier to maintain, and better suited for handling different document-processing tasks in a reliable way.
