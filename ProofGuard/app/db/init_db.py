"""
ProofGuard - Database Initialization Module
Author: Aswin (Team Lead)

Initializes SQLite database tables using SQLAlchemy DeclarativeBase metadata.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import Base, engine
# Import models so that they are registered on Base.metadata
from app.db import models


def init_db(target_engine=None):
    """Create all database tables defined in the ORM models."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    return eng


def get_table_names(target_engine=None):
    """Inspect and return existing table names."""
    from sqlalchemy import inspect
    eng = target_engine or engine
    inspector = inspect(eng)
    return inspector.get_table_names()


if __name__ == "__main__":
    print("Initializing ProofGuard database tables...")
    init_db()
    tables = get_table_names()
    print(f"Database initialized successfully at: {engine.url}")
    print(f"Registered tables: {tables}")
