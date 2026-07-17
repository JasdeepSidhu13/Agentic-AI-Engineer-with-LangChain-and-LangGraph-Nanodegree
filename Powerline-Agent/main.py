#!/usr/bin/env python3
"""Powerline take-home: LLM agent for battery performance gap analysis."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from src.agent import run_analysis
from src.data_loader import get_data_store

DEFAULT_PROMPT = (
    "Analyze this week's battery performance. Quantify the gap between historical "
    "and perfect foresight operation, identify the key driver and a secondary "
    "contributing factor, and give me two actionable recommendations."
)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Powerline battery performance analysis agent")
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Path to CSV dataset (defaults to data/data.csv)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Analysis prompt for the agent",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the report (e.g., example_output.md)",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Error: Set OPENAI_API_KEY in .env (see example.env)")

    store = get_data_store(args.data)
    print(f"Loaded {store.summary['row_count']} intervals "
          f"({store.summary['time_min']} → {store.summary['time_max']})\n")

    print("Running agent analysis...\n")
    report = run_analysis(args.prompt)

    if args.output:
        args.output.write_text(f"# Agent Report\n\n**Prompt:** {args.prompt}\n\n---\n\n{report}\n")
        print(f"Report saved to {args.output}\n")

    print(report)


if __name__ == "__main__":
    main()
