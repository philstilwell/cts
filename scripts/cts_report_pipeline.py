#!/usr/bin/env python3
"""Build privacy-safe CTS weekly report summaries from SurveyOL-style CSV files."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


SCHEMA_VERSION = "cts-weekly-summary-v0.2"
CUT_POINTS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object.")
    return data


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit(f"{path} does not look like a CSV with headers.")
        return [dict(row) for row in reader]


def normalize_header(value: str) -> str:
    return " ".join(value.strip().lower().split())


def source_candidates(item: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for key in ("source_column", "column", "text"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value)
    values = item.get("source_columns")
    if isinstance(values, list):
        candidates.extend(str(value) for value in values if str(value).strip())
    return candidates


def find_column(headers: list[str], candidates: list[str]) -> str | None:
    exact = {header: header for header in headers}
    normalized = {normalize_header(header): header for header in headers}
    for candidate in candidates:
        if candidate in exact:
            return candidate
        matched = normalized.get(normalize_header(candidate))
        if matched:
            return matched
    return None


def parse_credence(value: str) -> float | None:
    cleaned = value.strip().replace("%", "")
    if not cleaned:
        return None
    try:
        number = float(cleaned)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def rounded(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def count_equal(values: list[float], target: float) -> int:
    return sum(1 for value in values if abs(value - target) < 1e-9)


def count_between(values: list[float], low: float, high: float, *, include_low: bool, include_high: bool) -> int:
    total = 0
    for value in values:
        low_ok = value >= low if include_low else value > low
        high_ok = value <= high if include_high else value < high
        if low_ok and high_ok:
            total += 1
    return total


def s23_bucket_counts(values: list[float]) -> list[float]:
    """Reproduce the S23 half-boundary credence bucket formulas."""
    if not values:
        return [0.0] * 10

    counts: list[float] = []
    for index in range(10):
        low = CUT_POINTS[index]
        high = CUT_POINTS[index + 1]
        if index == 0:
            base = count_between(values, low, high, include_low=True, include_high=False)
        elif index == 9:
            base = count_between(values, low, high, include_low=False, include_high=True)
        else:
            base = count_between(values, low, high, include_low=False, include_high=False)
        counts.append(base + count_equal(values, low) / 2 + count_equal(values, high) / 2)
    return counts


def s23_smoothed_percentages(values: list[float]) -> list[float]:
    if not values:
        return [0.0] * 10
    counts = s23_bucket_counts(values)
    padded = [counts[0], *counts, counts[-1]]
    smoothed = [((padded[index] * 0.03 + padded[index + 1] + padded[index + 2] * 0.03) / len(values)) * 100 for index in range(10)]
    return [min(100.0, value) for value in smoothed]


def simple_histogram_counts(values: list[float]) -> list[int]:
    counts = [0] * 10
    for value in values:
        bucket = 9 if value >= 90 else max(0, min(9, int(value // 10)))
        counts[bucket] += 1
    return counts


def display_distribution_percentages(values: list[float]) -> list[float]:
    """Create the public sparkline series from observed bins with light smoothing."""
    if not values:
        return [0.0] * 10
    counts = simple_histogram_counts(values)
    padded = [0, *counts, 0]
    smoothed = [((padded[index] * 0.03 + padded[index + 1] + padded[index + 2] * 0.03) / len(values)) * 100 for index in range(10)]
    return [min(100.0, value) for value in smoothed]


def doubt_dogma(values: list[float]) -> dict[str, Any]:
    exact_zero_count = count_equal(values, 0)
    exact_hundred_count = count_equal(values, 100)
    endpoint_count = exact_zero_count + exact_hundred_count
    non_endpoint_count = len(values) - endpoint_count
    ratio = None if endpoint_count == 0 else non_endpoint_count / endpoint_count
    return {
        "non_endpoint_count": non_endpoint_count,
        "endpoint_count": endpoint_count,
        "exact_zero_count": exact_zero_count,
        "exact_hundred_count": exact_hundred_count,
        "ratio": rounded(ratio, 3),
    }


def key_tension(values: list[float], iqr: float | None, stdev: float | None, minimum_n: int) -> dict[str, Any]:
    if len(values) < minimum_n:
        return {"flag": False, "eligible": False, "reasons": ["below_minimum_n"]}

    reasons: list[str] = []
    if iqr is not None and iqr >= 40:
        reasons.append("high_iqr")
    if stdev is not None and stdev >= 30:
        reasons.append("high_standard_deviation")
    if values:
        low_share = sum(1 for value in values if value <= 33) / len(values)
        middle_share = sum(1 for value in values if 34 <= value <= 66) / len(values)
        high_share = sum(1 for value in values if value >= 67) / len(values)
        if low_share >= 0.2 and high_share >= 0.2 and middle_share <= 0.4:
            reasons.append("low_high_split")
    return {"flag": bool(reasons), "eligible": True, "reasons": reasons}


def summarize_item(
    item: dict[str, Any],
    rows: list[dict[str, str]],
    headers: list[str],
    quality: dict[str, Any],
    minimum_key_tension_n: int,
) -> dict[str, Any]:
    column = find_column(headers, source_candidates(item))
    item_id = str(item["id"])
    values: list[float] = []
    if column is None:
        quality["missing_item_columns"].append({"item_id": item_id, "candidates": source_candidates(item)})
    else:
        for row_index, row in enumerate(rows, start=2):
            raw_value = row.get(column, "")
            if raw_value is None or not str(raw_value).strip():
                continue
            parsed = parse_credence(str(raw_value))
            if parsed is None:
                quality["non_numeric_values"].append({"item_id": item_id, "row": row_index, "value": str(raw_value)})
                continue
            if parsed < 0 or parsed > 100:
                quality["out_of_range_values"].append({"item_id": item_id, "row": row_index, "value": parsed})
                continue
            values.append(parsed)

    n = len(values)
    q1 = percentile(values, 0.25)
    q3 = percentile(values, 0.75)
    iqr = q3 - q1 if q1 is not None and q3 is not None else None
    stdev = statistics.stdev(values) if n > 1 else 0.0 if n == 1 else None

    return {
        "id": item_id,
        "number": item.get("number"),
        "section": item.get("section"),
        "text": item.get("text"),
        "source_column": column,
        "n": n,
        "mean": rounded(statistics.fmean(values), 2) if values else None,
        "median": rounded(statistics.median(values), 2) if values else None,
        "min": rounded(min(values), 2) if values else None,
        "max": rounded(max(values), 2) if values else None,
        "q1": rounded(q1, 2),
        "q3": rounded(q3, 2),
        "iqr": rounded(iqr, 2),
        "standard_deviation": rounded(stdev, 2),
        "disagreement_score": rounded(iqr, 2),
        "doubt_dogma": doubt_dogma(values),
        "key_tension": key_tension(values, iqr, stdev, minimum_key_tension_n),
        "distribution": {
            "cut_points": CUT_POINTS,
            "simple_counts": simple_histogram_counts(values),
            "display_percentages": [round(value, 3) for value in display_distribution_percentages(values)],
            "s23_bucket_counts": [round(value, 3) for value in s23_bucket_counts(values)],
            "s23_smoothed_percentages": [round(value, 3) for value in s23_smoothed_percentages(values)],
        },
    }


def nonempty_count(rows: list[dict[str, str]], headers: list[str], candidates: list[str]) -> int:
    column = find_column(headers, candidates)
    if column is None:
        return 0
    return sum(1 for row in rows if str(row.get(column, "")).strip())


def build_summary(config: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    headers = list(rows[0].keys()) if rows else []
    quality: dict[str, Any] = {
        "rows_read": len(rows),
        "missing_item_columns": [],
        "non_numeric_values": [],
        "out_of_range_values": [],
    }
    privacy = config.get("privacy", {})
    minimum_key_tension_n = int(privacy.get("min_public_item_n", 30)) if isinstance(privacy, dict) else 30
    items = [summarize_item(item, rows, headers, quality, minimum_key_tension_n) for item in config.get("items", [])]
    suggestion_columns = [str(value) for value in config.get("suggestion_columns", [])]
    suggestions_received = nonempty_count(rows, headers, suggestion_columns)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "week": config.get("week"),
        "title": config.get("title"),
        "topic": config.get("topic"),
        "field_dates": config.get("field_dates", {}),
        "platform": config.get("platform", "SurveyOL"),
        "slider_scale": config.get("slider_scale", {"min": 0, "midpoint": 50, "max": 100}),
        "privacy": privacy,
        "response_count": max((item["n"] for item in items), default=0),
        "items": items,
        "participant_nominations": {
            "suggestions_received": suggestions_received,
            "raw_suggestions_public": False,
        },
        "quality": quality,
        "private_data_excluded": True,
    }


def cmd_summarize(args: argparse.Namespace) -> int:
    config = load_json(Path(args.config))
    rows = read_rows(Path(args.input))
    summary = build_summary(config, rows)
    payload = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize = subparsers.add_parser("summarize", help="create a public weekly summary JSON file")
    summarize.add_argument("--config", required=True, help="week report config JSON")
    summarize.add_argument("--input", required=True, help="private SurveyOL-style CSV input")
    summarize.add_argument("--output", help="public summary JSON output")
    summarize.set_defaults(func=cmd_summarize)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
