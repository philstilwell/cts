#!/usr/bin/env python3
"""Append public-safe entries to the CTS automation daily log."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "public" / "automation-daily-log.json"
ET = ZoneInfo("America/New_York")


def parse_iso(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"Unsupported ISO timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ET)
    return parsed


def format_time_et(value: datetime) -> str:
    return value.astimezone(ET).strftime("%-I:%M:%S %p %Z")


def load_log(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"updated_at": "", "updated_time_et": "", "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_log(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def cmd_append(args: argparse.Namespace) -> int:
    path = Path(args.path)
    payload = load_log(path)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    recorded_at = parse_iso(args.recorded_at)
    recorded_at_et = recorded_at.astimezone(ET)
    entry = {
        "date": recorded_at_et.strftime("%Y-%m-%d"),
        "recorded_at": recorded_at_et.isoformat(),
        "recorded_time_et": format_time_et(recorded_at),
        "status": args.status,
        "summary": args.summary,
        "ran": args.ran or [],
        "result": args.result,
        "next": args.next,
    }

    deduped = [
        item
        for item in entries
        if not (
            isinstance(item, dict)
            and str(item.get("recorded_at", "")) == entry["recorded_at"]
            and str(item.get("status", "")) == entry["status"]
        )
    ]
    deduped.insert(0, entry)
    payload["entries"] = deduped[: args.keep]
    payload["updated_at"] = recorded_at_et.isoformat()
    payload["updated_time_et"] = format_time_et(recorded_at)
    write_log(path, payload)
    print(f"Updated automation daily log at {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("append", help="prepend a public-safe entry")
    p.add_argument("--path", default=str(DEFAULT_PATH))
    p.add_argument("--recorded-at", required=True, help="ISO timestamp for the event")
    p.add_argument("--status", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--ran", action="append", default=[], help="bullet item; may be repeated")
    p.add_argument("--result", required=True)
    p.add_argument("--next", required=True)
    p.add_argument("--keep", type=int, default=30, help="max entries to retain")
    p.set_defaults(func=cmd_append)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
