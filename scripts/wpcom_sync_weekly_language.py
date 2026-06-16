#!/usr/bin/env python3
"""Sync current CTS weekly-structure language to selected WordPress pages."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import shlex
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / ".secrets" / "wordpress.env"
PAGE_IDS = [4895, 5302, 1759]

WEEKLY_STRUCTURE_LIST = """<ol type="A" class="wp-block-list">
<li><strong>Last week&#8217;s results summary and link:</strong> a brief summary and a link to the primary CTS website page containing the previous week&#8217;s results and reports.</li>
<li><strong>One CTS-administered topic:</strong> the Featured Topic banner appears immediately before a <strong>◉ Main topic...</strong> introduction line, followed by 12 related survey items from the CTS topic bank.</li>
<li><strong>Three participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week&#8217;s participant vote. These are intentionally independent from the weekly CTS-administered topic.</li>
<li><strong>A participant-nominated item ballot:</strong> 7 AI-polished ballot items selected from the previous week&#8217;s participant nominations, with AI-created seed items added only when fewer than 7 suitable participant nominations are available. Ballot items are selected for clarity, relevance, novelty, and likely participant tension.</li>
<li><strong>A text box:</strong> to suggest survey items to be voted on next week and possibly featured in the following week&#8217;s survey.</li>
<li><strong>A preview of upcoming topics:</strong> The topics for the next three weeks will be featured to allow for mental preparation.</li>
</ol>"""

BALLOT_RULE = """<p class="wp-block-paragraph"><strong>Participant-nominated ballot rule:</strong> Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, likely participant tension, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked eligible items become live participant-vote-determined survey items in the following week&#8217;s survey.</p>"""


def ssl_context() -> ssl.SSLContext:
    import certifi  # type: ignore

    return ssl.create_default_context(cafile=certifi.where())


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in TOKEN_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = shlex.split(value)[0] if value else ""
    return values


def api_url(env: dict[str, str], page_id: int, *, edit: bool = False) -> str:
    suffix = "?context=edit" if edit else ""
    return f"{env['WPCOM_API_BASE']}/rest/v1.1/sites/{env['WPCOM_SITE_ID']}/posts/{page_id}{suffix}"


def get_page(env: dict[str, str], page_id: int) -> dict:
    request = Request(
        api_url(env, page_id, edit=True),
        headers={"Authorization": f"Bearer {env['WPCOM_ACCESS_TOKEN']}", "Accept": "application/json"},
    )
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def update_page(env: dict[str, str], page_id: int, content: str) -> dict:
    body = urlencode({"content": content}).encode("utf-8")
    request = Request(
        api_url(env, page_id),
        data=body,
        headers={
            "Authorization": f"Bearer {env['WPCOM_ACCESS_TOKEN']}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def replace_structure_list(content: str) -> str:
    pattern = re.compile(r'<ol type="A" class="wp-block-list">.*?</ol>', flags=re.S)
    return pattern.sub(WEEKLY_STRUCTURE_LIST, content, count=1)


def ensure_ballot_rule(content: str) -> str:
    if "Participant-nominated ballot rule:" in content:
        content = re.sub(
            r'<p class="wp-block-paragraph"><strong>Participant-nominated ballot rule:</strong>.*?</p>',
            BALLOT_RULE,
            content,
            flags=re.S,
            count=1,
        )
        return content
    return content.replace(WEEKLY_STRUCTURE_LIST, WEEKLY_STRUCTURE_LIST + "\n" + BALLOT_RULE, 1)


def sync_content(content: str) -> str:
    content = replace_structure_list(content)
    content = ensure_ballot_rule(content)
    replacements = {
        "<li><strong>Participant-vote-determined questions:</strong> each survey adds 3 live survey items chosen based on the previous week&#8217;s participant vote.</li>":
            "<li><strong>Participant-vote-determined questions:</strong> each survey adds 3 independent live survey items chosen based on the previous week&#8217;s participant vote.</li>",
        "<li><strong>Ongoing item voting:</strong> every weekly survey includes a &#8216;purified&#8217; participant-nominated item ballot and a text box for next-week suggestions.</li>":
            "<li><strong>Ongoing item voting:</strong> every weekly survey includes a 7-item AI-polished participant-nominated item ballot and a text box for next-week suggestions.</li>",
        "the previous-results summary and link":
            "last week&#8217;s results summary and link",
        "<p class=\"wp-block-paragraph\">The cycle is cumulative: participant suggestions submitted in one weekly survey are refined, placed on the next ballot, and the top 3 selected items become live survey items in the following week&#8217;s survey.</p>":
            "<p class=\"wp-block-paragraph\">The cycle is cumulative: participant suggestions submitted in one weekly survey are reviewed by CTS with AI assistance, polished, reduced to a 7-item ballot, ranked by active participants, and the top 3 ranked eligible items become live survey items in the following week&#8217;s survey.</p>",
        "<li><strong>Participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week&#8217;s participant vote.</li>":
            "<li><strong>Participant-vote-determined questions:</strong> 3 additional independent live survey items chosen based on the previous week&#8217;s participant vote.</li>",
        "<li><strong>Participant-nominated item ballot:</strong> the ranked result from voting on last week&#8217;s &#8216;purified&#8217; participant-nominated survey items.</li>":
            "<li><strong>Participant-nominated item ballot:</strong> the ranked result from voting on last week&#8217;s 7 AI-polished participant-nominated ballot items.</li>",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def main() -> int:
    env = load_env()
    backup_dir = ROOT / ".secrets" / "wp-backups" / f"{datetime.now():%Y%m%d-%H%M%S}-orthogonal-tension-language"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for page_id in PAGE_IDS:
        page = get_page(env, page_id)
        slug = page.get("slug", str(page_id))
        (backup_dir / f"{page_id}-{slug}.json").write_text(json.dumps(page, indent=2), encoding="utf-8")
        original = str(page.get("content", ""))
        updated = sync_content(original)
        if updated == original:
            print(f"{page_id} {slug}: no changes")
            continue
        result = update_page(env, page_id, updated)
        print(f"{page_id} {slug}: updated -> {result.get('modified')}")
    print(f"backup: {backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
