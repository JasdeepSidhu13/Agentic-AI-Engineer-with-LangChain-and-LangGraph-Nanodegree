import json
import os
import uuid

from langchain_core.tools import tool
from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

_SOLUTION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MEMORY_DB = os.path.join(_SOLUTION_ROOT, "data", "core", "memory.db")

MemBase = declarative_base()


class LongTermMemory(MemBase):
    __tablename__ = "long_term_memory"
    memory_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    category = Column(String)  # "resolved_issue", "preference", "escalation_history"
    summary = Column(Text)
    details = Column(Text)  # JSON string of structured data
    created_at = Column(DateTime, default=func.now())


def _get_memory_session():
    engine = create_engine(f"sqlite:///{MEMORY_DB}", echo=False)
    MemBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@tool
def store_long_term_memory(user_id: str, category: str, summary: str, details: str) -> str:
    """Store a piece of long-term memory for a user.
    Categories: resolved_issue, preference, escalation_history.
    Use this to save important information about customer interactions for future reference."""
    session = _get_memory_session()
    try:
        mem = LongTermMemory(
            memory_id=str(uuid.uuid4()),
            user_id=user_id,
            category=category,
            summary=summary,
            details=details,
        )
        session.add(mem)
        session.commit()
        return json.dumps({"status": "stored", "memory_id": mem.memory_id})
    finally:
        session.close()


@tool
def retrieve_long_term_memory(user_id: str) -> str:
    """Retrieve all long-term memories for a user to provide personalized context.
    Use this at the start of an interaction to check if the user has prior history."""
    session = _get_memory_session()
    try:
        memories = (
            session.query(LongTermMemory)
            .filter_by(user_id=user_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(10)
            .all()
        )
        if not memories:
            return json.dumps({"message": "No prior history found for this user."})
        results = []
        for m in memories:
            results.append({
                "category": m.category,
                "summary": m.summary,
                "details": m.details,
                "created_at": str(m.created_at),
            })
        return json.dumps(results)
    finally:
        session.close()
