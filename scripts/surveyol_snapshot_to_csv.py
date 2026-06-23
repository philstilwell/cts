#!/usr/bin/env python3
"""Convert a private SurveyOL API snapshot into the CSV shape used by CTS reports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


INCLUDED_TYPES = {"Slider", "Ranking", "Comment Box"}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object.")
    return data


def question_columns(snapshot: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    questions_by_page = snapshot.get("questions_by_page", {})
    if not isinstance(questions_by_page, dict):
        raise SystemExit("Snapshot does not contain questions_by_page.")

    ordered: list[tuple[int, str, str]] = []
    for questions in questions_by_page.values():
        if not isinstance(questions, list):
            continue
        for question in questions:
            if not isinstance(question, dict) or question.get("type") not in INCLUDED_TYPES:
                continue
            props = question.get("properties", {})
            props = props if isinstance(props, dict) else {}
            title = str(props.get("title") or "").strip()
            guid = str(props.get("Guid") or question.get("id") or "").strip()
            if not title or not guid:
                continue
            ordered.append((int(question.get("questionIndex") or 0), guid, title))

    ordered.sort(key=lambda item: item[0])
    return [title for _, _, title in ordered], {guid: title for _, guid, title in ordered}


def response_rows(snapshot: dict[str, Any], guid_to_title: dict[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    responses = snapshot.get("responses", [])
    if not isinstance(responses, list):
        raise SystemExit("Snapshot does not contain a responses list.")

    for response in responses:
        if not isinstance(response, dict):
            continue
        row: dict[str, str] = {
            "Start Date": "",
            "End Date": str(response.get("completedDate") or ""),
        }
        answers = response.get("questions", [])
        if not isinstance(answers, list):
            answers = []
        for answer in answers:
            if not isinstance(answer, dict):
                continue
            title = guid_to_title.get(str(answer.get("guid") or ""))
            if not title:
                continue
            value = answer.get("answer")
            row[title] = "" if value is None else str(value)
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, help="private SurveyOL snapshot JSON")
    parser.add_argument("--output", required=True, help="private SurveyOL-style CSV output")
    args = parser.parse_args()

    snapshot = load_json(Path(args.snapshot))
    columns, guid_to_title = question_columns(snapshot)
    rows = response_rows(snapshot, guid_to_title)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Start Date", "End Date", *columns], extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} response rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
