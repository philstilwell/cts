#!/usr/bin/env python3
"""Operational hardening tools for the CTS weekly survey cycle.

The commands in this file are intentionally conservative:

- private inputs and generated contact files belong under data/private/;
- dry-run plans are the default for API-changing workflows;
- no command sends SurveyOL invitations;
- public report generation remains in cts_report_pipeline.py.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import ssl
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_DIR = ROOT / "data" / "private"
SURVEYOL_API_BASE = "https://api.surveyol.com/v1"
LOADED_ENV_FILES: list[str] = []
CTS_SYNC_ENV_VARS = (
    "SURVEYOL_API_TOKEN",
    "SURVEYOL_API_TOKEN_EXPIRES_AT",
)
SURVEYOL_TOKEN_EXPIRY_WARNING_DAYS = 14

EMAIL_FIELDS = (
    "Primary Email Address",
    "Primary Email",
    "Email Address",
    "Email",
    "E-mail",
    "email",
)
NAME_FIELDS = (
    "Name",
    "Full Name",
    "Full name",
    "Participant Name",
    "Contact Name",
)
FIRST_NAME_FIELDS = ("First Name", "First", "Given Name", "firstName", "first_name")
LAST_NAME_FIELDS = ("Last Name", "Last", "Family Name", "lastName", "last_name")
PARTICIPANT_ID_FIELDS = ("Participant ID", "Participant Id", "participant_id", "ID")
EMAIL_KEY_FIELDS = ("Email Key", "email_key", "EmailKey")
DO_NOT_EMAIL_FIELDS = (
    "Do Not Email?",
    "Do Not Email",
    "Do Not Contact?",
    "Do Not Contact",
    "Suppressed?",
    "Suppressed",
)
FRIENDLY_FIELDS = (
    "2024 Friendly Outreach List?",
    "2024 Friendly Outreach List",
    "Friendly Outreach List",
    "Friendly Outreach List?",
    "Friendly Outreach List = Yes",
    "Friendly?",
)
OUTREACH_STATUS_FIELDS = (
    "2026 Outreach Status",
    "Outreach Status",
    "Email Status",
    "Survey Outreach Status",
)
OUTREACH_HOLD_TERMS = (
    "hold",
    "pause",
    "paused",
    "suppress",
    "suppressed",
    "do not email",
    "do-not-email",
    "opt out",
    "opted out",
    "unsubscribe",
    "unsubscribed",
    "bounce",
    "bounced",
    "complaint",
)


def ssl_context() -> ssl.SSLContext | None:
    try:
        import certifi  # type: ignore
    except ImportError:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
    resolved = str(path.resolve())
    if resolved not in LOADED_ENV_FILES:
        LOADED_ENV_FILES.append(resolved)


def env_file_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def write_env_file(path: Path, values: dict[str, str], header_lines: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = list(header_lines or [])
    for key in sorted(values):
        value = values[key].replace("\n", " ").strip()
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def default_env_files() -> list[Path]:
    candidates = [
        ROOT / ".env",
        ROOT / ".env.local",
        ROOT / ".secrets" / "cts.env",
        ROOT / ".secrets" / "cts-ops.env",
        Path.home() / ".codex" / "cts.env",
    ]
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        candidates.append(Path(codex_home) / "cts.env")
    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        resolved = str(path)
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def load_default_env_files() -> list[str]:
    loaded_before = set(LOADED_ENV_FILES)
    for path in default_env_files():
        load_env_file(path)
    return [path for path in LOADED_ENV_FILES if path not in loaded_before]


def parse_iso_datetime(value: str) -> datetime | None:
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        searched = ", ".join(LOADED_ENV_FILES) if LOADED_ENV_FILES else "no env files loaded"
        raise SystemExit(
            f"Missing required environment variable: {name}. "
            f"Searched loaded env files: {searched}. "
            "Run `python3 scripts/cts_ops.py env-doctor --verify-api` to confirm the CTS ops environment."
        )
    return value


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def find_field(headers: list[str], candidates: tuple[str, ...] | list[str]) -> str | None:
    exact = {header: header for header in headers}
    normalized = {normalize_header(header): header for header in headers}
    for candidate in candidates:
        if candidate in exact:
            return candidate
        match = normalized.get(normalize_header(candidate))
        if match:
            return match
    return None


def truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "x", "do not email", "suppressed"}


def outreach_hold(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return any(term in normalized for term in OUTREACH_HOLD_TERMS)


def normalize_email(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def split_name(name: str) -> tuple[str, str]:
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    if not headers:
        raise SystemExit(f"{path} does not look like a CSV with headers.")
    return headers, rows


def require_email_field(headers: list[str], path: Path, explicit_field: str = "") -> str:
    if explicit_field:
        if explicit_field not in headers:
            raise SystemExit(f"{path} does not contain requested email column {explicit_field!r}. Headers: {headers}")
        return explicit_field
    email_field = find_field(headers, EMAIL_FIELDS)
    if not email_field:
        raise SystemExit(f"Could not find an email column in {path}. Headers: {headers}")
    return email_field


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_duplicate_email_report(
    path: Path,
    explicit_email_field: str = "",
    max_duplicates: int = 200,
) -> dict[str, Any]:
    headers, rows = read_csv(path)
    email_field = require_email_field(headers, path, explicit_email_field)
    name_field = find_field(headers, NAME_FIELDS)
    id_field = find_field(headers, ["id", "ID", "Contact ID", "contact_id", *PARTICIPANT_ID_FIELDS])
    source_row_field = find_field(headers, ["source_row", "Source Row", "Source XL Row"])
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        email = normalize_email(row.get(email_field))
        if not email:
            continue
        detail = {
            "csv_row": index,
            "email": email,
        }
        if name_field:
            detail["name"] = row.get(name_field, "")
        if id_field:
            detail["id"] = row.get(id_field, "")
        if source_row_field:
            detail["source_row"] = row.get(source_row_field, "")
        groups[email].append(detail)
    duplicates = [
        {"email": email, "count": len(items), "rows": items}
        for email, items in sorted(groups.items())
        if len(items) > 1
    ]
    return {
        "path": str(path),
        "email_field": email_field,
        "row_count": len(rows),
        "unique_email_count": len(groups),
        "duplicate_email_count": len(duplicates),
        "duplicate_row_count": sum(item["count"] for item in duplicates),
        "duplicates": duplicates[:max_duplicates],
        "duplicates_truncated": len(duplicates) > max_duplicates,
    }


def surveyol_contact_duplicate_report(contacts: list[dict[str, Any]], max_duplicates: int = 200) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for contact in contacts:
        email = normalize_email(str(contact.get("email", "")))
        if not email:
            continue
        first = str(contact.get("firstName", "") or "").strip()
        last = str(contact.get("lastName", "") or "").strip()
        groups[email].append(
            {
                "id": str(contact.get("id", "")),
                "email": email,
                "first_name": first,
                "last_name": last,
                "name": f"{first} {last}".strip(),
            }
        )
    duplicates = [
        {"email": email, "count": len(items), "contacts": items}
        for email, items in sorted(groups.items())
        if len(items) > 1
    ]
    return {
        "contact_row_count": len(contacts),
        "unique_email_count": len(groups),
        "duplicate_email_count": len(duplicates),
        "duplicate_contact_count": sum(item["count"] for item in duplicates),
        "duplicates": duplicates[:max_duplicates],
        "duplicates_truncated": len(duplicates) > max_duplicates,
    }


def surveyol_invitation_duplicate_report(
    payload: dict[str, Any],
    target_email: str = "",
    max_duplicates: int = 200,
) -> dict[str, Any]:
    invitations_raw = payload.get("invitations", [])
    if not isinstance(invitations_raw, list):
        raise SystemExit("Invitation extract does not contain a top-level invitations list.")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    status_counts: dict[str, int] = {}
    reminded_by_title: dict[str, int] = {}
    missing_email_count = 0
    target = normalize_email(target_email)
    target_invitations: list[dict[str, Any]] = []

    for index, invitation in enumerate(invitations_raw):
        if not isinstance(invitation, dict):
            continue
        email = normalize_email(str(invitation.get("email", "")))
        if not email:
            missing_email_count += 1
            continue
        statuses_raw = invitation.get("statuses", [])
        statuses = statuses_raw if isinstance(statuses_raw, list) else []
        normalized_statuses: list[dict[str, str]] = []
        for status in statuses:
            if not isinstance(status, dict):
                continue
            label = str(status.get("label", "")).strip()
            title = str(status.get("title", "")).strip()
            css_class = str(status.get("class", "")).strip()
            if label:
                status_counts[label] = status_counts.get(label, 0) + 1
            if label.lower() == "reminded":
                reminded_by_title[title] = reminded_by_title.get(title, 0) + 1
            normalized_statuses.append({"label": label, "title": title, "class": css_class})
        detail = {
            "extract_row": index,
            "email": email,
            "guid": str(invitation.get("guid", "")).strip(),
            "statuses": normalized_statuses,
        }
        groups[email].append(detail)
        if target and email == target:
            target_invitations.append(detail)

    duplicates = [
        {"email": email, "count": len(items), "invitations": items}
        for email, items in sorted(groups.items())
        if len(items) > 1
    ]
    return {
        "source": payload.get("source", ""),
        "survey_guid": payload.get("survey_guid", payload.get("surveyGuid", "")),
        "collector_title": payload.get("collector_title", payload.get("collectorTitle", "")),
        "collector_key": payload.get("collector_key", payload.get("collectorKey", "")),
        "invitation_row_count": sum(len(items) for items in groups.values()),
        "missing_email_count": missing_email_count,
        "unique_email_count": len(groups),
        "duplicate_email_count": len(duplicates),
        "duplicate_invitation_count": sum(item["count"] for item in duplicates),
        "duplicates": duplicates[:max_duplicates],
        "duplicates_truncated": len(duplicates) > max_duplicates,
        "status_counts": dict(sorted(status_counts.items())),
        "reminded_count": status_counts.get("Reminded", 0),
        "reminded_by_title": dict(sorted(reminded_by_title.items())),
        "target_email": target,
        "target_invitation_count": len(target_invitations) if target else None,
        "target_invitations": target_invitations if target else [],
    }


def normalize_live_extract_contact(contact: dict[str, Any]) -> dict[str, str]:
    first_name = str(contact.get("first_name", contact.get("firstName", "")) or "").strip()
    last_name = str(contact.get("last_name", contact.get("lastName", "")) or "").strip()
    email = normalize_email(str(contact.get("email", "")))
    contact_id = str(contact.get("id", "")) or email
    return {
        "id": contact_id,
        "email": email,
        "first_name": first_name,
        "last_name": re.sub(r"\s*\(\d+\)\s*$", "", last_name).strip(),
    }


def contacts_by_email(contacts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for contact in contacts:
        email = normalize_email(str(contact.get("email", "")))
        if email:
            grouped[email].append(contact)
    return dict(grouped)


def review_fields(required: bool, reason: str = "", next_action: str = "") -> dict[str, Any]:
    return {
        "human_review_required": bool(required),
        "human_review_reason": reason if required else "",
        "human_review_next_action": next_action if required else "",
    }


def print_review_notice(data: dict[str, Any]) -> None:
    if data.get("human_review_required"):
        reason = str(data.get("human_review_reason") or "Review this output before taking the next action.")
        next_action = str(data.get("human_review_next_action") or "")
        print(f"Human review required: {reason}")
        if next_action:
            print(f"Next action after review: {next_action}")


def api_json(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    body = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=60, context=ssl_context()) as response:
            data = response.read().decode("utf-8")
            if not data:
                return None
            return json.loads(data)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"{method} {url} failed: {exc.reason}") from exc


def status_suppression_row(source: str, email: str, status: str, source_id: str = "", note: str = "") -> dict[str, str]:
    return {
        "email": normalize_email(email),
        "source": source,
        "status": status,
        "source_id": source_id,
        "note": note,
        "collected_at": now_iso(),
    }


@dataclass
class RegistryRecord:
    source_row: int
    email: str
    name: str
    first_name: str
    last_name: str
    participant_id: str
    email_key: str
    do_not_email: bool
    friendly: bool | None
    outreach_status: str
    raw: dict[str, str]


def registry_records(path: Path, require_friendly: bool) -> tuple[list[RegistryRecord], dict[str, str | None]]:
    headers, rows = read_csv(path)
    email_field = find_field(headers, EMAIL_FIELDS)
    name_field = find_field(headers, NAME_FIELDS)
    first_name_field = find_field(headers, FIRST_NAME_FIELDS)
    last_name_field = find_field(headers, LAST_NAME_FIELDS)
    participant_id_field = find_field(headers, PARTICIPANT_ID_FIELDS)
    email_key_field = find_field(headers, EMAIL_KEY_FIELDS)
    do_not_email_field = find_field(headers, DO_NOT_EMAIL_FIELDS)
    friendly_field = find_field(headers, FRIENDLY_FIELDS)
    outreach_status_field = find_field(headers, OUTREACH_STATUS_FIELDS)

    if not email_field:
        raise SystemExit(f"Could not find an email column in {path}. Headers: {headers}")

    records: list[RegistryRecord] = []
    for index, row in enumerate(rows, start=2):
        email = normalize_email(row.get(email_field))
        first_name = row.get(first_name_field, "").strip() if first_name_field else ""
        last_name = row.get(last_name_field, "").strip() if last_name_field else ""
        name = row.get(name_field, "").strip() if name_field else ""
        if not name:
            name = f"{first_name} {last_name}".strip()
        if name and (not first_name or not last_name):
            inferred_first, inferred_last = split_name(name)
            first_name = first_name or inferred_first
            last_name = last_name or inferred_last
        friendly: bool | None = None
        if friendly_field:
            friendly = truthy(row.get(friendly_field))
        if require_friendly and friendly is False:
            continue
        records.append(
            RegistryRecord(
                source_row=index,
                email=email,
                name=name,
                first_name=first_name,
                last_name=last_name,
                participant_id=row.get(participant_id_field, "").strip() if participant_id_field else "",
                email_key=row.get(email_key_field, "").strip() if email_key_field else "",
                do_not_email=truthy(row.get(do_not_email_field)) if do_not_email_field else False,
                friendly=friendly,
                outreach_status=row.get(outreach_status_field, "").strip() if outreach_status_field else "",
                raw=row,
            )
        )

    fields = {
        "email": email_field,
        "name": name_field,
        "first_name": first_name_field,
        "last_name": last_name_field,
        "participant_id": participant_id_field,
        "email_key": email_key_field,
        "do_not_email": do_not_email_field,
        "friendly": friendly_field,
        "outreach_status": outreach_status_field,
    }
    return records, fields


def read_suppression_files(paths: list[Path]) -> dict[str, list[dict[str, str]]]:
    suppressions: dict[str, list[dict[str, str]]] = {}
    for path in paths:
        headers, rows = read_csv(path)
        email_field = find_field(headers, EMAIL_FIELDS)
        if not email_field:
            raise SystemExit(f"Could not find an email column in suppression file {path}")
        source_field = find_field(headers, ["source", "Source"])
        status_field = find_field(headers, ["status", "Status", "reason", "Reason"])
        for row in rows:
            email = normalize_email(row.get(email_field))
            if not email:
                continue
            entry = {
                "email": email,
                "source": row.get(source_field, path.name) if source_field else path.name,
                "status": row.get(status_field, "suppressed") if status_field else "suppressed",
                "path": str(path),
            }
            suppressions.setdefault(email, []).append(entry)
    return suppressions


def cmd_env_doctor(args: argparse.Namespace) -> int:
    required = [
        "SURVEYOL_API_TOKEN",
    ]
    optional: list[str] = []
    visible_default_files = [str(path) for path in default_env_files()]
    env_status = []
    missing_required = []
    discovered_key_sources: dict[str, list[str]] = {}
    for path in default_env_files():
        values = env_file_values(path)
        for key in set(values):
            discovered_key_sources.setdefault(key, []).append(str(path))
    for name in [*required, *optional]:
        present = bool(os.environ.get(name, "").strip())
        env_status.append(
            {
                "name": name,
                "required": name in required,
                "present": present,
                "discovered_in_files": discovered_key_sources.get(name, []),
            }
        )
        if name in required and not present:
            missing_required.append(name)

    api_checks: dict[str, Any] = {}
    verify_errors: list[str] = []
    token_expiry_at = parse_iso_datetime(os.environ.get("SURVEYOL_API_TOKEN_EXPIRES_AT", ""))
    token_expiry_status: dict[str, Any] | None = None
    expiry_review_reason = ""
    if token_expiry_at is not None:
        remaining = token_expiry_at - datetime.now(timezone.utc)
        warning_window = timedelta(days=SURVEYOL_TOKEN_EXPIRY_WARNING_DAYS)
        status = "ok"
        if remaining <= timedelta(0):
            status = "expired"
            expiry_review_reason = "The stored SurveyOL API token has expired."
        elif remaining <= warning_window:
            status = "expiring_soon"
            expiry_review_reason = (
                f"The stored SurveyOL API token expires within {SURVEYOL_TOKEN_EXPIRY_WARNING_DAYS} days."
            )
        token_expiry_status = {
            "present": True,
            "status": status,
            "expires_at": token_expiry_at.isoformat().replace("+00:00", "Z"),
            "days_remaining": round(remaining.total_seconds() / 86400, 2),
        }
    elif os.environ.get("SURVEYOL_API_TOKEN", "").strip():
        token_expiry_status = {
            "present": False,
            "status": "unknown",
            "expires_at": "",
            "days_remaining": None,
        }
        expiry_review_reason = (
            "The SurveyOL API token is present, but SURVEYOL_API_TOKEN_EXPIRES_AT is missing."
        )
    if args.verify_api and not missing_required:
        try:
            surveyol_account = api_json("GET", f"{SURVEYOL_API_BASE}/account/me", require_env("SURVEYOL_API_TOKEN"))
            api_checks["surveyol_account"] = {
                "ok": True,
                "email": surveyol_account.get("email", "") if isinstance(surveyol_account, dict) else "",
            }
        except SystemExit as exc:
            api_checks["surveyol_account"] = {"ok": False, "error": str(exc)}
            verify_errors.append(f"SurveyOL API check failed: {exc}")
    review_required = bool(missing_required or verify_errors or expiry_review_reason)
    next_action = ""
    if missing_required:
        next_action = (
            "Add the missing SurveyOL token to a discovered private env file such as .secrets/cts.env, "
            "then run `python3 scripts/cts_ops.py sync-env --target ~/.codex/cts.env` and rerun "
            "`python3 scripts/cts_ops.py env-doctor --verify-api`."
        )
    elif verify_errors:
        next_action = (
            "Repair the failing SurveyOL API token, mirror it with "
            "`python3 scripts/cts_ops.py sync-env --target ~/.codex/cts.env`, and rerun "
            "`python3 scripts/cts_ops.py env-doctor --verify-api`."
        )
    elif expiry_review_reason:
        next_action = (
            "Refresh the SurveyOL API token before the next cron window, set `SURVEYOL_API_TOKEN_EXPIRES_AT`, "
            "mirror both values with `python3 scripts/cts_ops.py sync-env --target ~/.codex/cts.env`, "
            "then rerun `python3 scripts/cts_ops.py env-doctor --verify-api`."
        )
    result = {
        "generated_at": now_iso(),
        **review_fields(
            review_required,
            expiry_review_reason
            or (
                "CTS ops environment is not ready for suppression reconciliation or API-backed hygiene commands."
                if review_required
                else ""
            ),
            next_action if review_required else "",
        ),
        "loaded_env_files": LOADED_ENV_FILES,
        "default_env_candidates": visible_default_files,
        "env": env_status,
        "api_checks": api_checks,
        "surveyol_token_expiry": token_expiry_status,
        "recommended_mirror_target": str(Path.home() / ".codex" / "cts.env"),
    }
    if args.json_output:
        write_json(Path(args.json_output), result)
        print(f"Wrote env doctor report to {args.json_output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    print_review_notice(result)
    return 0 if not review_required else 2


def cmd_surveyol_account(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    account = api_json("GET", f"{SURVEYOL_API_BASE}/account/me", token)
    print(json.dumps(account, indent=2, ensure_ascii=False))
    return 0


def cmd_sync_env(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser()
    current = env_file_values(target)
    values: dict[str, str] = {}
    missing: list[str] = []
    for key in CTS_SYNC_ENV_VARS:
        value = os.environ.get(key, "").strip()
        if value:
            values[key] = value
        elif key == "SURVEYOL_API_TOKEN":
            missing.append(key)
    if missing:
        raise SystemExit(
            "Cannot sync CTS env because required values are still missing from the loaded environment: "
            + ", ".join(missing)
        )
    if args.preserve_existing:
        for key, value in current.items():
            if key not in values:
                values[key] = value
    header_lines = [
        "# Mirrored by scripts/cts_ops.py sync-env",
        "# This file is a stable Codex-wide fallback for CTS automation env discovery.",
    ]
    write_env_file(target, values, header_lines)
    print(f"Wrote CTS env mirror to {target}")
    return 0


def surveyol_list(path: str, token: str) -> list[dict[str, Any]]:
    payload = api_json("GET", f"{SURVEYOL_API_BASE}{path}", token)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return [item for item in payload["data"] if isinstance(item, dict)]
    raise SystemExit(f"Unexpected SurveyOL response for {path}: {payload}")


def cmd_surveyol_surveys(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    surveys = surveyol_list("/surveys", token)
    write_json(Path(args.output), surveys)
    print(f"Wrote {len(surveys)} SurveyOL survey rows to {args.output}")
    return 0


def cmd_surveyol_snapshot(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    survey = api_json("GET", f"{SURVEYOL_API_BASE}/survey/{args.survey_id}", token)
    pages = surveyol_list(f"/survey/{args.survey_id}/pages", token)
    questions_by_page: dict[str, list[dict[str, Any]]] = {}
    for page in pages:
        page_id = str(page.get("id", ""))
        if not page_id:
            continue
        questions_by_page[page_id] = surveyol_list(f"/page/{page_id}/questions", token)
    collectors = surveyol_list(f"/survey/{args.survey_id}/collectors", token)
    responses = surveyol_list(f"/survey/{args.survey_id}/responses", token)
    payload = {
        "generated_at": now_iso(),
        "survey_id": args.survey_id,
        "survey": survey,
        "pages": pages,
        "questions_by_page": questions_by_page,
        "collectors": collectors,
        "responses": responses,
    }
    output = out_dir / f"{args.week}-surveyol-snapshot.json"
    write_json(output, payload)
    question_count = sum(len(value) for value in questions_by_page.values())
    print(
        f"Wrote SurveyOL snapshot with {len(pages)} pages, {question_count} questions, "
        f"{len(collectors)} collectors, and {len(responses)} responses to {output}"
    )
    return 0


def cmd_surveyol_contacts(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    contacts = surveyol_list("/contacts", token)
    rows = [
        {
            "id": contact.get("id", ""),
            "email": normalize_email(str(contact.get("email", ""))),
            "first_name": contact.get("firstName", ""),
            "last_name": contact.get("lastName", ""),
        }
        for contact in contacts
    ]
    write_csv(Path(args.output), ["id", "email", "first_name", "last_name"], rows)
    print(f"Wrote {len(rows)} SurveyOL contacts to {args.output}")
    duplicate_audit = surveyol_contact_duplicate_report(contacts, args.max_duplicates)
    if args.audit_output:
        audit = {
            "generated_at": now_iso(),
            **review_fields(
                duplicate_audit["duplicate_email_count"] > 0,
                "SurveyOL contacts contain duplicate email addresses. Do not import recipients or send invitations until these contact records are merged or deleted.",
                "Resolve duplicate contacts in SurveyOL, then re-run this contact export and confirm duplicate_email_count is 0.",
            ),
            **duplicate_audit,
        }
        write_json(Path(args.audit_output), audit)
        print(f"Wrote SurveyOL contact duplicate audit to {args.audit_output}")
        print_review_notice(audit)
    elif duplicate_audit["duplicate_email_count"]:
        print(f"Warning: found {duplicate_audit['duplicate_email_count']} duplicate SurveyOL contact email(s).")
    return 0


def cmd_surveyol_live_extract(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input_json))
    raw_contacts = payload.get("contacts", []) if isinstance(payload, dict) else []
    if not isinstance(raw_contacts, list):
        raise SystemExit(f"{args.input_json} does not contain a top-level contacts list.")
    contacts = [normalize_live_extract_contact(item) for item in raw_contacts if isinstance(item, dict)]
    contacts = [item for item in contacts if item["email"]]
    write_csv(Path(args.output), ["id", "email", "first_name", "last_name"], contacts)
    print(f"Wrote {len(contacts)} SurveyOL contacts from live extract to {args.output}")
    duplicate_audit = surveyol_contact_duplicate_report(
        [
            {
                "id": item["id"],
                "email": item["email"],
                "firstName": item["first_name"],
                "lastName": item["last_name"],
            }
            for item in contacts
        ],
        args.max_duplicates,
    )
    if args.audit_output:
        audit = {
            "generated_at": now_iso(),
            **review_fields(
                duplicate_audit["duplicate_email_count"] > 0,
                "SurveyOL contacts contain duplicate email addresses. Do not import recipients or send invitations until these contact records are merged or deleted.",
                "Resolve duplicate contacts in SurveyOL, then re-run this live extract and confirm duplicate_email_count is 0.",
            ),
            **duplicate_audit,
            "source": "surveyol live extract",
            "input_json": args.input_json,
        }
        write_json(Path(args.audit_output), audit)
        print(f"Wrote SurveyOL live-extract duplicate audit to {args.audit_output}")
        print_review_notice(audit)
    raw_invitations = payload.get("invitations", []) if isinstance(payload, dict) else []
    if args.next_batch_output or args.summary_output:
        invited = {
            normalize_email(str(item.get("email", "")))
            for item in raw_invitations
            if isinstance(item, dict) and normalize_email(str(item.get("email", "")))
        }
        remaining = [item for item in contacts if item["email"] not in invited]
        if args.next_batch_output:
            write_csv(
                Path(args.next_batch_output),
                ["id", "email", "first_name", "last_name"],
                remaining[: args.next_batch_size],
            )
            print(
                f"Wrote {min(len(remaining), args.next_batch_size)} remaining live-extract contacts "
                f"to {args.next_batch_output}"
            )
        if args.summary_output:
            summary = {
                "generated_at": now_iso(),
                "input_json": args.input_json,
                "contact_row_count": len(contacts),
                "invitation_row_count": len(invited),
                "remaining_contact_count": len(remaining),
                "next_batch_size": min(len(remaining), args.next_batch_size),
                "next_batch_emails": [item["email"] for item in remaining[: args.next_batch_size]],
                **review_fields(
                    duplicate_audit["duplicate_email_count"] > 0,
                    "SurveyOL live extract still contains duplicate emails.",
                    "Resolve duplicate SurveyOL contacts before using the next batch output.",
                ),
            }
            write_json(Path(args.summary_output), summary)
            print(f"Wrote SurveyOL live-extract summary to {args.summary_output}")
    return 0


def cmd_surveyol_sync_contacts(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    send_list_path = Path(args.send_list)
    send_headers, send_rows = read_csv(send_list_path)
    send_email_field = require_email_field(send_headers, send_list_path)
    send_duplicate_audit = csv_duplicate_email_report(send_list_path, max_duplicates=args.max_duplicates)
    contacts = surveyol_list("/contacts", token)
    current_grouped = contacts_by_email(contacts)
    current_by_email = {email: items[0] for email, items in current_grouped.items()}
    current_duplicate_audit = surveyol_contact_duplicate_report(contacts, args.max_duplicates)
    desired = {normalize_email(row.get(send_email_field)): row for row in send_rows if normalize_email(row.get(send_email_field))}
    missing = sorted(email for email in desired if email not in current_grouped)
    existing = sorted(email for email in desired if email in current_grouped)
    duplicate_blockers = []
    if send_duplicate_audit["duplicate_email_count"]:
        duplicate_blockers.append("send_list_duplicate_emails")
    if current_duplicate_audit["duplicate_email_count"]:
        duplicate_blockers.append("surveyol_duplicate_contacts")
    review_required = bool(duplicate_blockers) or not args.apply
    if duplicate_blockers:
        review_reason = (
            "Duplicate emails exist in the SurveyOL send path. Stop invitation sends until the send list and SurveyOL contact table "
            "both have at most one row per normalized email address."
        )
        review_next_action = (
            "De-duplicate the listed email rows or SurveyOL contact records, then re-run this command. Do not use --apply while "
            "duplicate_blockers is non-empty."
        )
    else:
        review_reason = "This is a dry-run SurveyOL contact sync plan; review missing contacts before adding them to SurveyOL."
        review_next_action = (
            "If the plan is correct, re-run the same command with --apply. Correct the send list first if any contact should not be added."
        )
    plan = {
        "generated_at": now_iso(),
        "dry_run": not args.apply,
        **review_fields(
            review_required,
            review_reason,
            review_next_action,
        ),
        "send_list": args.send_list,
        "send_list_email_field": send_email_field,
        "current_contact_rows": len(contacts),
        "current_unique_contacts": len(current_by_email),
        "desired_contacts": len(desired),
        "missing_contacts_to_add": missing,
        "existing_contacts": existing,
        "duplicate_blockers": duplicate_blockers,
        "send_list_duplicate_audit": send_duplicate_audit,
        "surveyol_contact_duplicate_audit": current_duplicate_audit,
        "actions": [],
    }
    if args.apply and duplicate_blockers:
        write_json(Path(args.plan_output), plan)
        print(f"Wrote blocked SurveyOL contact sync plan to {args.plan_output}")
        print_review_notice(plan)
        raise SystemExit("Blocked SurveyOL contact sync because duplicate email records are present.")
    if args.apply:
        for email in missing:
            row = desired[email]
            payload = {
                "email": email,
                "firstName": row.get("first_name") or split_name(row.get("name", ""))[0],
                "lastName": row.get("last_name") or split_name(row.get("name", ""))[1],
            }
            result = api_json("POST", f"{SURVEYOL_API_BASE}/contact", token, payload)
            plan["actions"].append({"action": "add_contact", "email": email, "id": result.get("id", "") if isinstance(result, dict) else ""})
    write_json(Path(args.plan_output), plan)
    print(f"Wrote SurveyOL contact sync plan to {args.plan_output}")
    print_review_notice(plan)
    if not args.apply:
        print("Dry run only. Re-run with --apply to add missing SurveyOL contacts.")
    return 0


def cmd_audit_email_duplicates(args: argparse.Namespace) -> int:
    reports = [
        csv_duplicate_email_report(Path(path), args.email_field or "", args.max_duplicates)
        for path in args.csv
    ]
    duplicate_email_count = sum(report["duplicate_email_count"] for report in reports)
    duplicate_row_count = sum(report["duplicate_row_count"] for report in reports)
    audit = {
        "generated_at": now_iso(),
        **review_fields(
            duplicate_email_count > 0,
            "One or more contact CSVs contain duplicate normalized email addresses. Do not import this file or send invitations from it until it is de-duplicated.",
            "Keep exactly one intended recipient row per normalized email address, regenerate the CSV if needed, and re-run this audit.",
        ),
        "csv_count": len(reports),
        "duplicate_email_count": duplicate_email_count,
        "duplicate_row_count": duplicate_row_count,
        "reports": reports,
    }
    if args.output:
        write_json(Path(args.output), audit)
        print(f"Wrote duplicate email audit to {args.output}")
        print_review_notice(audit)
    else:
        print(json.dumps(audit, indent=2, ensure_ascii=False))
    if args.fail_on_duplicates and duplicate_email_count:
        return 2
    return 0


def cmd_audit_surveyol_invitations(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input_json))
    report = surveyol_invitation_duplicate_report(payload, args.target_email or "", args.max_duplicates)
    duplicate_email_count = report["duplicate_email_count"]
    audit = {
        "generated_at": now_iso(),
        **review_fields(
            duplicate_email_count > 0,
            "The SurveyOL invitation table contains duplicate normalized recipient email addresses. Disable or do not enable reminder follow-up until duplicate invitation rows are resolved.",
            "Cancel or otherwise resolve extra invitation rows in SurveyOL, re-extract invitation statistics, and re-run this audit before reminder-enabled sends.",
        ),
        "input_json": args.input_json,
        **report,
    }
    if args.output:
        write_json(Path(args.output), audit)
        print(f"Wrote SurveyOL invitation audit to {args.output}")
        print_review_notice(audit)
    else:
        print(json.dumps(audit, indent=2, ensure_ascii=False))
    if args.fail_on_duplicates and duplicate_email_count:
        return 2
    return 0


def cmd_build_send_list(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry_csv)
    records, field_map = registry_records(registry_path, args.require_friendly)
    suppressions = read_suppression_files([Path(path) for path in args.suppression_csv])

    accepted: list[RegistryRecord] = []
    rejected: list[dict[str, Any]] = []
    seen_emails: set[str] = set()
    for record in records:
        reasons: list[str] = []
        if not record.email:
            reasons.append("missing_email")
        if not record.name:
            reasons.append("missing_name")
        if record.do_not_email:
            reasons.append("registry_do_not_email")
        if outreach_hold(record.outreach_status):
            reasons.append("outreach_status_hold")
        if record.email in suppressions:
            reasons.append("global_suppression")
        if record.email and record.email in seen_emails:
            reasons.append("duplicate_email")
        if args.require_participant_id and not record.participant_id:
            reasons.append("missing_participant_id")
        if args.require_email_key and not record.email_key:
            reasons.append("missing_email_key")

        if reasons:
            rejected.append(
                {
                    "source_row": record.source_row,
                    "email": record.email,
                    "name": record.name,
                    "reasons": reasons,
                    "outreach_status": record.outreach_status,
                    "suppression_sources": suppressions.get(record.email, []),
                }
            )
            continue
        accepted.append(record)
        seen_emails.add(record.email)

    if args.limit:
        accepted = accepted[: args.limit]

    out_dir = Path(args.out_dir)
    send_list_path = out_dir / "send-lists" / f"{args.week}-surveyol-contacts.csv"
    crosswalk_path = out_dir / "contact-crosswalks" / f"{args.week}.csv"
    audit_path = out_dir / "audits" / f"{args.week}-send-list-audit.json"

    send_rows = [
        {
            "email": record.email,
            "first_name": record.first_name,
            "last_name": record.last_name,
            "name": record.name,
        }
        for record in accepted
    ]
    crosswalk_rows = [
        {
            "participant_id": record.participant_id,
            "email_key": record.email_key,
            "email": record.email,
            "name": record.name,
            "first_name": record.first_name,
            "last_name": record.last_name,
            "source_row": record.source_row,
            "week": args.week,
            "created_at": now_iso(),
        }
        for record in accepted
    ]
    write_csv(send_list_path, ["email", "first_name", "last_name", "name"], send_rows)
    write_csv(
        crosswalk_path,
        ["participant_id", "email_key", "email", "name", "first_name", "last_name", "source_row", "week", "created_at"],
        crosswalk_rows,
    )
    audit = {
        "generated_at": now_iso(),
        **review_fields(
            True,
            "Review accepted/rejected counts and rejected-record reasons before importing contacts or sending invitations.",
            "If the audit is acceptable, use the generated send list for SurveyOL contact import and keep the crosswalk private.",
        ),
        "week": args.week,
        "registry_csv": str(registry_path),
        "field_map": field_map,
        "require_friendly": args.require_friendly,
        "require_participant_id": args.require_participant_id,
        "require_email_key": args.require_email_key,
        "records_seen": len(records),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "suppressed_email_count": len(suppressions),
        "outputs": {
            "send_list": str(send_list_path),
            "crosswalk": str(crosswalk_path),
        },
        "reject_reasons": rejection_counts(rejected),
        "rejected_records": rejected[: args.audit_rejected_limit],
        "rejected_records_truncated": len(rejected) > args.audit_rejected_limit,
    }
    write_json(audit_path, audit)
    print(f"Wrote {len(send_rows)} send-list contacts to {send_list_path}")
    print(f"Wrote private crosswalk to {crosswalk_path}")
    print(f"Wrote audit to {audit_path}")
    print_review_notice(audit)
    return 0


def rejection_counts(rejected: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in rejected:
        for reason in item.get("reasons", []):
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def add_common_env(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env-file", action="append", default=[], help="optional env file to load before reading API tokens")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_env(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("audit-email-duplicates", help="audit one or more contact CSVs for duplicate normalized email addresses")
    p.add_argument("--csv", action="append", required=True, help="contact CSV to audit; may be repeated")
    p.add_argument("--email-field", default="", help="optional explicit email column name used for every CSV")
    p.add_argument("--output", help="optional JSON audit output")
    p.add_argument("--fail-on-duplicates", action="store_true", help="exit with status 2 if any duplicate email is found")
    p.add_argument("--max-duplicates", type=int, default=200)
    p.set_defaults(func=cmd_audit_email_duplicates)

    p = subparsers.add_parser(
        "audit-surveyol-invitations",
        help="audit a SurveyOL Email collector invitation extract for duplicate recipient email rows",
    )
    p.add_argument("--input-json", required=True, help="JSON payload extracted from the live SurveyOL send page")
    p.add_argument("--output", help="optional JSON audit output")
    p.add_argument("--target-email", default="", help="optional normalized-recipient drilldown to include in the report")
    p.add_argument("--fail-on-duplicates", action="store_true", help="exit with status 2 if any duplicate invitation email is found")
    p.add_argument("--max-duplicates", type=int, default=200)
    p.set_defaults(func=cmd_audit_surveyol_invitations)

    p = subparsers.add_parser("env-doctor", help="check CTS ops env discovery and optionally verify API access")
    p.add_argument("--verify-api", action="store_true", help="also verify SurveyOL API access when a token is present")
    p.add_argument("--json-output", help="optional JSON report output path")
    p.set_defaults(func=cmd_env_doctor)

    p = subparsers.add_parser("sync-env", help="mirror the loaded CTS env values into a stable private env file")
    p.add_argument("--target", default=str(Path.home() / ".codex" / "cts.env"))
    p.add_argument("--preserve-existing", action="store_true", help="keep unrelated keys already present in the target file")
    p.set_defaults(func=cmd_sync_env)

    p = subparsers.add_parser("surveyol-account", help="verify SurveyOL API token/account")
    p.set_defaults(func=cmd_surveyol_account)

    p = subparsers.add_parser("surveyol-surveys", help="snapshot SurveyOL survey list")
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_surveyol_surveys)

    p = subparsers.add_parser("surveyol-snapshot", help="snapshot a SurveyOL survey, collectors, and responses")
    p.add_argument("--survey-id", required=True)
    p.add_argument("--week", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_PRIVATE_DIR / "surveyol-api"))
    p.set_defaults(func=cmd_surveyol_snapshot)

    p = subparsers.add_parser("surveyol-contacts", help="export SurveyOL contacts to CSV")
    p.add_argument("--output", required=True)
    p.add_argument("--audit-output", help="optional JSON duplicate-email audit output")
    p.add_argument("--max-duplicates", type=int, default=200)
    p.set_defaults(func=cmd_surveyol_contacts)

    p = subparsers.add_parser(
        "surveyol-live-extract",
        help="materialize SurveyOL contact artifacts from a live browser extract JSON",
    )
    p.add_argument("--input-json", required=True, help="JSON payload extracted from the live SurveyOL send page")
    p.add_argument("--output", required=True, help="contact CSV output path")
    p.add_argument("--audit-output", help="optional JSON duplicate-email audit output")
    p.add_argument("--next-batch-output", help="optional CSV of remaining uninvited contacts")
    p.add_argument("--summary-output", help="optional JSON summary including remaining-contact counts")
    p.add_argument("--next-batch-size", type=int, default=100)
    p.add_argument("--max-duplicates", type=int, default=200)
    p.set_defaults(func=cmd_surveyol_live_extract)

    p = subparsers.add_parser("surveyol-sync-contacts", help="dry-run or apply missing SurveyOL contact additions from a private send list")
    p.add_argument("--send-list", required=True)
    p.add_argument("--plan-output", required=True)
    p.add_argument("--apply", action="store_true", help="make API changes; default is dry-run")
    p.add_argument("--max-duplicates", type=int, default=200)
    p.set_defaults(func=cmd_surveyol_sync_contacts)

    p = subparsers.add_parser("build-send-list", help="build a weekly SurveyOL send list and private crosswalk from CTS registry CSV")
    p.add_argument("--week", required=True, help="week id, e.g. week-003")
    p.add_argument("--registry-csv", required=True, help="private CTS 2026 registry CSV export")
    p.add_argument("--suppression-csv", action="append", default=[], help="suppression CSV; may be repeated")
    p.add_argument("--out-dir", default=str(DEFAULT_PRIVATE_DIR))
    p.add_argument("--require-friendly", action="store_true", help="include only rows marked as friendly outreach when such a field exists")
    p.add_argument("--require-participant-id", action="store_true")
    p.add_argument("--require-email-key", action="store_true")
    p.add_argument("--limit", type=int, help="optional cap for test batches")
    p.add_argument("--audit-rejected-limit", type=int, default=100)
    p.set_defaults(func=cmd_build_send_list)

    args = parser.parse_args()
    load_default_env_files()
    for env_file in args.env_file:
        load_env_file(Path(env_file))
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
