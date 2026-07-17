from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.tools import ANALYSIS_TOOLS

SYSTEM_PROMPT = """You are a battery trading decision-support agent for Powerline.

Analyze one week of interval-level battery performance data by calling the provided tools.
Do NOT estimate numbers yourself — always use tool outputs.

Follow this workflow:
1. Call compute_revenue_summary to quantify the performance gap.
2. Call compare_historical_vs_perfect_dispatch and identify_high_price_intervals to find gap drivers.
3. Call analyze_state_of_charge_patterns for contributing SOC constraints.
4. Synthesize a concise report for a battery trader.

Your final answer MUST include these sections:

## Performance Gap
- Total Historical revenue (USD)
- Total Perfect revenue (USD)
- Total gap (Perfect − Historical, USD)

## Key Driver
- Name the primary driver of the gap
- Short explanation
- Supporting evidence (cite specific tool outputs / numbers)

## Secondary Contributing Factor
- Name a secondary factor
- Short explanation
- Supporting evidence

## Recommendations
Provide exactly 2 recommendations. For each:
- **Action**: what to change
- **Rationale**: why, grounded in tool evidence
- **Expected benefit**: brief, quantitative if possible
- **Tradeoff**: one downside or cost

Write for a battery trader. Be specific and grounded. Do not invent numbers."""


def build_agent(model: str | None = None):
    llm = ChatOpenAI(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return create_react_agent(
        model=llm,
        tools=ANALYSIS_TOOLS,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )


def run_analysis(user_prompt: str, model: str | None = None) -> str:
    agent = build_agent(model=model)
    result = agent.invoke({"messages": [HumanMessage(content=user_prompt)]})
    return result["messages"][-1].content
