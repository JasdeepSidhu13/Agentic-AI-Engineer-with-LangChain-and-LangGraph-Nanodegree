
# EcoHome Energy Advisor

An AI-powered energy optimization agent that helps customers reduce electricity costs and environmental impact through personalized recommendations.

## Project Overview

EcoHome is a smart-home energy solution that helps customers with solar panels, electric vehicles, and smart thermostats optimize their energy usage. The Energy Advisor agent provides precision recommendations on when to operate devices to minimize costs and reduce carbon footprints.

### Key Features

* **Weather Integration**: Utilizes hyper-local weather forecasts to predict solar generation potential.
* **Dynamic Pricing**: Analyzes real-time, time-of-day electricity pricing for cost optimization.
* **Historical Analysis**: Queries longitudinal energy usage patterns to generate tailored advice.
* **RAG Pipeline**: Leverages a Retrieval-Augmented Generation pipeline to surface evidence-based energy-saving best practices.
* **Multi-device Optimization**: Intelligently manages orchestration for EVs, HVAC, appliances, and solar systems.
* **Cost Calculations**: Provides granular savings estimates and ROI analysis.

## Project Structure

```text
ecohome_core/
├── models/
│   ├── __init__.py
│   └── energy.py              # Database models for energy infrastructure
├── data/
│   └── documents/
│       ├── tip_device_best_practices.txt
│       └── tip_energy_savings.txt
├── agent.py                   # Main Energy Advisor agent logic
├── tools.py                   # Agent tools (weather, pricing, database, RAG)
├── requirements.txt           # Python dependencies
├── 01_db_setup.ipynb          # Database schema initialization and data ingestion
├── 02_rag_setup.ipynb         # RAG pipeline configuration
├── 03_agent_evaluation.ipynb  # Agent performance validation
├── 04_agent_run.ipynb         # Production-ready agent execution
└── README.md                  # Project documentation

```

## Deployment Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt

```

### 2. Configure Environment

Create a `.env` file with the required API credentials:

```text
VOCAREUM_API_KEY=your_vocareum_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

```

### 3. Execution Workflow

Execute the modules in the following order:

1. **01_db_setup.ipynb**: Initializes the relational database and populates system data.
2. **02_rag_setup.ipynb**: Configures the vector store and RAG retrieval parameters.
3. **03_agent_evaluation.ipynb**: Conducts rigorous performance and accuracy testing.
4. **04_agent_run.ipynb**: Executes the agent within defined operational scenarios.

## Agent Capabilities

### Operational Tools

* **Weather Forecast**: Retrieves hourly predictions and solar irradiance levels.
* **Electricity Pricing**: Accesses time-of-day pricing indices.
* **Energy Usage Query**: Extracts historical consumption metrics.
* **Solar Generation Query**: Processes past solar production throughput.
* **Energy Tips Search**: Searches for optimized energy-saving protocols.
* **Savings Calculator**: Computes projected cost reductions and efficiency gains.

### Example Queries

* "When should I charge my electric vehicle tomorrow to minimize cost while maximizing solar self-consumption?"
* "What is the optimal thermostat setpoint for Wednesday afternoon given predicted electricity price spikes?"
* "Analyze my usage history and suggest three high-impact strategies to reduce energy overhead."
* "Quantify the potential savings of shifting dishwasher operation to off-peak hours."

## Technical Specifications

### Data Schema

| Table | Primary Data Points |
| --- | --- |
| **Energy Usage** | `timestamp`, `consumption_kwh`, `device_type`, `device_name`, `cost_usd` |
| **Solar Generation** | `timestamp`, `generation_kwh`, `weather_condition`, `temperature_c`, `solar_irradiance` |

### Core Technologies

* **LangChain**: Orchestration framework for agentic workflows and tool integration.
* **LangGraph**: Specialized agent state management.
* **ChromaDB**: High-performance vector database for efficient document retrieval.
* **SQLAlchemy**: Robust Object-Relational Mapping (ORM) for data management.
* **OpenAI**: Foundation for LLM reasoning and embedding generation.
* **SQLite**: Reliable, low-latency local storage.

## Performance Standards

The EcoHome Energy Advisor is held to the following standards:

* **Accuracy**: Precise extraction of data and error-free financial modeling.
* **Relevance**: Direct, contextual alignment between user queries and output.
* **Completeness**: Holistic, actionable advice.
* **Tool Utilization**: Efficient, logical invocation of external APIs and databases.
* **Reasoning**: Transparent, logical derivation of all optimization recommendations.

## Roadmap

* Integration of advanced, real-time demand-response algorithms.
* Implementation of expanded multi-modal data processing.
* Development of a real-time dashboard for enhanced user visualization.
