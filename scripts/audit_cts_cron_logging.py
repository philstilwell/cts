#!/usr/bin/env python3
"""Verify that CTS cron automations share the current process contract."""

from __future__ import annotations

import sys
from pathlib import Path


AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
REQUIRED_SNIPPETS = (
    'kind = "cron"',
    "CTS_PROCESS_COORDINATION.md",
    "data/public/automation-daily-log.json",
    "rebuild the static site",
    "push to the remote",
)

FORBIDDEN_SNIPPETS = (
    "Mailer" "Lite",
    "mailer" "lite",
    "MAILER" "LITE",
    "automate reminders" " within " "12 " "days",
    "Reminder Follow-up setting is" " set" " to " "automate reminders",
    "surveyol." "reminder-followup-configured",
)


def main() -> int:
    paths = sorted(AUTOMATIONS_DIR.glob("cts-*/automation.toml"))
    if not paths:
        print(f"No CTS automation definitions found under {AUTOMATIONS_DIR}")
        return 1

    failures: list[tuple[Path, list[str], list[str]]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
        forbidden = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
        if missing or forbidden:
            failures.append((path, missing, forbidden))

    if failures:
        for path, missing, forbidden in failures:
            print(f"FAIL {path}")
            for snippet in missing:
                print(f"  missing: {snippet}")
            for snippet in forbidden:
                print(f"  forbidden: {snippet}")
        return 2

    print(f"PASS {len(paths)} CTS cron automation definitions share the current process contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
