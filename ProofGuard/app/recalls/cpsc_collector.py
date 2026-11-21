"""
ProofGuard - CPSC Recall Data Collection & Normalization Module
Author: Ashfaq (Recall Dataset Responsibility) / Integration

Collects official consumer product recall records from the US Consumer Product
Safety Commission (CPSC) via the SaferProducts.gov public API, cleans and
normalizes the records to conform to the RecallCreate Pydantic schema, handles
missing values without fabrication, and exports structured CSV and JSON datasets.
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
import requests

from app.schemas import RecallCreate

CPSC_API_BASE = "https://www.saferproducts.gov/RestWebServices/Recall"
USER_AGENT = "ProofGuard/1.0 (Academic Research; Evidence-Based Recall Intelligence)"

DEFAULT_QUERIES = [
    "washing machine",
    "refrigerator",
    "dishwasher",
    "dryer",
    "microwave",
    "cooktop",
    "air conditioner",
    "television",
    "laptop",
    "battery",
    "heater",
]


def extract_models_from_text(text: str) -> list[str]:
    """Extract candidate model numbers mentioned in descriptions or text blocks."""
    if not text:
        return []

    models = set()
    # Pattern for explicit model listings: model(s) [include/are/:] WA70, WA80, RF28...
    match = re.search(
        r"(?i)\bmodels?(?:\s+(?:include|including|are|numbers?|no\.?|codes?))?[\s:=#]+([A-Za-z0-9\-_/,\s]{3,120})",
        text,
    )
    if match:
        raw_segment = match.group(1)
        # Stop at words like 'with', 'sold', 'manufactured', 'having', 'which'
        stop_match = re.split(r"(?i)\b(?:with|sold|manufactured|having|which|and\s+were|between)\b", raw_segment)
        segment = stop_match[0] if stop_match else raw_segment

        # Split on commas, 'and', 'or', semicolons, whitespace
        parts = re.split(r"[\t\n,;/]+|\band\b|\bor\b", segment)
        for p in parts:
            p_clean = p.strip().strip(".")
            # Filter out non-model words
            words = p_clean.split()
            for token in words:
                token_clean = token.strip("(),;:. ")
                if (
                    2 <= len(token_clean) <= 30
                    and any(c.isdigit() for c in token_clean)
                    and not token_clean.lower().startswith("http")
                ):
                    models.add(token_clean)

    return sorted(models)



def normalize_cpsc_record(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Clean and normalize an official CPSC API recall record into the ProofGuard schema.
    Handles missing fields with None or empty lists (never fabricates data).
    """
    # 1. External Recall ID
    recall_num = raw.get("RecallNumber") or raw.get("RecallID")
    if recall_num:
        external_id = f"CPSC-{str(recall_num).strip()}"
    else:
        external_id = f"CPSC-UNKNOWN-{raw.get('RecallID') or '0'}"


    # 2. Product Name
    title = (raw.get("Title") or "").strip()
    products_list = raw.get("Products") or []
    product_name = None
    if products_list and isinstance(products_list, list) and len(products_list) > 0:
        first_prod = products_list[0]
        if isinstance(first_prod, dict) and first_prod.get("Name"):
            product_name = first_prod.get("Name").strip()

    if not product_name and title:
        # Fallback to cleaning Title (e.g. 'Samsung Recalls Top-Load Washing Machines Due to...')
        title_match = re.search(r"(?i)\brecalls?\s+([^;]+?)\s+(?:due\s+to|because)\b", title)
        if title_match and len(title_match.group(1).strip()) > 3:
            product_name = title_match.group(1).strip()
        else:
            product_name = title


    # 3. Manufacturer
    mfr_list = raw.get("Manufacturers") or []
    dist_list = raw.get("Distributors") or []
    importer_list = raw.get("Importers") or []
    manufacturer = None

    for candidate_list in (mfr_list, dist_list, importer_list):
        if candidate_list and isinstance(candidate_list, list):
            for item in candidate_list:
                if isinstance(item, dict) and item.get("Name"):
                    cand_name = item.get("Name").strip()
                    if cand_name:
                        manufacturer = cand_name
                        break
        if manufacturer:
            break

    # If manufacturer is still missing, try inferring only from explicit '<Name> Recalls...' pattern
    if not manufacturer and title:
        title_mfr_match = re.search(r"^(?:Official\s+)?([A-Za-z0-9&.\- ]+?)\s+(?:recalls|announces\s+recall\s+of)\b", title, re.IGNORECASE)
        if title_mfr_match:
            candidate_mfr = title_mfr_match.group(1).strip()
            if candidate_mfr.lower() not in {"cpsc", "recall", "recalls", "the", "consumer", "various", "major", "safety"}:
                manufacturer = candidate_mfr



    # 4. Model Numbers
    models = set()
    for prod in products_list:
        if isinstance(prod, dict) and prod.get("Model"):
            m_str = str(prod.get("Model")).strip()
            if m_str:
                for sub_m in re.split(r"[,;]+", m_str):
                    sub_m = sub_m.strip()
                    if len(sub_m) >= 2:
                        models.add(sub_m)

    description = raw.get("Description") or ""
    inferred_models = extract_models_from_text(description)
    models.update(inferred_models)

    # 5. Recall Date
    raw_date = raw.get("RecallDate") or ""
    recall_date = None
    if raw_date:
        # Formats usually like "2022-12-22T00:00:00" or "YYYY-MM-DD"
        recall_date = raw_date.split("T")[0].strip()

    # 6. Hazard Description
    hazards_list = raw.get("Hazards") or []
    hazard_parts = []
    if isinstance(hazards_list, list):
        for h in hazards_list:
            if isinstance(h, dict) and h.get("Name"):
                hazard_parts.append(h.get("Name").strip())
    hazard_description = " ".join(hazard_parts) if hazard_parts else None

    # 7. Remedy
    remedies_list = raw.get("Remedies") or []
    remedy_parts = []
    if isinstance(remedies_list, list):
        for rem in remedies_list:
            if isinstance(rem, dict) and rem.get("Name"):
                remedy_parts.append(rem.get("Name").strip())
    remedy = " ".join(remedy_parts) if remedy_parts else None

    # 8. Source URL
    source_url = raw.get("URL") or (
        f"https://www.cpsc.gov/Recalls/{recall_num}" if recall_num else None
    )

    record = {
        "external_recall_id": external_id,
        "product_name": product_name,
        "manufacturer": manufacturer,
        "model_numbers": sorted(models),
        "recall_date": recall_date,
        "hazard_description": hazard_description,
        "remedy": remedy,
        "source_url": source_url,
    }

    # Validate against schema to ensure strict data consistency
    validated = RecallCreate(**record)
    return validated.model_dump()


