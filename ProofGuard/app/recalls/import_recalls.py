"""
ProofGuard - CPSC Recall Database Import Module
Author: Ashfaq (Recall Dataset Responsibility) / Integration

Imports normalized CPSC recall records from JSON or CSV files into the ProofGuard
SQLite database (the 'recalls' table) using SQLAlchemy ORM and Pydantic validation.
"""

import json
import csv
from pathlib import Path
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, engine
from app.db.models import Recall
from app.db.init_db import init_db
from app.schemas import RecallCreate

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "recalls" / "cpsc_recalls.json"


def load_recalls_from_file(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load recall records from a JSON or CSV file."""
    path = Path(file_path) if file_path else DEFAULT_DATA_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Recall data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif suffix == ".csv":
        records = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                models_raw = row.get("model_numbers", "")
                models_list = [m.strip() for m in models_raw.split("|") if m.strip()] if models_raw else []
                record = {
                    "external_recall_id": row.get("external_recall_id"),
                    "product_name": row.get("product_name") or None,
                    "manufacturer": row.get("manufacturer") or None,
                    "model_numbers": models_list,
                    "recall_date": row.get("recall_date") or None,
                    "hazard_description": row.get("hazard_description") or None,
                    "remedy": row.get("remedy") or None,
                    "source_url": row.get("source_url") or None,
                }
                records.append(record)
        return records
    else:
        raise ValueError(f"Unsupported recall data file format: {suffix}")


def import_recalls_to_db(
    records: list[dict[str, Any]] | None = None,
    file_path: str | Path | None = None,
    session: Session | None = None,
) -> tuple[int, int]:
    """
    Import recall records into SQLite database.
    Performs upsert / deduplication on external_recall_id.

    Returns:
        (inserted_count, updated_count)
    """
    if records is None:
        records = load_recalls_from_file(file_path)

    should_close = False
    if session is None:
        init_db()  # Ensure tables exist
        session = SessionLocal()
        should_close = True

    inserted = 0
    updated = 0

    try:
        for raw_item in records:
            # Validate through RecallCreate schema
            validated = RecallCreate(**raw_item)
            data = validated.model_dump()

            existing = session.scalar(
                select(Recall).where(Recall.external_recall_id == data["external_recall_id"])
            )

            if existing:
                existing.product_name = data.get("product_name")
                existing.manufacturer = data.get("manufacturer")
                existing.model_numbers = data.get("model_numbers") or []
                existing.recall_date = data.get("recall_date")
                existing.hazard_description = data.get("hazard_description")
                existing.remedy = data.get("remedy")
                existing.source_url = data.get("source_url")
                updated += 1
            else:
                new_recall = Recall(**data)
                session.add(new_recall)
                inserted += 1

        session.commit()
        return inserted, updated
    except Exception:
        session.rollback()
        raise
    finally:
        if should_close:
            session.close()


if __name__ == "__main__":
    print(f"Importing CPSC recall records from {DEFAULT_DATA_PATH}...")
    ins, upd = import_recalls_to_db()
    print(f"Import finished successfully: {ins} inserted, {upd} updated.")
