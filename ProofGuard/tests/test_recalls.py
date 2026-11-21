"""
Unit and Integration Tests for CPSC Recall Collection & Import
"""

import json
from pathlib import Path
import pytest

from app.recalls.cpsc_collector import (
    normalize_cpsc_record,
    deduplicate_recalls,
    extract_models_from_text,
)
from app.recalls.import_recalls import import_recalls_to_db, load_recalls_from_file
from app.schemas import RecallCreate
from app.db.models import Recall


def test_normalize_cpsc_record_full():
    raw_cpsc = {
        "RecallID": 10001,
        "RecallNumber": "23-001",
        "RecallDate": "2023-01-15T00:00:00",
        "Title": "Samsung Recalls Top-Load Washers Due to Fire Hazard",
        "Description": "This recall involves models WA70 and WA80 sold nationwide.",
        "URL": "https://www.cpsc.gov/Recalls/2023/samsung-washers",
        "Hazards": [{"Name": "The washing machine can overheat and cause fire."}],
        "Remedies": [{"Name": "Contact manufacturer for free repair."}],
        "Products": [{"Name": "Samsung Top-Load Washers", "Model": "WA70"}],
        "Manufacturers": [{"Name": "Samsung Electronics"}],
    }

    normalized = normalize_cpsc_record(raw_cpsc)

    assert normalized["external_recall_id"] == "CPSC-23-001"
    assert normalized["product_name"] == "Samsung Top-Load Washers"
    assert normalized["manufacturer"] == "Samsung Electronics"
    assert "WA70" in normalized["model_numbers"]
    assert normalized["recall_date"] == "2023-01-15"
    assert "fire" in normalized["hazard_description"].lower()
    assert "repair" in normalized["remedy"].lower()
    assert normalized["source_url"] == "https://www.cpsc.gov/Recalls/2023/samsung-washers"


def test_normalize_cpsc_record_missing_fields():
    # Record with minimal info - should not hallucinate
    raw_cpsc = {
        "RecallID": None,
        "RecallNumber": None,
        "RecallDate": None,
        "Title": "Appliance Recall Announcement",
        "Description": None,
        "Hazards": [],
        "Remedies": [],
        "Products": [],
        "Manufacturers": [],
    }

    normalized = normalize_cpsc_record(raw_cpsc)

    assert normalized["external_recall_id"] == "CPSC-UNKNOWN-0"
    assert normalized["product_name"] == "Appliance Recall Announcement"
    assert normalized["manufacturer"] is None
    assert normalized["model_numbers"] == []
    assert normalized["recall_date"] is None
    assert normalized["hazard_description"] is None
    assert normalized["remedy"] is None



def test_deduplicate_recalls():
    records = [
        {"external_recall_id": "CPSC-001", "source_url": "https://example.com/1", "product_name": "A"},
        {"external_recall_id": "CPSC-001", "source_url": "https://example.com/1-dup", "product_name": "A-dup"},
        {"external_recall_id": "CPSC-002", "source_url": "https://example.com/2", "product_name": "B"},
        {"external_recall_id": "CPSC-003", "source_url": "https://example.com/2", "product_name": "B-dup-url"},
    ]

    deduped = deduplicate_recalls(records)
    assert len(deduped) == 2
    ids = [r["external_recall_id"] for r in deduped]
    assert ids == ["CPSC-001", "CPSC-002"]


def test_extract_models_from_text():
    text = "The affected models include RF28, RF29, and RF30 with serial numbers..."
    models = extract_models_from_text(text)
    assert "RF28" in models
    assert "RF29" in models
    assert "RF30" in models


def test_import_recalls_to_db(session):
    test_records = [
        {
            "external_recall_id": "TEST-CPSC-101",
            "product_name": "Recall Dishwasher",
            "manufacturer": "Bosch",
            "model_numbers": ["SHX-01"],
            "recall_date": "2024-05-10",
            "hazard_description": "Overheating cord",
            "remedy": "Free inspection",
            "source_url": "https://example.com/recall-shx",
        },
        {
            "external_recall_id": "TEST-CPSC-102",
            "product_name": "Recall Microwave",
            "manufacturer": "GE",
            "model_numbers": ["JVM-12"],
            "recall_date": "2024-06-15",
            "hazard_description": "Spark hazard",
            "remedy": "Replacement",
            "source_url": "https://example.com/recall-jvm",
        },
    ]

    ins, upd = import_recalls_to_db(records=test_records, session=session)
    assert ins == 2
    assert upd == 0

    # Test update (upsert)
    updated_records = [
        {
            "external_recall_id": "TEST-CPSC-101",
            "product_name": "Recall Dishwasher Updated",
            "manufacturer": "Bosch",
            "model_numbers": ["SHX-01", "SHX-02"],
            "recall_date": "2024-05-10",
            "hazard_description": "Overheating cord updated",
            "remedy": "Free inspection",
            "source_url": "https://example.com/recall-shx",
        }
    ]
    ins2, upd2 = import_recalls_to_db(records=updated_records, session=session)
    assert ins2 == 0
    assert upd2 == 1


def test_load_real_recalls_file():
    data_path = Path("data/recalls/cpsc_recalls.json")
    assert data_path.exists(), "CPSC recall dataset JSON must exist"
    records = load_recalls_from_file(data_path)
    assert len(records) > 100
    # Check first record conforms to schema
    RecallCreate(**records[0])
