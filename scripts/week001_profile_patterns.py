#!/usr/bin/env python3
"""Build Week 1 privacy-safe profile pattern evidence.

This script reads private respondent-level files and writes:
- a private audit with subgroup eligibility and exploratory differences
- public-safe aggregate profile patterns into the Week 1 summary JSON files
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
from typing import Any


PUBLIC_PATTERN_ITEMS = [
    "W001-Q09",
    "W001-Q10",
    "W001-Q08",
    "W001-Q14",
    "W001-Q15",
    "W001-Q05",
    "W001-Q03",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object.")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str | None) -> float | None:
    cleaned = str(value or "").strip().replace(",", "").replace("%", "")
    if not cleaned:
        return None
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def clean(value: str | None) -> str | None:
    normalized = " ".join(str(value or "").strip().split())
    return normalized or None


def item_columns(config: dict[str, Any], headers: list[str]) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for item in config.get("items", []):
        if not isinstance(item, dict):
            continue
        column = next((candidate for candidate in item.get("source_columns", []) if candidate in headers), None)
        if column:
            found[str(item["id"])] = {
                "id": str(item["id"]),
                "number": item.get("number"),
                "text": item.get("text"),
                "column": column,
            }
    return found


def mean(values: list[float]) -> float:
    return round(statistics.fmean(values), 1)


def group_values(rows: list[dict[str, Any]], profile_field: str, group: str, item_column: str) -> list[float]:
    values = [
        number(row.get(item_column))
        for row in rows
        if clean(row.get(profile_field)) == group
    ]
    return [value for value in values if value is not None]


def merge_registry(rows: list[dict[str, str]], registry_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    registry_by_id = {
        clean(row.get("Participant ID")): row
        for row in registry_rows
        if clean(row.get("Participant ID"))
    }
    merged: list[dict[str, Any]] = []
    for row in rows:
        registry_row = registry_by_id.get(clean(row.get("Participant ID")), {})
        merged.append({**row, **{f"registry::{key}": value for key, value in registry_row.items()}})
    return merged


def build_patterns(args: argparse.Namespace) -> int:
    config = load_json(Path(args.config))
    responses = read_csv(Path(args.joined))
    registry = read_csv(Path(args.registry))
    rows = merge_registry(responses, registry)
    headers = list(responses[0].keys()) if responses else []
    items = item_columns(config, headers)
    privacy = config.get("privacy", {})
    min_public_subgroup_n = int(privacy.get("min_public_subgroup_n", 15))
    preferred_public_subgroup_n = int(privacy.get("preferred_public_subgroup_n", 20))

    profile_field = "registry::Denomination Evangelical?"
    profile_counts: dict[str, int] = {}
    for row in rows:
        value = clean(row.get(profile_field))
        if value:
            profile_counts[value] = profile_counts.get(value, 0) + 1

    groups = ["Yes", "No"]
    group_counts = {group: profile_counts.get(group, 0) for group in groups}
    eligible = all(count >= min_public_subgroup_n for count in group_counts.values())

    item_patterns = []
    for item_id in PUBLIC_PATTERN_ITEMS:
        item = items[item_id]
        yes_values = group_values(rows, profile_field, "Yes", item["column"])
        no_values = group_values(rows, profile_field, "No", item["column"])
        if len(yes_values) < min_public_subgroup_n or len(no_values) < min_public_subgroup_n:
            continue
        yes_mean = mean(yes_values)
        no_mean = mean(no_values)
        item_patterns.append(
            {
                "item_id": item_id,
                "number": item["number"],
                "text": item["text"],
                "groups": [
                    {"label": "Evangelical", "n": len(yes_values), "mean": yes_mean},
                    {"label": "Non-evangelical", "n": len(no_values), "mean": no_mean},
                ],
                "mean_difference": round(yes_mean - no_mean, 1),
            }
        )

    suppressed_fields = []
    for field in [
        "Closest Denomination/Fellowship Affiliation",
        "Gender",
        "Marital Status (Submitted)",
        "Race",
        "Self-Identifies Fundamentalist?",
    ]:
        counts: dict[str, int] = {}
        registry_field = f"registry::{field}"
        for row in rows:
            value = clean(row.get(registry_field))
            if value:
                counts[value] = counts.get(value, 0) + 1
        suppressed_fields.append(
            {
                "field": field,
                "reason": "too_sparse_for_public_subgroup_reporting"
                if not any(count >= min_public_subgroup_n for count in counts.values())
                else "partial_or_imbalanced_cells",
                "counts": dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))),
            }
        )

    generated_at = datetime.now(timezone.utc).isoformat()
    public_payload = {
        "generated_at": generated_at,
        "status": "exploratory_privacy_safe",
        "axis": {
            "field": "Denomination Evangelical?",
            "public_label": "Evangelical profile",
            "groups": [
                {"label": "Evangelical", "value": "Yes", "n": group_counts["Yes"]},
                {"label": "Non-evangelical", "value": "No", "n": group_counts["No"]},
            ],
            "eligible_for_public_reporting": eligible,
            "minimum_public_subgroup_n": min_public_subgroup_n,
            "preferred_public_subgroup_n": preferred_public_subgroup_n,
        },
        "interpretation_note": (
            "These are exploratory subgroup mean differences from the final Week 1 respondent set. "
            "They are descriptive, not causal, and the smaller group barely clears the public minimum."
        ),
        "items": item_patterns,
        "suppressed_profile_fields": [
            {"field": item["field"], "reason": item["reason"]}
            for item in suppressed_fields
        ],
        "private_data_excluded": True,
    }

    audit_payload = {
        "generated_at": generated_at,
        "response_rows": len(rows),
        "profile_patterns": public_payload,
        "suppressed_field_counts": suppressed_fields,
        "source_files": {
            "joined": str(args.joined),
            "registry": str(args.registry),
            "config": str(args.config),
        },
    }

    audit_path = Path(args.audit_output)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for summary_path_text in args.summary:
        summary_path = Path(summary_path_text)
        summary = load_json(summary_path)
        summary["profile_patterns"] = public_payload
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--joined", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--audit-output", required=True)
    parser.add_argument("--summary", action="append", default=[])
    return build_patterns(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
