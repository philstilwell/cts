#!/usr/bin/env python3
"""Build a local index of legacy CTS item pages from WordPress."""

from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import re
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SITE = "christianthoughtsurvey.wordpress.com"
API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}"


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def ascii_clean(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u03c0\u03af\u03c3\u03c4\u03b9\u03c2": "pistis",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return ascii_clean(unescape(value))


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "CTS legacy item indexer"})
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_statement(content: str) -> str:
    matches = re.findall(r"<p\b[^>]*has-medium-font-size[^>]*>(.*?)</p>", content, flags=re.I | re.S)
    if matches:
        return strip_tags(matches[0])
    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", content, flags=re.I | re.S)
    for paragraph in paragraphs:
        text = strip_tags(paragraph)
        if len(text) > 20 and not text.startswith("Word Limit"):
            return text
    return ""


def extract_suggestions(content: str) -> list[str]:
    marker = re.search(r"Suggested Topics/Questions:", content, flags=re.I)
    if not marker:
        return []
    tail = content[marker.end() :]
    tail = tail.split("<hr", 1)[0]
    items = re.findall(r"<li\b[^>]*>(.*?)</li>", tail, flags=re.I | re.S)
    return [strip_tags(item) for item in items if strip_tags(item)]


def item_record(number: int, delay: float) -> dict:
    if delay:
        time.sleep(delay)
    slug = f"item-{number}"
    url = f"{API_BASE}/posts/slug:{slug}?type=page"
    data = fetch_json(url)
    content = str(data.get("content", ""))
    tags = sorted((data.get("terms", {}).get("post_tag", {}) or {}).keys())
    return {
        "number": number,
        "title": data.get("title", f"Item {number}"),
        "url": data.get("URL", f"https://{SITE}/{slug}/"),
        "statement": extract_statement(content),
        "tags": tags,
        "suggested_questions": extract_suggestions(content),
        "modified": data.get("modified"),
    }


def write_markdown(records: list[dict], path: Path) -> None:
    lines: list[str] = [
        "# Legacy 200-Item CTS Index",
        "",
        "Generated from the public WordPress item pages for the original CTS item set.",
        "",
        "Use this as a reference pool for themes or seed ideas. Do not copy items mechanically into the weekly survey cycle; rewrite candidates for current clarity, orthogonality to the weekly topic, and likely participant tension.",
        "",
        f"Source pattern: https://{SITE}/item-N/",
        "",
        "## Items",
        "",
    ]
    for record in records:
        tags = ", ".join(record["tags"]) if record["tags"] else "none"
        lines.append(f"### Item {record['number']}")
        lines.append("")
        lines.append(record["statement"] or "[statement not extracted]")
        lines.append("")
        lines.append(f"- Source: {record['url']}")
        lines.append(f"- Tags: {tags}")
        if record["suggested_questions"]:
            lines.append("- Suggested follow-up questions:")
            for question in record["suggested_questions"]:
                lines.append(f"  - {question}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--json-output", default="data/public/legacy-200-items.json")
    parser.add_argument("--markdown-output", default="LEGACY_200_ITEM_INDEX.md")
    args = parser.parse_args()

    records = [item_record(number, args.delay) for number in range(1, args.count + 1)]
    missing = [record["number"] for record in records if not record["statement"]]
    if missing:
        raise SystemExit(f"Could not extract statements for items: {missing}")

    json_path = ROOT / args.json_output
    md_path = ROOT / args.markdown_output
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(records, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    write_markdown(records, md_path)
    print(f"wrote {len(records)} items to {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
