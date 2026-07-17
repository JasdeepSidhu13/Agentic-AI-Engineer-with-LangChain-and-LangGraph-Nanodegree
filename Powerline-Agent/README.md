# Powerline Battery Performance Agent

LLM-powered agent that analyzes one week of battery interval data, compares **historical operation** vs **perfect foresight**, and produces actionable trading recommendations — using tools, not raw data in the prompt.

## How to Run

```bash
cd Powerline-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp example.env .env        # add your OPENAI_API_KEY
python main.py
```

Optional flags:

```bash
python main.py --data path/to/data.csv
python main.py --prompt "Your custom analysis question"
python main.py --output example_output.md
```

Run tests:

```bash
python -m pytest tests/ -q
```

## High-Level Approach

1. **Load data** — CSV is normalized via a schema adapter so the same code works on any dataset with the expected columns (see [Generalization](#generalization)).
2. **Agent calls tools** — A LangGraph ReAct agent invokes Python analysis functions over the dataset.
3. **Synthesize report** — The LLM uses tool outputs to produce a structured decision-support brief for a battery trader.

```
User prompt → ReAct Agent → Tools (Python) → Structured report
```

The agent is instructed to call tools in a fixed order and never invent numbers.

## How the Agent Uses Tools

The agent has five tools defined in `src/tools.py`:

| Tool | Purpose |
|------|---------|
| `compute_revenue_summary` | Total historical revenue, perfect revenue, and gap |
| `identify_high_price_intervals` | Top-N price spikes and whether dispatch was missed |
| `compare_historical_vs_perfect_dispatch` | Intervals with the largest revenue gap |
| `analyze_state_of_charge_patterns` | SOC constraints during high-price periods |
| `get_dataset_info` | Dataset metadata (time range, row count) |

The workflow in `src/agent.py`:

1. Agent receives the user prompt.
2. Agent calls `compute_revenue_summary` to quantify the gap.
3. Agent calls dispatch and price tools to identify drivers.
4. Agent calls SOC analysis for contributing factors.
5. Agent writes the final report with gap, drivers, and 2 recommendations.

Tool outputs are JSON strings returned to the LLM as observations — the model reasons over these, not over raw CSV rows.

## Project Structure

```text
Powerline-Agent/
├── main.py              # Runnable entry point
├── README.md
├── example_output.md    # Example prompt + output
├── architecture.md      # Design notes
├── requirements.txt
├── example.env
├── data/
│   └── data.csv         # One week, interval-level battery data
├── src/
│   ├── data_loader.py   # CSV loading + schema normalization
│   ├── tools.py         # Analysis tools
│   └── agent.py         # LangGraph ReAct agent
└── tests/
    └── test_tools.py
```

## Generalization

The system runs on any CSV with the same schema without code changes. Column names are normalized via aliases in `src/data_loader.py`:

| Canonical Column | Accepted Aliases |
|------------------|------------------|
| `historical_revenue_usd` | `historical_revenue`, `actual_revenue_usd`, `revenue_usd` |
| `perfect_revenue_usd` | `perfect_revenue`, `benchmark_revenue_usd`, `counterfactual_revenue_usd` |
| `historical_power_mw` | `historical_power`, `actual_power_mw`, `power_mw` |
| `perfect_power_mw` | `perfect_power`, `counterfactual_power_mw` |

Point to a new file with `--data path/to/other.csv`.

## Example Output

See [example_output.md](example_output.md) for a full example prompt and grounded agent response.

**Quick summary from the included dataset:**

| Metric | Value |
|--------|-------|
| Historical revenue | $146,734.24 |
| Perfect revenue | $217,519.99 |
| Gap | $70,785.75 |

## Requirements Mapping

| Assignment Requirement | Implementation |
|------------------------|----------------|
| LLM agent + tools | LangGraph `create_react_agent` with 5 Python tools |
| Structured workflow | Agent calls tools sequentially, then synthesizes |
| Quantify gap | `compute_revenue_summary` |
| Identify drivers | `compare_historical_vs_perfect_dispatch`, `identify_high_price_intervals`, `analyze_state_of_charge_patterns` |
| 2 recommendations | Structured output template in agent system prompt |
| Generalization | Schema alias adapter in `data_loader.py` |
| Runnable script | `main.py` |
| README | This file |
| Example output | `example_output.md` |

## Author

Jasdeep Sidhu