def deduplicate_recalls(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate recall records based on external_recall_id or source_url."""
    seen_ids = set()
    seen_urls = set()
    unique_records = []

    for rec in records:
        rec_id = rec.get("external_recall_id")
        rec_url = rec.get("source_url")

        if rec_id and rec_id in seen_ids:
            continue
        if rec_url and rec_url in seen_urls:
            continue

        if rec_id:
            seen_ids.add(rec_id)
        if rec_url:
            seen_urls.add(rec_url)

        unique_records.append(rec)

    return unique_records


def fetch_cpsc_recalls(
    queries: list[str] | None = None,
    timeout: int = 15,
) -> list[dict[str, Any]]:
    """Fetch real recall records from the official CPSC SaferProducts.gov API."""
    if queries is None:
        queries = DEFAULT_QUERIES

    headers = {"User-Agent": USER_AGENT}
    raw_records = []

    for query in queries:
        url = f"{CPSC_API_BASE}?format=json&RecallTitle={requests.utils.quote(query)}"
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    raw_records.extend(data)
        except Exception as e:
            print(f"Warning: failed to query CPSC API for '{query}': {e}")

    return raw_records


def collect_and_save(
    output_dir: str | Path = "data/recalls",
    queries: list[str] | None = None,
) -> tuple[Path, Path, int]:
    """
    Fetch official CPSC recall data, normalize, deduplicate, and save to CSV and JSON.
    Returns (json_path, csv_path, record_count).
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    raw_records = fetch_cpsc_recalls(queries=queries)
    normalized = [normalize_cpsc_record(r) for r in raw_records]
    deduped = deduplicate_recalls(normalized)

    json_path = out_path / "cpsc_recalls.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    csv_path = out_path / "cpsc_recalls.csv"
    fieldnames = [
        "external_recall_id",
        "product_name",
        "manufacturer",
        "model_numbers",
        "recall_date",
        "hazard_description",
        "remedy",
        "source_url",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in deduped:
            row = dict(rec)
            # Serialize list of model numbers to pipe-separated string for CSV
            row["model_numbers"] = " | ".join(row.get("model_numbers") or [])
            writer.writerow(row)

    # Save collection provenance metadata
    metadata_path = out_path / "collection_metadata.json"
    metadata = {
        "source": "US Consumer Product Safety Commission (CPSC) - SaferProducts.gov API",
        "api_endpoint": CPSC_API_BASE,
        "collection_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
        "total_records_collected": len(deduped),
        "queries_used": queries or DEFAULT_QUERIES,
        "schema_version": "ProofGuard RecallCreate v1.0",
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return json_path, csv_path, len(deduped)


if __name__ == "__main__":
    print("Collecting official CPSC product recall records...")
    j_path, c_path, count = collect_and_save()
    print(f"Collection complete: {count} unique verified CPSC recall records saved.")
    print(f"JSON dataset: {j_path}")
    print(f"CSV dataset:  {c_path}")
