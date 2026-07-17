#!/usr/bin/env python3
"""Powerline Battery Co-Pilot — interactive CLI entry point."""

from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.workflow import build_app, get_llm


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY in .env (see example.env)")
        return

    app = build_app()
    thread_id = str(uuid.uuid4())
    user_id = os.getenv("DEFAULT_USER_ID", "operator-001")
    print("Powerline Battery Co-Pilot")
    print(f"Session: {thread_id}")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if not query or query.lower() in {"exit", "quit"}:
            break

        result = app.invoke(
            {
                "user_query": query,
                "messages": [HumanMessage(content=query)],
                "session_id": thread_id,
                "user_id": user_id,
                "resolution_status": "pending",
                "retry_count": 0,
                "actions_taken": [],
            },
            config={"configurable": {"thread_id": thread_id, "llm": get_llm()}},
        )

        answer = result.get("draft_answer") or "No answer generated."
        print(f"\nCo-Pilot: {answer}\n")
        if result.get("confidence_score") is not None:
            print(f"[confidence: {result['confidence_score']:.2f}]")
        if result.get("quality_score") is not None:
            print(f"[quality: {result['quality_score']:.2f}]")
        print(f"[agents: {' → '.join(result.get('actions_taken', []))}]\n")


if __name__ == "__main__":
    main()
