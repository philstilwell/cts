#!/usr/bin/env python3
"""Operational hardening tools for the CTS weekly survey cycle.

The commands in this file are intentionally conservative:

- private inputs and generated contact files belong under data/private/;
- dry-run plans are the default for API-changing workflows;
- no command sends a SurveyOL or MailerLite campaign;
- public report generation remains in cts_report_pipeline.py.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import ssl
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_DIR = ROOT / "data" / "private"
MAILERLITE_API_BASE = "https://connect.mailerlite.com/api"
SURVEYOL_API_BASE = "https://api.surveyol.com/v1"
SUPPRESSION_STATUSES = ("unsubscribed", "bounced", "junk")
MAILERLITE_GROUP_STATUSES = ("active", "unsubscribed", "unconfirmed", "bounced", "junk")

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
    "Friendly Outreach List",
    "Friendly Outreach List?",
    "Friendly Outreach List = Yes",
    "Friendly?",
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


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
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


def api_empty(method: str, url: str, token: str) -> None:
    request = Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method=method,
    )
    try:
        with urlopen(request, timeout=60, context=ssl_context()) as response:
            response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"{method} {url} failed: {exc.reason}") from exc


def mailerlite_get_all(path: str, token: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    params = dict(params or {})
    data: list[dict[str, Any]] = []
    cursor = params.pop("cursor", None)
    while True:
        query = dict(params)
        if cursor:
            query["cursor"] = cursor
        sep = "&" if "?" in path else "?"
        url = f"{MAILERLITE_API_BASE}{path}"
        if query:
            url = f"{url}{sep}{urlencode(query)}"
        payload = api_json("GET", url, token)
        items = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(items, list):
            raise SystemExit(f"Unexpected MailerLite response for {path}: {payload}")
        data.extend(item for item in items if isinstance(item, dict))
        meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        cursor = meta.get("next_cursor") if isinstance(meta, dict) else None
        if not cursor:
            break
    return data


def mailerlite_get_pages(path: str, token: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    params = dict(params or {})
    page = int(params.pop("page", 1))
    data: list[dict[str, Any]] = []
    while True:
        query = {**params, "page": page}
        url = f"{MAILERLITE_API_BASE}{path}?{urlencode(query)}"
        payload = api_json("GET", url, token)
        items = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(items, list):
            raise SystemExit(f"Unexpected MailerLite response for {path}: {payload}")
        data.extend(item for item in items if isinstance(item, dict))
        meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        last_page = int(meta.get("last_page", page)) if isinstance(meta, dict) else page
        if page >= last_page:
            break
        page += 1
    return data


def subscriber_email(subscriber: dict[str, Any]) -> str:
    return normalize_email(str(subscriber.get("email", "")))


def subscriber_name_fields(subscriber: dict[str, Any]) -> tuple[str, str, str]:
    fields = subscriber.get("fields", {})
    fields = fields if isinstance(fields, dict) else {}
    first = str(fields.get("name") or subscriber.get("name") or "").strip()
    last = str(fields.get("last_name") or "").strip()
    full = f"{first} {last}".strip()
    return full, first, last


def mailerlite_group_subscribers(
    group_id: str,
    token: str,
    limit: int,
    statuses: tuple[str, ...] = MAILERLITE_GROUP_STATUSES,
) -> list[dict[str, Any]]:
    by_id_or_email: dict[str, dict[str, Any]] = {}
    for status in statuses:
        subscribers = mailerlite_get_all(
            f"/groups/{group_id}/subscribers",
            token,
            {"filter[status]": status, "limit": limit, "include": "groups"},
        )
        for subscriber in subscribers:
            key = str(subscriber.get("id") or subscriber_email(subscriber))
            if key:
                by_id_or_email[key] = subscriber
    return list(by_id_or_email.values())


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


def cmd_mailerlite_groups(args: argparse.Namespace) -> int:
    token = require_env("MAILERLITE_API_TOKEN")
    groups = mailerlite_get_pages("/groups", token, {"limit": args.limit})
    if args.output:
        rows = [
            {
                "id": group.get("id", ""),
                "name": group.get("name", ""),
                "active_count": group.get("active_count", ""),
                "unsubscribed_count": group.get("unsubscribed_count", ""),
                "bounced_count": group.get("bounced_count", ""),
                "junk_count": group.get("junk_count", ""),
            }
            for group in groups
        ]
        write_csv(Path(args.output), ["id", "name", "active_count", "unsubscribed_count", "bounced_count", "junk_count"], rows)
    else:
        print(json.dumps(groups, indent=2, ensure_ascii=False))
    return 0


def cmd_mailerlite_suppressions(args: argparse.Namespace) -> int:
    token = require_env("MAILERLITE_API_TOKEN")
    statuses = args.status or list(SUPPRESSION_STATUSES)
    rows: list[dict[str, str]] = []
    for status in statuses:
        subscribers = mailerlite_get_all(
            "/subscribers",
            token,
            {"filter[status]": status, "limit": args.limit},
        )
        for subscriber in subscribers:
            email = subscriber_email(subscriber)
            if not email:
                continue
            rows.append(
                status_suppression_row(
                    "mailerlite",
                    email,
                    status,
                    str(subscriber.get("id", "")),
                    str(subscriber.get("unsubscribed_at") or subscriber.get("updated_at") or ""),
                )
            )
    write_csv(Path(args.output), ["email", "source", "status", "source_id", "note", "collected_at"], rows)
    print(f"Wrote {len(rows)} MailerLite suppression rows to {args.output}")
    return 0


def cmd_mailerlite_group_snapshot(args: argparse.Namespace) -> int:
    token = require_env("MAILERLITE_API_TOKEN")
    subscribers = mailerlite_group_subscribers(args.group_id, token, args.limit)
    rows = []
    for subscriber in subscribers:
        full, first, last = subscriber_name_fields(subscriber)
        rows.append(
            {
                "id": subscriber.get("id", ""),
                "email": subscriber_email(subscriber),
                "status": subscriber.get("status", ""),
                "name": full,
                "first_name": first,
                "last_name": last,
                "updated_at": subscriber.get("updated_at", ""),
            }
        )
    write_csv(Path(args.output), ["id", "email", "status", "name", "first_name", "last_name", "updated_at"], rows)
    print(f"Wrote {len(rows)} MailerLite group subscriber rows to {args.output}")
    return 0


def cmd_mailerlite_sync_group(args: argparse.Namespace) -> int:
    token = require_env("MAILERLITE_API_TOKEN")
    _, send_rows = read_csv(Path(args.send_list))
    suppressions = read_suppression_files([Path(path) for path in args.suppression_csv])
    group_subscribers = mailerlite_group_subscribers(args.group_id, token, args.limit)
    current_by_email = {subscriber_email(item): item for item in group_subscribers if subscriber_email(item)}

    desired_by_email = {normalize_email(row.get("email")): row for row in send_rows if normalize_email(row.get("email"))}
    suppressed_current = sorted(email for email in current_by_email if email in suppressions)
    missing = sorted(email for email in desired_by_email if email not in current_by_email and email not in suppressions)
    extra = sorted(email for email in current_by_email if email not in desired_by_email and email not in suppressions)
    plan = {
        "generated_at": now_iso(),
        "dry_run": not args.apply,
        "group_id": args.group_id,
        "send_list": args.send_list,
        "desired_count": len(desired_by_email),
        "current_count": len(current_by_email),
        "missing_active_contacts": missing,
        "suppressed_group_contacts_to_remove": suppressed_current,
        "extra_group_contacts_not_in_send_list": extra,
        "remove_extra": bool(args.remove_extra),
        "actions": [],
    }

    if args.apply:
        for email in missing:
            row = desired_by_email[email]
            payload = {
                "email": email,
                "fields": {
                    "name": row.get("first_name") or row.get("name", ""),
                    "last_name": row.get("last_name", ""),
                },
                "groups": [args.group_id],
            }
            result = api_json("POST", f"{MAILERLITE_API_BASE}/subscribers", token, payload)
            plan["actions"].append({"action": "upsert_to_group", "email": email, "result_id": result.get("data", {}).get("id", "") if isinstance(result, dict) else ""})
        remove_emails = list(suppressed_current)
        if args.remove_extra:
            remove_emails.extend(extra)
        for email in sorted(set(remove_emails)):
            subscriber = current_by_email[email]
            subscriber_id = str(subscriber.get("id", ""))
            if not subscriber_id:
                continue
            api_empty("DELETE", f"{MAILERLITE_API_BASE}/subscribers/{subscriber_id}/groups/{args.group_id}", token)
            plan["actions"].append({"action": "remove_from_group", "email": email, "subscriber_id": subscriber_id})

    write_json(Path(args.plan_output), plan)
    print(f"Wrote MailerLite group sync plan to {args.plan_output}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to make API changes.")
    return 0


def cmd_surveyol_account(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    account = api_json("GET", f"{SURVEYOL_API_BASE}/account/me", token)
    print(json.dumps(account, indent=2, ensure_ascii=False))
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
    return 0


def cmd_surveyol_sync_contacts(args: argparse.Namespace) -> int:
    token = require_env("SURVEYOL_API_TOKEN")
    _, send_rows = read_csv(Path(args.send_list))
    contacts = surveyol_list("/contacts", token)
    current_by_email = {normalize_email(str(contact.get("email", ""))): contact for contact in contacts if normalize_email(str(contact.get("email", "")))}
    desired = {normalize_email(row.get("email")): row for row in send_rows if normalize_email(row.get("email"))}
    missing = sorted(email for email in desired if email not in current_by_email)
    existing = sorted(email for email in desired if email in current_by_email)
    plan = {
        "generated_at": now_iso(),
        "dry_run": not args.apply,
        "send_list": args.send_list,
        "current_contacts": len(current_by_email),
        "desired_contacts": len(desired),
        "missing_contacts_to_add": missing,
        "existing_contacts": existing,
        "actions": [],
    }
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
    if not args.apply:
        print("Dry run only. Re-run with --apply to add missing SurveyOL contacts.")
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

    p = subparsers.add_parser("mailerlite-groups", help="list MailerLite groups")
    p.add_argument("--output", help="optional CSV output")
    p.add_argument("--limit", type=int, default=1000)
    p.set_defaults(func=cmd_mailerlite_groups)

    p = subparsers.add_parser("mailerlite-suppressions", help="export MailerLite unsubscribed/bounced/junk subscribers")
    p.add_argument("--output", required=True)
    p.add_argument("--status", action="append", choices=["active", "unsubscribed", "unconfirmed", "bounced", "junk"], help="status to export; may be repeated")
    p.add_argument("--limit", type=int, default=1000)
    p.set_defaults(func=cmd_mailerlite_suppressions)

    p = subparsers.add_parser("mailerlite-group-snapshot", help="export subscribers currently in a MailerLite group")
    p.add_argument("--group-id", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--limit", type=int, default=1000)
    p.set_defaults(func=cmd_mailerlite_group_snapshot)

    p = subparsers.add_parser("mailerlite-sync-group", help="dry-run or apply MailerLite group alignment from a private send list")
    p.add_argument("--send-list", required=True)
    p.add_argument("--group-id", required=True)
    p.add_argument("--suppression-csv", action="append", default=[], help="suppression CSV; may be repeated")
    p.add_argument("--plan-output", required=True)
    p.add_argument("--remove-extra", action="store_true", help="also remove active group members not present in the send list")
    p.add_argument("--apply", action="store_true", help="make API changes; default is dry-run")
    p.add_argument("--limit", type=int, default=1000)
    p.set_defaults(func=cmd_mailerlite_sync_group)

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
    p.set_defaults(func=cmd_surveyol_contacts)

    p = subparsers.add_parser("surveyol-sync-contacts", help="dry-run or apply missing SurveyOL contact additions from a private send list")
    p.add_argument("--send-list", required=True)
    p.add_argument("--plan-output", required=True)
    p.add_argument("--apply", action="store_true", help="make API changes; default is dry-run")
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
    for env_file in args.env_file:
        load_env_file(Path(env_file))
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
