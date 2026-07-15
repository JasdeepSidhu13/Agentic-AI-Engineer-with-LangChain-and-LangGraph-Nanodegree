import logging
import os
import uuid
from contextlib import contextmanager

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("udahub.utils")

Base = declarative_base()


def reset_db(db_path: str, echo: bool = True):
    """Drops the existing db file and recreates all tables."""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing {db_path}")

    engine = create_engine(f"sqlite:///{db_path}", echo=echo)
    Base.metadata.create_all(engine)
    print(f"Recreated {db_path} with fresh schema")


@contextmanager
def get_session(engine: Engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def model_to_dict(instance):
    """Convert a SQLAlchemy model instance to a dictionary."""
    return {
        column.name: getattr(instance, column.name)
        for column in instance.__table__.columns
    }


def save_message_to_db(engine: Engine, ticket_id: str, role: str, content: str):
    """Persist a message to the ticket_messages table."""
    from data.models.udahub import RoleEnum, TicketMessage

    with get_session(engine) as session:
        msg = TicketMessage(
            message_id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            role=RoleEnum[role],
            content=content,
        )
        session.add(msg)


def chat_interface(agent: CompiledStateGraph, ticket_id: str, engine: Engine = None):
    """Interactive chat loop with the agent.

    Args:
        agent: Compiled LangGraph agent.
        ticket_id: Thread/ticket ID for session continuity.
        engine: Optional SQLAlchemy engine to persist messages to the DB.
    """
    config = {"configurable": {"thread_id": ticket_id}}

    print("UDA-Hub Support Chat")
    print("Type your message below. Type 'quit' to exit.")
    print("-" * 45)

    while True:
        try:
            user_input = input("\nUser: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye!")
            break

        if not user_input.strip():
            continue

        if user_input.strip().lower() in ["quit", "exit", "q"]:
            print("Assistant: Goodbye!")
            break

        trigger = {"messages": [HumanMessage(content=user_input)]}

        result = agent.invoke(input=trigger, config=config)
        response = result["messages"][-1].content
        print(f"\nAssistant: {response}")

        # Persist to DB if engine provided
        if engine:
            try:
                save_message_to_db(engine, ticket_id, "user", user_input)
                save_message_to_db(engine, ticket_id, "ai", response)
            except Exception as e:
                logger.warning(f"Failed to persist message: {e}")

        logger.info(f"[ticket={ticket_id}] User: {user_input[:80]}")
        logger.info(f"[ticket={ticket_id}] AI: {response[:80]}")
