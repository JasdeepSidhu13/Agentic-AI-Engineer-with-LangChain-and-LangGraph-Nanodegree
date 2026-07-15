# UDA-Hub - Universal Decision Agent for Customer Support

A multi-agent customer support system built with LangGraph that intelligently resolves support tickets for CultPass, a cultural experience subscription platform.

## Architecture

UDA-Hub follows a **Supervisor pattern** with 5 specialized agents:

| Agent | Role |
|-------|------|
| **Supervisor** | Central orchestrator that routes tickets to the right specialist |
| **Classifier** | Analyzes ticket content to determine category, urgency, and complexity |
| **Resolver** | Searches knowledge base via RAG to answer questions |
| **Account Agent** | Performs CultPass database operations (account lookup, subscription management, refunds, reservations) |
| **Escalation** | Escalates to human support when confidence is low |

For the full architecture design with diagrams, see [agentic/design/architecture.md](agentic/design/architecture.md).

## Setup

### Prerequisites
- Python 3.11+
- OpenAI API key

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the `solution/` directory:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### Database Setup

Run the setup notebooks in order:

1. **`01_external_db_setup.ipynb`** - Sets up the CultPass external database (users, experiences, subscriptions, reservations)
2. **`02_core_db_setup.ipynb`** - Sets up the UDA-Hub core database (accounts, knowledge base with 14 articles, sample ticket)

## Running

### Interactive Chat

Open `03_agentic_app.ipynb` and run all cells. The chat interface will start and you can interact with the agent.

Example queries:
- "I can't log in to my CultPass account"
- "Can you check my subscription status? My email is bob.stone@granite.com"
- "How do I reserve an experience?"
- "I need a refund for a cancelled event"

### Test Cases

Run `04_test_cases.ipynb` to execute all 8 test scenarios:

1. Login issue resolution (RAG)
2. Account/subscription lookup (tool usage)
3. Escalation (low confidence)
4. Multi-turn conversation (short-term memory)
5. Reservation lookup (tool usage)
6. Refund processing (tool usage)
7. Long-term memory across sessions
8. Error handling

## Project Structure

```
solution/
├── agentic/
│   ├── agents/          # 5 specialized agents
│   ├── design/          # Architecture documentation
│   ├── tools/           # MCP tools, RAG pipeline, memory tools
│   ├── state.py         # AgentState TypedDict
│   ├── prompts.py       # All agent system prompts
│   └── workflow.py      # LangGraph StateGraph (the orchestrator)
├── data/
│   ├── core/            # UDA-Hub database (generated)
│   ├── external/        # CultPass data files and database (generated)
│   └── models/          # SQLAlchemy ORM models
├── 01_external_db_setup.ipynb
├── 02_core_db_setup.ipynb
├── 03_agentic_app.ipynb
├── 04_test_cases.ipynb
├── utils.py
└── requirements.txt
```

## Key Features

- **RAG-based Knowledge Retrieval**: Embedding-based similarity search over 14 knowledge base articles with confidence scoring
- **4 Database Tools** (via FastMCP): account_lookup, subscription_management, reservation_lookup, process_refund
- **Short-term Memory**: LangGraph MemorySaver checkpointer for multi-turn conversation continuity
- **Long-term Memory**: SQLite-based persistent memory for cross-session personalization
- **Escalation Logic**: Automatic escalation when RAG confidence < 0.6
- **Structured Logging**: All agent decisions, routing, and tool calls are logged

## Dependencies

See [requirements.txt](requirements.txt) for the full list. Key packages:
- `langgraph` - Multi-agent graph orchestration
- `langchain-openai` - OpenAI LLM integration
- `fastmcp` - MCP server for database tools
- `sqlalchemy` - Database ORM
