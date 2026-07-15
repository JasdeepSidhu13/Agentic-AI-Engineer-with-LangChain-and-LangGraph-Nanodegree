# Agentic AI Engineer with LangChain and LangGraph Nanodegree

Author: Jasdeep Sidhu

This repository consolidates three agentic AI projects built while working through
LangChain and LangGraph workflows. Each project remains in its own top-level
directory so it can be explored, installed, and run independently.

## Repository Contents

| Project | Directory | Focus |
| --- | --- | --- |
| DocuMind Graph | [`DocuMind-Graph/`](DocuMind-Graph/) | Multi-agent document assistant for question answering, summarization, and document-based calculations. |
| EcoHome Agent | [`EcoHome-Agent/`](EcoHome-Agent/) | Energy optimization advisor that combines smart-home data, retrieval, and tool-based recommendations. |
| UDA-Hub | [`Uda-Hub/`](Uda-Hub/) | Customer support supervisor system for classifying, routing, resolving, and escalating support tickets. |

## High-Level Structure

```text
.
├── DocuMind-Graph/
│   ├── main.py
│   ├── requirements.txt
│   ├── src/
│   ├── tests/
│   └── README.md
├── EcoHome-Agent/
│   ├── 01_db_setup.ipynb
│   ├── 02_rag_setup.ipynb
│   ├── 03_run_and_evaluate.ipynb
│   ├── agent.py
│   ├── tools.py
│   ├── models/
│   ├── data/
│   └── README.md
├── Uda-Hub/
│   ├── requirements.txt
│   ├── README.md
│   └── solution/
│       ├── 01_external_db_setup.ipynb
│       ├── 02_core_db_setup.ipynb
│       ├── 03_agentic_app.ipynb
│       ├── 04_test_cases.ipynb
│       ├── agentic/
│       ├── data/
│       └── README.md
└── README.md
```

## Project Summaries

### DocuMind Graph

DocuMind Graph is a document-processing assistant that uses LangGraph to route
user requests to specialized agents. It supports:

- Intent classification for document questions, summaries, calculations, and
  fallback handling.
- Structured response models with Pydantic.
- Session-aware interactions backed by saved JSON session state.
- Retrieval and document tools for locating source material.
- Tests for retrieval behavior, prompts, tools, and integration flow.

Start with [`DocuMind-Graph/README.md`](DocuMind-Graph/README.md) for the full
project documentation.

### EcoHome Agent

EcoHome Agent is an AI energy advisor for smart-home customers. It combines
weather inputs, pricing information, usage history, and retrieval over best
practice documents to recommend lower-cost and lower-impact energy behavior.

Core capabilities include:

- Energy usage and solar generation modeling.
- Retrieval-augmented recommendations from energy tips documents.
- Tool-based reasoning for weather, pricing, usage, solar production, and
  savings calculations.
- Notebook-driven setup, retrieval configuration, execution, and evaluation.

Start with [`EcoHome-Agent/README.md`](EcoHome-Agent/README.md) before running
the notebooks.

### UDA-Hub

UDA-Hub is a multi-agent customer support system for CultPass, a cultural
experience subscription platform. It uses a supervisor pattern to coordinate
specialist agents.

Core capabilities include:

- Ticket classification by category, urgency, and complexity.
- RAG-based knowledge retrieval for support answers.
- Account, subscription, reservation, and refund tools through the project tool
  layer.
- Human escalation when confidence is low.
- Short-term and long-term memory patterns for customer support context.

Start with [`Uda-Hub/README.md`](Uda-Hub/README.md), then continue into
[`Uda-Hub/solution/README.md`](Uda-Hub/solution/README.md) for the runnable
solution details.

## Prerequisites

The projects are Python-based and rely on notebooks, LangChain, LangGraph, and
OpenAI-compatible model APIs.

Recommended baseline:

- Python 3.11 for UDA-Hub and EcoHome Agent.
- Python 3.9 or newer for DocuMind Graph.
- `pip` for dependency installation.
- Jupyter or an editor capable of running `.ipynb` notebooks.
- An OpenAI API key or an OpenAI-compatible endpoint where required by the
  project-specific README files.

## Setup

Each project has its own dependency file. Create a separate virtual environment
per project to avoid package version conflicts.

### DocuMind Graph

```bash
cd DocuMind-Graph
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp example.env .env
```

Add the required API key values to `DocuMind-Graph/.env`, then run:

```bash
python main.py
```

### EcoHome Agent

```bash
cd EcoHome-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the credentials described in
[`EcoHome-Agent/README.md`](EcoHome-Agent/README.md). Run the notebooks in order:

1. `01_db_setup.ipynb`
2. `02_rag_setup.ipynb`
3. `03_run_and_evaluate.ipynb`

### UDA-Hub

```bash
cd Uda-Hub/solution
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp example.env .env
```

Add the required API key values to `Uda-Hub/solution/.env`, then run the
notebooks in order:

1. `01_external_db_setup.ipynb`
2. `02_core_db_setup.ipynb`
3. `03_agentic_app.ipynb`
4. `04_test_cases.ipynb`

## Testing

Testing is project-specific:

- DocuMind Graph includes a `tests/` directory. After installing dependencies,
  run `pytest` from `DocuMind-Graph/`.
- EcoHome Agent uses notebook-based setup and evaluation in
  `03_run_and_evaluate.ipynb`.
- UDA-Hub validates its support workflows through
  `Uda-Hub/solution/04_test_cases.ipynb`.

Because these projects use LLM calls, API keys and compatible endpoints may be
required for complete end-to-end runs.

## Common Technologies

Across the three projects, the main technologies include:

- LangChain for LLM application components and tool integration.
- LangGraph for stateful and multi-agent workflow orchestration.
- Pydantic for structured models and validated responses.
- SQLAlchemy and SQLite for local data modeling and storage.
- ChromaDB or retrieval utilities for RAG workflows where applicable.
- Jupyter notebooks for setup, experimentation, and evaluation.

## Environment Files and Secrets

Do not commit real API keys, tokens, or credentials. Use each project's sample
environment file as a template and keep local `.env` files private.

Expected environment values may include:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `VOCAREUM_API_KEY`

Review each project README for the exact variables it expects.

## Notes for Reviewers

- The three projects are intentionally kept as separate directories because they
  have independent dependencies, data setup steps, and execution flows.
- Project-level README files remain in place for detailed instructions.
- The root README provides a unified entry point for navigating the full
  repository.

## Ownership

This repository and the consolidated project structure are maintained by
Jasdeep Sidhu.
