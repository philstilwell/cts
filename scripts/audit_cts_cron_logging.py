#!/usr/bin/env python3
"""Verify that all CTS cron automations require public automation-log updates."""

from __future__ import annotations

import sys
from pathlib import Path


AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
REQUIRED_SNIPPETS = (
    'kind = "cron"',
    "data/public/automation-daily-log.json",
    "rebuild the static site",
    "push to the remote",
)


def main() -> int:
    paths = sorted(AUTOMATIONS_DIR.glob("cts-*/automation.toml"))
    if not paths:
        print(f"No CTS automation definitions found under {AUTOMATIONS_DIR}")
        return 1

    failures: list[tuple[Path, list[str]]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
        if missing:
            failures.append((path, missing))

    if failures:
        for path, missing in failures:
            print(f"FAIL {path}")
            for snippet in missing:
                print(f"  missing: {snippet}")
        return 2

    print(f"PASS {len(paths)} CTS cron automation definitions require public automation-log updates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
