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

For the full architecture design with diagrams, see [solution/agentic/design/architecture.md](solution/agentic/design/architecture.md).

## Getting Started

### Dependencies

- Python 3.11+
- OpenAI API key

### Installation

```bash
cd solution
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the `solution/` directory:

```
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://openai.vocareum.com/v1   # only if using Vocareum
```

### Database Setup

Run the setup notebooks in order:

1. **`solution/01_external_db_setup.ipynb`** - Sets up the CultPass external database (users, experiences, subscriptions, reservations)
2. **`solution/02_core_db_setup.ipynb`** - Sets up the UDA-Hub core database (accounts, knowledge base with 14 articles, sample ticket)

## Running

Open `solution/03_agentic_app.ipynb` and run all cells. The chat interface will start and you can interact with the agent.

Example queries:
- "I can't log in to my CultPass account"
- "Can you check my subscription status? My email is bob.stone@granite.com"
- "How do I reserve an experience?"
- "I need a refund for a cancelled event"

Type `quit` to exit the chat.

## Testing

Run `solution/04_test_cases.ipynb` to execute all 8 end-to-end test scenarios:

| Test | What's Validated |
|------|-----------------|
| 1. Login Issue Resolution | RAG search, confidence scoring, knowledge-based response |
| 2. Account/Subscription Lookup | `account_lookup` tool, database abstraction |
| 3. Escalation | Low confidence triggers escalation, human-ready summary |
| 4. Multi-turn Conversation | Short-term memory via `thread_id`, contextual follow-up |
| 5. Reservation Lookup | `reservation_lookup` tool |
| 6. Refund Processing | `process_refund` tool |
| 7. Long-term Memory | Cross-session memory persistence (store + retrieve) |
| 8. Error Handling | Graceful handling of invalid inputs |

## Project Structure

```
solution/
├── agentic/
│   ├── agents/          # 5 specialized agents
│   ├── design/          # Architecture documentation
│   ├── tools/           # DB tools, RAG pipeline, memory tools
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
- **4 Database Tools**: account_lookup, subscription_management, reservation_lookup, process_refund
- **Short-term Memory**: LangGraph MemorySaver checkpointer for multi-turn conversation continuity
- **Long-term Memory**: SQLite-based persistent memory for cross-session personalization
- **Escalation Logic**: Automatic escalation when RAG confidence < 0.6
- **Structured Logging**: All agent decisions, routing, and tool calls are logged

## Built With

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent graph orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [OpenAI gpt-4o-mini](https://platform.openai.com/) - Language model
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server for database tool abstraction
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
