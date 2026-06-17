#!/usr/bin/env python3
"""Build a timestamped CTS automation status board.

The script reads automation/weekly-process.json, detects known private/public
artifacts, combines them with an operator ledger, and writes a Markdown status
board showing run evidence, current status, coverage, and redundancies.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import glob
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "automation" / "weekly-process.json"
DEFAULT_STATUS_DIR = ROOT / "data" / "private" / "automation-status"
VALID_RECORD_STATUSES = {
    "passed",
    "review_required",
    "blocked",
    "failed",
    "planned",
    "running",
    "not_due",
}
STATUS_RANK = {
    "failed": 0,
    "blocked": 1,
    "missing": 2,
    "stale": 3,
    "review_required": 4,
    "running": 5,
    "planned": 6,
    "not_due": 7,
    "passed": 8,
}
TIMESTAMP_FIELDS = ("generated_at", "collected_at", "created_at", "updated_at", "ended_at", "started_at")


@dataclass
class EvidenceResult:
    status: str
    timestamp: datetime | None
    label: str
    detail: str
    review_reason: str = ""
    next_action: str = ""


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def now_iso() -> str:
    return now_utc().isoformat()


def parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime | None) -> str:
    if not value:
        return "none"
    return value.replace(microsecond=0).isoformat()


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ledger_path(week: str, status_dir: Path) -> Path:
    return status_dir / f"{week}-ledger.json"


def load_ledger(week: str, status_dir: Path) -> dict[str, Any]:
    path = ledger_path(week, status_dir)
    if not path.exists():
        return {"week": week, "created_at": now_iso(), "records": []}
    data = load_json(path)
    if "records" not in data or not isinstance(data["records"], list):
        raise SystemExit(f"{path} does not contain a records list.")
    return data


def latest_record(records: list[dict[str, Any]], automation_id: str) -> dict[str, Any] | None:
    matches = [record for record in records if record.get("id") == automation_id]
    if not matches:
        return None

    def record_key(record: dict[str, Any]) -> datetime:
        return (
            parse_timestamp(record.get("ended_at"))
            or parse_timestamp(record.get("started_at"))
            or parse_timestamp(record.get("recorded_at"))
            or datetime.min.replace(tzinfo=timezone.utc)
        )

    return sorted(matches, key=record_key)[-1]


def csv_latest_timestamp(path: Path) -> tuple[datetime | None, int]:
    latest: datetime | None = None
    row_count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row_count += 1
            for field in TIMESTAMP_FIELDS:
                parsed = parse_timestamp(row.get(field))
                if parsed and (latest is None or parsed > latest):
                    latest = parsed
    return latest, row_count


def file_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)


def json_status(path: Path, data: Any) -> tuple[str, str, str, datetime | None]:
    timestamp = None
    status = "passed"
    reason = ""
    next_action = ""
    if isinstance(data, dict):
        for field in TIMESTAMP_FIELDS:
            timestamp = parse_timestamp(data.get(field))
            if timestamp:
                break
        duplicate_count = data.get("duplicate_email_count")
        duplicate_blockers = data.get("duplicate_blockers")
        if isinstance(duplicate_count, int) and duplicate_count > 0:
            status = "blocked"
            reason = "Duplicate email records are present."
        if isinstance(duplicate_blockers, list) and duplicate_blockers:
            status = "blocked"
            reason = "Duplicate blockers are present: " + ", ".join(str(item) for item in duplicate_blockers)
        if status != "blocked" and data.get("human_review_required"):
            status = "review_required"
            reason = str(data.get("human_review_reason") or "Human review required.")
            next_action = str(data.get("human_review_next_action") or "")
        if status != "blocked" and data.get("failed"):
            status = "failed"
            reason = str(data.get("error") or "Artifact reports failure.")
    return status, reason, next_action, timestamp


def artifact_result(path: Path, label: str) -> EvidenceResult:
    if not path.exists():
        return EvidenceResult("missing", None, label, "not found")
    timestamp: datetime | None = None
    status = "passed"
    reason = ""
    next_action = ""
    detail = "found"
    try:
        if path.suffix.lower() == ".json":
            data = load_json(path)
            status, reason, next_action, timestamp = json_status(path, data)
            if isinstance(data, dict):
                fields = []
                for key in ("records_seen", "accepted", "rejected", "duplicate_email_count", "desired_contacts", "current_count"):
                    if key in data:
                        fields.append(f"{key}={data[key]}")
                if fields:
                    detail = ", ".join(fields)
            elif isinstance(data, list):
                detail = f"{len(data)} rows"
        elif path.suffix.lower() == ".csv":
            timestamp, row_count = csv_latest_timestamp(path)
            detail = f"{row_count} rows"
        else:
            detail = "found"
    except Exception as exc:  # noqa: BLE001 - status board should report malformed evidence.
        return EvidenceResult("failed", file_mtime(path), label, f"could not read evidence: {exc}")
    if timestamp is None:
        timestamp = file_mtime(path)
    return EvidenceResult(status, timestamp, label, detail, reason, next_action)


def expand_artifacts(evidence: dict[str, Any], week: str) -> list[Path]:
    if evidence["kind"] == "artifact":
        raw_path = str(evidence["path"]).format(week=week)
        return [ROOT / raw_path]
    if evidence["kind"] == "artifact_glob":
        pattern = str(ROOT / str(evidence["glob"]).format(week=week))
        return [Path(match) for match in sorted(glob.glob(pattern))]
    return []


def record_result(record: dict[str, Any] | None, required: bool) -> EvidenceResult:
    if not record:
        status = "missing" if required else "passed"
        return EvidenceResult(status, None, "ledger", "no manual record")
    status = str(record.get("status") or "missing")
    timestamp = parse_timestamp(record.get("ended_at")) or parse_timestamp(record.get("started_at")) or parse_timestamp(record.get("recorded_at"))
    detail_parts = []
    if record.get("note"):
        detail_parts.append(str(record["note"]))
    artifacts = record.get("artifacts") or []
    if artifacts:
        detail_parts.append("artifacts: " + ", ".join(str(item) for item in artifacts))
    detail = "; ".join(detail_parts) if detail_parts else "recorded"
    return EvidenceResult(status, timestamp, "ledger", detail)


def evaluate_evidence_item(evidence: dict[str, Any], week: str, latest: dict[str, Any] | None) -> list[EvidenceResult]:
    kind = evidence.get("kind")
    required = bool(evidence.get("required"))
    if kind == "record":
        return [record_result(latest, required)]
    if kind in {"artifact", "artifact_glob"}:
        paths = expand_artifacts(evidence, week)
        label = str(evidence.get("path") or evidence.get("glob"))
        if not paths:
            status = "missing" if required else "passed"
            return [EvidenceResult(status, None, label, "not found")]
        results = [artifact_result(path, relative_path(path)) for path in paths]
        if kind == "artifact_glob":
            results = sorted(
                results,
                key=lambda item: item.timestamp or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
            return [results[0]]
        return results
    if kind == "any_of":
        option_results = []
        for option in evidence.get("options", []):
            results = evaluate_evidence_item(option, week, latest)
            option_status = worst_status([item.status for item in results])
            option_timestamp = max((item.timestamp for item in results if item.timestamp), default=None)
            option_label = " + ".join(item.label for item in results)
            option_detail = "; ".join(f"{item.label}: {item.status} ({item.detail})" for item in results)
            review_reason = next((item.review_reason for item in results if item.review_reason), "")
            next_action = next((item.next_action for item in results if item.next_action), "")
            option_results.append(
                EvidenceResult(option_status, option_timestamp, option_label, option_detail, review_reason, next_action)
            )
        if not option_results:
            status = "missing" if required else "passed"
            return [EvidenceResult(status, None, "any_of", "no options configured")]
        chosen = sorted(
            option_results,
            key=lambda item: (
                STATUS_RANK.get(item.status, -1),
                item.timestamp or datetime.min.replace(tzinfo=timezone.utc),
            ),
            reverse=True,
        )[0]
        label = "any_of"
        detail = f"satisfied by {chosen.label}: {chosen.detail}"
        if chosen.status == "missing":
            detail = "none of the acceptable evidence options was found"
        return [EvidenceResult(chosen.status, chosen.timestamp, label, detail, chosen.review_reason, chosen.next_action)]
    status = "missing" if required else "passed"
    return [EvidenceResult(status, None, str(kind or "unknown"), "unsupported evidence kind")]


def worst_status(statuses: list[str]) -> str:
    if not statuses:
        return "missing"
    return sorted(statuses, key=lambda item: STATUS_RANK.get(item, -1))[0]


def apply_freshness(status: str, timestamp: datetime | None, max_age_hours: int | None, generated_at: datetime) -> str:
    if status not in {"passed", "review_required"} or not timestamp or not max_age_hours:
        return status
    age_hours = (generated_at - timestamp).total_seconds() / 3600
    if age_hours > max_age_hours:
        return "stale"
    return status


def evaluate_automation(
    automation: dict[str, Any],
    week: str,
    records: list[dict[str, Any]],
    generated_at: datetime,
) -> dict[str, Any]:
    evidence_results: list[EvidenceResult] = []
    latest = latest_record(records, str(automation["id"]))
    for evidence in automation.get("evidence", []):
        evidence_results.extend(evaluate_evidence_item(evidence, week, latest))
    max_age = automation.get("max_age_hours")
    status = worst_status([item.status for item in evidence_results])
    timestamp = max(
        (item.timestamp for item in evidence_results if item.timestamp),
        default=None,
    )
    status = apply_freshness(status, timestamp, int(max_age) if max_age else None, generated_at)
    review_reasons = [item.review_reason for item in evidence_results if item.review_reason]
    next_actions = [item.next_action for item in evidence_results if item.next_action]
    return {
        "id": automation["id"],
        "title": automation["title"],
        "phase": automation["phase"],
        "required": bool(automation.get("required")),
        "status": status,
        "timestamp": timestamp,
        "evidence": evidence_results,
        "review_reason": review_reasons[0] if review_reasons else "",
        "next_action": next_actions[0] if next_actions else "",
        "operator_note": automation.get("operator_note", ""),
        "covers": automation.get("covers", []),
        "redundancy_groups": automation.get("redundancy_groups", []),
    }


def filter_automations(manifest: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    return [
        automation
        for automation in manifest.get("automations", [])
        if scope in automation.get("scopes", [])
    ]


def status_summary(results: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for result in results:
        summary[result["status"]] = summary.get(result["status"], 0) + 1
    return dict(sorted(summary.items(), key=lambda item: STATUS_RANK.get(item[0], -1)))


def has_run_evidence(result: dict[str, Any]) -> bool:
    if result["status"] in {"missing", "planned", "not_due"}:
        return False
    return any(item.timestamp for item in result["evidence"])


def markdown_escape(value: Any) -> str:
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "\\|")


def evidence_summary(result: dict[str, Any]) -> str:
    chunks = []
    for item in result["evidence"]:
        if item.status == "passed" and item.detail == "no manual record":
            continue
        label = item.label
        detail = item.detail
        chunks.append(f"{label}: {item.status} ({detail})")
    return "; ".join(chunks) if chunks else "none"


def coverage_rows(
    manifest: dict[str, Any],
    scope: str,
    result_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    rows = []
    automation_ids_in_scope = {automation["id"] for automation in filter_automations(manifest, scope)}
    for area in manifest.get("coverage_areas", []):
        if scope not in area.get("scopes", []):
            continue
        required_ids = [item for item in area.get("required_automation_ids", []) if item in automation_ids_in_scope]
        if not required_ids:
            continue
        missing_definition = [item for item in required_ids if item not in result_by_id]
        statuses = [result_by_id[item]["status"] for item in required_ids if item in result_by_id]
        missing_runs = [item for item in required_ids if result_by_id.get(item, {}).get("status") in {"missing", "stale"}]
        active_review = [item for item in required_ids if result_by_id.get(item, {}).get("status") == "review_required"]
        blocked = [item for item in required_ids if result_by_id.get(item, {}).get("status") in {"blocked", "failed"}]
        if missing_definition:
            coverage_status = "definition gap"
        elif blocked:
            coverage_status = "blocked"
        elif missing_runs:
            coverage_status = "missing evidence"
        elif active_review:
            coverage_status = "review required"
        else:
            coverage_status = "covered"
        redundancy_groups = area.get("redundancy_groups", [])
        redundancy_status = "documented" if len(redundancy_groups) >= 1 else "gap"
        rows.append(
            {
                "area": area["title"],
                "coverage_status": coverage_status,
                "required_ids": ", ".join(required_ids),
                "current_statuses": ", ".join(statuses),
                "redundancy": f"{redundancy_status}: {area.get('redundancy_reason', '')}",
            }
        )
    return rows


def build_markdown(
    manifest: dict[str, Any],
    week: str,
    scope: str,
    results: list[dict[str, Any]],
    generated_at: datetime,
    ledger: dict[str, Any],
    status_dir: Path,
) -> str:
    result_by_id = {result["id"]: result for result in results}
    summary = status_summary(results)
    required_count = len([result for result in results if result["required"]])
    evidenced_count = len([result for result in results if result["required"] and has_run_evidence(result)])
    missing_count = summary.get("missing", 0) + summary.get("stale", 0)
    review_count = summary.get("review_required", 0)
    blocked_count = summary.get("blocked", 0) + summary.get("failed", 0)
    all_evidenced = missing_count == 0
    all_healthy = blocked_count == 0 and review_count == 0 and missing_count == 0
    lines = [
        f"# CTS Automation Status: {week}",
        "",
        f"- Generated at: {format_timestamp(generated_at)}",
        f"- Scope: {scope} - {manifest.get('scopes', {}).get(scope, '')}",
        f"- Ledger: {relative_path(ledger_path(week, status_dir))}",
        f"- Required run evidence: {evidenced_count}/{required_count} recorded",
        f"- All required automations/checks have evidence: {'yes' if all_evidenced else 'no'}",
        f"- All required statuses are clear: {'yes' if all_healthy else 'no'}",
        f"- Status counts: {', '.join(f'{key}={value}' for key, value in summary.items()) or 'none'}",
        "",
        "## Required Automation Status",
        "",
        "| Phase | Automation/check | Status | Last timestamp | Evidence | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        action = result["next_action"] or result["review_reason"] or result["operator_note"]
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(result["phase"]),
                    markdown_escape(f"{result['title']} ({result['id']})"),
                    markdown_escape(result["status"]),
                    markdown_escape(format_timestamp(result["timestamp"])),
                    markdown_escape(evidence_summary(result)),
                    markdown_escape(action),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Coverage And Redundancy",
            "",
            "| Process area | Coverage status | Required automations/checks | Current statuses | Redundancy |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in coverage_rows(manifest, scope, result_by_id):
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(row["area"]),
                    markdown_escape(row["coverage_status"]),
                    markdown_escape(row["required_ids"]),
                    markdown_escape(row["current_statuses"]),
                    markdown_escape(row["redundancy"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Manual Ledger Records",
            "",
        ]
    )
    records = ledger.get("records", [])
    if not records:
        lines.append("No manual ledger records yet.")
    else:
        lines.extend(["| Recorded at | ID | Status | Started | Ended | Note |", "| --- | --- | --- | --- | --- | --- |"])
        for record in records:
            lines.append(
                "| "
                + " | ".join(
                    [
                        markdown_escape(record.get("recorded_at", "")),
                        markdown_escape(record.get("id", "")),
                        markdown_escape(record.get("status", "")),
                        markdown_escape(record.get("started_at", "")),
                        markdown_escape(record.get("ended_at", "")),
                        markdown_escape(record.get("note", "")),
                    ]
                )
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def cmd_record(args: argparse.Namespace) -> int:
    manifest = load_json(Path(args.manifest))
    known_ids = {automation["id"] for automation in manifest.get("automations", [])}
    if args.id not in known_ids:
        raise SystemExit(f"Unknown automation/check id {args.id!r}. Run list to see valid IDs.")
    status_dir = Path(args.status_dir)
    ledger = load_ledger(args.week, status_dir)
    if not ledger_path(args.week, status_dir).exists():
        write_json(ledger_path(args.week, status_dir), ledger)
    status = args.status
    if status not in VALID_RECORD_STATUSES:
        raise SystemExit(f"Unsupported status {status!r}. Use one of: {', '.join(sorted(VALID_RECORD_STATUSES))}")
    recorded_at = now_iso()
    started_at = args.started_at or recorded_at
    ended_at = args.ended_at or (recorded_at if status not in {"planned", "running"} else "")
    record = {
        "id": args.id,
        "status": status,
        "recorded_at": recorded_at,
        "started_at": started_at,
        "ended_at": ended_at,
        "note": args.note or "",
        "artifacts": args.artifact or [],
    }
    ledger.setdefault("records", []).append(record)
    ledger["updated_at"] = recorded_at
    write_json(ledger_path(args.week, status_dir), ledger)
    print(f"Recorded {status} for {args.id} in {ledger_path(args.week, status_dir)}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    manifest = load_json(Path(args.manifest))
    valid_scopes = set(manifest.get("scopes", {}))
    if args.scope not in valid_scopes:
        raise SystemExit(f"Unsupported scope {args.scope!r}. Use one of: {', '.join(sorted(valid_scopes))}")
    status_dir = Path(args.status_dir)
    ledger = load_ledger(args.week, status_dir)
    if not ledger_path(args.week, status_dir).exists():
        write_json(ledger_path(args.week, status_dir), ledger)
    generated_at = now_utc()
    automations = filter_automations(manifest, args.scope)
    results = [
        evaluate_automation(automation, args.week, ledger.get("records", []), generated_at)
        for automation in automations
    ]
    markdown = build_markdown(manifest, args.week, args.scope, results, generated_at, ledger, status_dir)
    output = Path(args.output) if args.output else status_dir / f"{args.week}-{args.scope}-status.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    print(f"Wrote automation status report to {output}")
    if args.print:
        print(markdown)
    if args.fail_on_attention:
        statuses = {result["status"] for result in results if result["required"]}
        if statuses.intersection({"missing", "stale", "blocked", "failed", "review_required"}):
            return 2
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    manifest = load_json(Path(args.manifest))
    valid_scopes = set(manifest.get("scopes", {}))
    if args.scope not in valid_scopes:
        raise SystemExit(f"Unsupported scope {args.scope!r}. Use one of: {', '.join(sorted(valid_scopes))}")
    automations = filter_automations(manifest, args.scope)
    for automation in automations:
        print(f"{automation['id']}\t{automation['phase']}\t{automation['title']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="automation process manifest")
    parser.add_argument("--status-dir", default=str(DEFAULT_STATUS_DIR), help="private status ledger/report directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("list", help="list automation/check IDs for a scope")
    p.add_argument("--scope", default="full-cycle")
    p.set_defaults(func=cmd_list)

    p = subparsers.add_parser("record", help="append a manual status record to the private ledger")
    p.add_argument("--week", required=True, help="week id, e.g. week-003")
    p.add_argument("--id", required=True, help="automation/check id from the manifest")
    p.add_argument("--status", required=True, choices=sorted(VALID_RECORD_STATUSES))
    p.add_argument("--started-at", help="ISO timestamp; defaults to now")
    p.add_argument("--ended-at", help="ISO timestamp; defaults to now for terminal statuses")
    p.add_argument("--note", default="", help="short public-safe note")
    p.add_argument("--artifact", action="append", help="supporting artifact path; may be repeated")
    p.set_defaults(func=cmd_record)

    p = subparsers.add_parser("report", help="write a Markdown status board for a week and scope")
    p.add_argument("--week", required=True, help="week id, e.g. week-003")
    p.add_argument("--scope", default="full-cycle", help="launch, invitation, report, close, or full-cycle")
    p.add_argument("--output", help="optional Markdown output path")
    p.add_argument("--print", action="store_true", help="also print the Markdown report")
    p.add_argument("--fail-on-attention", action="store_true", help="exit 2 if required evidence is missing, stale, blocked, failed, or waiting on review")
    p.set_defaults(func=cmd_report)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
