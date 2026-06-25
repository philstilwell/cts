#!/usr/bin/env python3
"""Build, publish, and verify the GitHub Pages static site branch."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRANCH = "gh-pages"
DEFAULT_VERIFY_URL = "https://christianthoughtsurvey.com/automation-daily-log/"
PUBLISH_PATHS = (
    "404.html",
    "CNAME",
    "assets",
    "automation-daily-log",
    "contact",
    "email-confirmation",
    "herding-cats",
    "index.html",
    "newsletter",
    "overview",
    "participant-pool",
    "previous-results-archive",
    "privacy-data-release",
    "robots.txt",
    "sitemap.xml",
    "weekly-survey-reports",
    "data/public",
)
FORBIDDEN_PUBLISH_PARTS = {
    "data/private",
    "data/fixtures",
    "data/tmp",
    ".secrets",
    ".env",
    ".env.local",
}


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="")


def ensure_clean_publish_paths(paths: tuple[str, ...]) -> None:
    for raw_path in paths:
        normalized = raw_path.rstrip("/")
        if normalized in FORBIDDEN_PUBLISH_PARTS or normalized.startswith("data/private"):
            raise SystemExit(f"Refusing to publish forbidden path: {raw_path}")
        source = ROOT / raw_path
        if not source.exists():
            raise SystemExit(f"Publish source does not exist: {raw_path}")


def copy_publish_paths(worktree: Path, paths: tuple[str, ...]) -> None:
    for raw_path in paths:
        source = ROOT / raw_path
        target = worktree / raw_path
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def reject_forbidden_files(worktree: Path) -> None:
    forbidden = []
    for path in worktree.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(worktree).as_posix()
        if rel.startswith(("data/private/", "data/fixtures/", "data/tmp/", ".secrets/")):
            forbidden.append(rel)
        if rel in {".env", ".env.local"}:
            forbidden.append(rel)
    if forbidden:
        joined = "\n".join(f"  {item}" for item in forbidden[:50])
        raise SystemExit(f"Refusing to publish forbidden files:\n{joined}")


def verify_live(url: str, expected_text: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    cache_key = str(int(time.time()))
    last_error = ""
    while time.time() < deadline:
        verify_url = f"{url}{'&' if '?' in url else '?'}v={cache_key}"
        request = urllib.request.Request(
            verify_url,
            headers={
                "Cache-Control": "no-cache",
                "User-Agent": "cts-publish-static-site/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
                last_modified = response.headers.get("Last-Modified", "unknown")
        except Exception as exc:  # noqa: BLE001 - report the latest network/deploy failure.
            last_error = str(exc)
        else:
            if expected_text in body:
                print(f"Verified live page: {url}")
                print(f"Last-Modified: {last_modified}")
                return
            last_error = f"expected text not found at {verify_url}"
        time.sleep(interval_seconds)
    raise SystemExit(f"Live verification failed after {timeout_seconds}s: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="GitHub Pages branch to publish")
    parser.add_argument("--remote", default="origin", help="git remote to push")
    parser.add_argument("--message", required=True, help="commit message for the Pages branch")
    parser.add_argument("--verify-url", default=DEFAULT_VERIFY_URL, help="live URL to verify after push")
    parser.add_argument("--expect-text", required=True, help="text that must appear in the live page")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="live verification timeout")
    parser.add_argument("--interval-seconds", type=int, default=10, help="live verification polling interval")
    parser.add_argument("--skip-build", action="store_true", help="skip scripts/build_static_site.py")
    parser.add_argument("--skip-verify", action="store_true", help="skip live URL verification")
    parser.add_argument("--dry-run", action="store_true", help="build and sync into a temp worktree without committing or pushing")
    args = parser.parse_args()

    ensure_clean_publish_paths(PUBLISH_PATHS)

    if not args.skip_build:
        print_output(run([sys.executable, "scripts/build_static_site.py"]))

    print_output(run(["git", "fetch", args.remote, args.branch]))

    with tempfile.TemporaryDirectory(prefix="cts-gh-pages-") as tmp:
        worktree = Path(tmp) / "site"
        print_output(run(["git", "worktree", "add", str(worktree), f"{args.remote}/{args.branch}"]))
        try:
            copy_publish_paths(worktree, PUBLISH_PATHS)
            reject_forbidden_files(worktree)
            status = run(["git", "status", "--short"], cwd=worktree)
            print_output(status)
            if not status.stdout.strip():
                print("No gh-pages changes to publish.")
                if not args.skip_verify and not args.dry_run:
                    verify_live(args.verify_url, args.expect_text, args.timeout_seconds, args.interval_seconds)
                return 0
            if args.dry_run:
                print("Dry run complete; gh-pages worktree has changes but was not committed.")
                return 0
            print_output(run(["git", "add", *PUBLISH_PATHS], cwd=worktree))
            print_output(run(["git", "commit", "-m", args.message], cwd=worktree))
            print_output(run(["git", "push", args.remote, f"HEAD:{args.branch}"], cwd=worktree))
        finally:
            print_output(run(["git", "worktree", "remove", "--force", str(worktree)], check=False))

    if not args.skip_verify:
        verify_live(args.verify_url, args.expect_text, args.timeout_seconds, args.interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
