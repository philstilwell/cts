#!/usr/bin/env python3
"""Build the static GitHub Pages version of the revived CTS pages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_NAME = "Christian Thought Survey"
SITE_DESCRIPTION = (
    "Weekly Christian research reports for ministers, with credence-slider surveys, "
    "participant-voted questions, and responsible data releases."
)
SITE_URL = "https://christianthoughtsurvey.com"
CSS_VERSION = "20260622-herding-cats-bg"
WP_SITE = "https://christianthoughtsurvey.wordpress.com"
UPDATED = "June 22, 2026"
SITEMAP_LASTMOD = "2026-06-22"
SURVEYOL_FORM_URL = "https://www.surveyol.com/r/C33E5B3"
SURVEYOL_EMBED_URL = "https://www.surveyol.com/s2/1BA7FF3"
WEEK_1_REPORT_OUTPUT = "weekly-survey-reports/week-001-divorce-and-remarriage/index.html"
WEEK_2_REPORT_OUTPUT = "weekly-survey-reports/week-002-pornography-and-the-church/index.html"
NEWSLETTER_CONFIRMATION_OUTPUT = "email-confirmation/index.html"
AUTOMATION_DAILY_LOG_OUTPUT = "automation-daily-log/index.html"
AUTOMATION_DAILY_LOG_DATA = ROOT / "data/public/automation-daily-log.json"
REPORT_MANAGED_OUTPUTS = {WEEK_1_REPORT_OUTPUT, WEEK_2_REPORT_OUTPUT}
OG_IMAGE = f"{SITE_URL}/assets/cts-research-overview.png"
OG_IMAGE_ALT = "Christian Thought Survey research overview graphic"
DEFAULT_ROBOTS = "index,follow,max-image-preview:large"
THEME_COLOR = "#174d51"
CLOUDFLARE_ANALYTICS = "<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"b86c3e7a273f47648ae70f08866f9ec5\"}'></script><!-- End Cloudflare Web Analytics -->"
MAILERLITE_UNIVERSAL_SCRIPT = """<!-- MailerLite Universal -->
<script>
    (function(w,d,e,u,f,l,n){w[f]=w[f]||function(){(w[f].q=w[f].q||[])
    .push(arguments);},l=d.createElement(e),l.async=1,l.src=u,
    n=d.getElementsByTagName(e)[0],n.parentNode.insertBefore(l,n);})
    (window,document,'script','https://assets.mailerlite.com/js/universal.js','ml');
    ml('account', '2397853');
</script>
<!-- End MailerLite Universal -->"""
MAILERLITE_NEWSLETTER_FORM_EMBED = '<div class="ml-embedded" data-form="EQ6WXD"></div>'
WEEKLY_STRUCTURE_LIST = """<ol class="process-list" type="A">
  <li><strong>Last week's results summary and link:</strong> a brief summary and a link to the primary CTS website page containing the previous week's results and reports.</li>
  <li><strong>One CTS-administered topic:</strong> the Featured Topic banner appears immediately before a <strong>◉ Main topic...</strong> introduction line, followed by 12 related survey items from the CTS topic bank.</li>
  <li><strong>Three participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week's participant vote. These are intentionally independent from the weekly CTS-administered topic.</li>
  <li><strong>A participant-nominated item ballot:</strong> 7 AI-polished ballot items selected from the previous week's participant nominations, with AI-created seed items added only when fewer than 7 suitable participant nominations are available. Ballot items are selected for clarity, relevance, novelty, and likely participant tension.</li>
  <li><strong>A text box:</strong> to suggest survey items to be voted on next week and possibly featured in the following week's survey.</li>
  <li><strong>A preview of upcoming topics:</strong> The topics for the next three weeks will be featured to allow for mental preparation.</li>
</ol>"""
RESPONSE_RULE_NOTE = "The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses."
PARTICIPANT_BALLOT_NOTE = "Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, likely participant tension, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked eligible items become live participant-vote-determined survey items in the following week's survey."


def load_automation_daily_log() -> dict[str, object]:
    if not AUTOMATION_DAILY_LOG_DATA.exists():
        return {"updated_at": "", "entries": []}
    return json.loads(AUTOMATION_DAILY_LOG_DATA.read_text(encoding="utf-8"))


def render_text_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return ""
    list_items = "\n".join(f"        <li>{escape(str(item))}</li>" for item in items)
    return f"<ul>\n{list_items}\n      </ul>"


def render_automation_daily_log_content() -> str:
    data = load_automation_daily_log()
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        recorded_date = escape(str(entry.get("date", "")))
        recorded_time = escape(str(entry.get("recorded_time_et") or entry.get("recorded_at", "")))
        rows.append(
            "\n".join(
                [
                    "      <tr>",
                    f"        <td><div class=\"recorded-status\"><time datetime=\"{escape(str(entry.get('recorded_at', '')))}\"><span class=\"recorded-date\">{recorded_date}</span><span class=\"recorded-time\">{recorded_time}</span></time>\n<span class=\"log-status\">{escape(str(entry.get('status', '')))}</span></div></td>",
                    f"        <td>{escape(str(entry.get('summary', '')))}{render_text_list(entry.get('ran'))}</td>",
                    f"        <td>{escape(str(entry.get('result', '')))}</td>",
                    f"        <td>{escape(str(entry.get('next', '')))}</td>",
                    "      </tr>",
                ]
            )
        )
    if not rows:
        rows.append(
            "\n".join(
                [
                    "      <tr>",
                    "        <td colspan=\"4\">No daily automation log entries have been published yet.</td>",
                    "      </tr>",
                ]
            )
        )
    updated_at = escape(str(data.get("updated_time_et") or data.get("updated_at", "")))
    return f"""
<div class="wp-content automation-log">
  <p class="callout"><strong>Private-data note:</strong> This page is intentionally unlinked, omitted from the sitemap, and marked `noindex,nofollow`. It shows only public-safe operational summaries, not participant data, respondent links, raw exports, or private status-board paths.</p>

  <div class="status-grid automation-log-summary">
    <div class="status-card">
      <span>Visibility</span>
      <strong>Orphaned</strong>
      <p>No public navigation or sitemap entry points to this page.</p>
    </div>
    <div class="status-card">
      <span>Robots</span>
      <strong>Noindex, nofollow</strong>
      <p>The page-level robots directive asks search engines not to index or follow it.</p>
    </div>
    <div class="status-card">
      <span>Updated</span>
      <strong>{updated_at}</strong>
      <p>The log is updated only with public-safe automation summaries.</p>
    </div>
  </div>

  <figure class="automation-log-table-wrap">
    <table class="automation-log-table">
      <thead>
        <tr>
          <th scope="col">Recorded / Status</th>
          <th scope="col">What ran</th>
          <th scope="col">Result</th>
          <th scope="col">Next</th>
        </tr>
      </thead>
      <tbody>
{chr(10).join(rows)}
      </tbody>
    </table>
  </figure>
</div>
"""


@dataclass(frozen=True)
class Page:
    key: str
    output: str
    nav_label: str
    title: str
    eyebrow: str
    description: str
    content: str
    in_nav: bool = True
    show_nav: bool = True
    robots: str = ""


PAGES = [
    Page(
        key="home",
        output="index.html",
        nav_label="Home",
        title="Christian Thought Survey 2026",
        eyebrow="Returning in 2026",
        description=(
            "Weekly Christian Thought Survey reports for ministers, with "
            "credence-slider research, participant-voted questions, and responsible "
            "data releases."
        ),
        content="""
<section class="content-band shade report-spotlight-band">
  <div class="container latest-report">
    <div class="latest-report-copy">
      <p class="section-label">Latest weekly report</p>
      <h2>Week 1: Divorce and Remarriage</h2>
      <p class="section-copy">For most visitors, weekly results should be the fastest path through the site. The Week 1 report page now holds preliminary aggregate results, refreshed on June 16, 2026, and will be revised after the final CTS export is reviewed.</p>
      <div class="report-meta-grid" aria-label="Latest report status">
        <div class="meta-chip">
          <span>Status</span>
          <strong>Preliminary results</strong>
        </div>
        <div class="meta-chip">
          <span>Publication rhythm</span>
          <strong>Tuesday reports</strong>
        </div>
        <div class="meta-chip">
          <span>Current responses</span>
          <strong>33 complete</strong>
        </div>
        <div class="meta-chip">
          <span>Topic</span>
          <strong>Divorce and Remarriage</strong>
        </div>
      </div>
      <div class="button-row">
        <a class="button" href="{week_1_report_url}">Open Latest Report</a>
        <a class="button light" href="{weekly_url}">View All Weekly Reports</a>
      </div>
    </div>
    <aside class="latest-report-aside" aria-label="What the latest report will include">
      <span class="report-status preliminary">Preliminary</span>
      <strong>Current snapshot posted</strong>
      <p>The report includes a summary, key tensions, item-level aggregate distributions, ballot results, and data-release notes.</p>
    </aside>
  </div>
</section>

<section class="content-band">
  <div class="container two-column">
    <div>
      <p class="section-label">What changes in 2026?</p>
      <h2>Shorter surveys, faster reports, cleaner data.</h2>
      <p class="section-copy">The revived project keeps the original CTS concern for precise wording and fine-grained measurement, but changes the rhythm to one focused topic, participant-vote-determined questions, and a continuing participant-generated item pipeline.</p>
    </div>
    <div class="wp-content">
      <ul>
        <li><strong>Focused weekly surveys:</strong> each survey begins with one CTS-administered topic and 12 related items.</li>
        <li><strong>Participant-vote-determined questions:</strong> each survey adds 3 live survey items chosen based on the previous week's participant vote.</li>
        <li><strong>Credence-based responses:</strong> all survey items use sliders so responses preserve more precision than ordinary agree/disagree choices.</li>
        <li><strong>Minister-focused panel:</strong> the first invitations will go to prior CTS participants who were willing to be contacted by email.</li>
        <li><strong>Open reporting:</strong> weekly summaries will be written for public reading, while data releases will be structured for responsible reanalysis.</li>
        <li><strong>Ongoing item voting:</strong> every weekly survey includes a 7-item AI-polished participant-nominated item ballot and a text box for next-week suggestions.</li>
        <li><strong>Looking ahead:</strong> every survey features the next three weeks' topics to allow for mental preparation.</li>
      </ul>
    </div>
  </div>
</section>

<section class="content-band shade">
  <div class="container two-column">
    <div>
      <p class="section-label">Weekly cycle</p>
      <h2>How the weekly cycle works</h2>
      <p class="section-copy">The CTS administration supplies the main topic, active participants help choose participant-generated questions, each survey collects suggestions for the next round, and every survey previews upcoming topics for mental preparation.</p>
    </div>
    <div class="wp-content">
      {weekly_structure_list}
      <p class="callout"><strong>Participant-nominated ballot rule:</strong> {participant_ballot_note}</p>
      <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>
    </div>
  </div>
</section>

<section class="content-band">
  <div class="container">
    <p class="section-label">Site sections</p>
    <h2>Follow the revived project.</h2>
    <div class="path-grid">
      <a class="path-card" href="{weekly_url}">
        <strong>Weekly Survey Reports</strong>
        <span>Survey structure, publication plan, and the first report index.</span>
      </a>
      <a class="path-card" href="{archive_url}">
        <strong>Previous Results Archive</strong>
        <span>Links to earlier full results, mini-surveys, items, and policy pages.</span>
      </a>
      <a class="path-card" href="{contact_url}">
        <strong>Contact &amp; Participation</strong>
        <span>Invitation notes for ministers, topic suggestions, and data questions.</span>
      </a>
      <a class="path-card" href="{participant_pool_url}">
        <strong>Participant Pool</strong>
        <span>How the ministry-focused panel was assembled, why it is useful, and where its limits remain.</span>
      </a>
      <a class="path-card" href="{herding_cats_url}">
        <strong>Herding Cats</strong>
        <span>A cheerful note on why theological survey wording makes everyone reach for a red pen.</span>
      </a>
      <a class="path-card" href="{newsletter_url}">
        <strong>Newsletter Signup</strong>
        <span>Result notices, topic previews, and occasional CTS articles for non-participant readers.</span>
      </a>
      <a class="path-card" href="{privacy_url}">
        <strong>Privacy &amp; Data Release</strong>
        <span>Participant protections, public reporting rules, and raw-data handling.</span>
      </a>
    </div>
  </div>
</section>
""",
    ),
    Page(
        key="weekly",
        output="weekly-survey-reports/index.html",
        nav_label="Reports",
        title="Weekly Survey Reports",
        eyebrow="Report index",
        description=(
            "Browse weekly Christian Thought Survey reports, upcoming topics, "
            "participant-generated questions, and public data-release notes."
        ),
        content="""
<div class="wp-content results-hub">
  <p>This page is the public hub for weekly Christian Thought Survey results. The newest survey page is featured first, followed by the current weekly survey status lanes and the participant-nominated item rotation.</p>

  <section class="latest-report-card" aria-labelledby="latest-report-heading">
    <div>
      <p class="section-label">Newest survey page</p>
      <h2 id="latest-report-heading">Week 2: Pornography and the Church</h2>
      <p>The Week 2 placeholder page is published before CTS invitations are sent. It names the topic, planned survey items, participant ballot, reporting schedule, and a short encapsulation linking to the June 16 refresh of the Week 1 report.</p>
      <div class="button-row">
        <a class="button" href="{week_2_report_url}">Open Week 2 Placeholder</a>
        <a class="button light" href="{week_1_report_url}">Open Week 1 Report</a>
      </div>
    </div>
    <dl class="report-meta-list">
      <div>
        <dt>Status</dt>
        <dd>Survey placeholder</dd>
      </div>
      <div>
        <dt>Survey topic</dt>
        <dd>Pornography and the Church</dd>
      </div>
    </dl>
  </section>

  <section class="survey-control-board" aria-labelledby="survey-control-heading">
    <div class="section-heading-row">
      <div>
        <p class="section-label">Survey status</p>
        <h2 id="survey-control-heading">Weekly survey status</h2>
      </div>
      <p>This board gives readers a public progress snapshot for each weekly survey: what is open now, what has already been reported, and when to expect the next public update. Participant identities and raw response files are not published.</p>
    </div>
    <div class="survey-timeline-chart" aria-label="Weekly survey status timeline">
      <div class="survey-lane current" style="--progress-width: 22.4%;">
        <div class="survey-lane-label">
          <a href="{week_2_report_url}">Week 2</a>
          <span>Pornography and the Church</span>
        </div>
        <div class="survey-stage-track" aria-label="Week 2 is currently fielding invitations.">
          <div class="survey-stage done" data-short-label="Page">
            <button class="stage-dot" type="button" aria-describedby="week2-placeholder-info" aria-label="Week 2 placeholder details"></button>
            <span class="stage-info-panel" id="week2-placeholder-info" role="tooltip"><strong>Week 2 placeholder</strong> Public page published before the CTS response link was distributed. Current public responses: not yet reported.</span>
            <span>Placeholder</span>
          </div>
          <div class="survey-stage active" data-short-label="Open">
            <button class="stage-dot" type="button" aria-describedby="week2-fielding-info" aria-label="Week 2 fielding details"></button>
            <span class="stage-info-panel" id="week2-fielding-info" role="tooltip"><strong>Fielding now</strong> CTS email invitations are being sent in daily batches. Current public responses: pending the first report.</span>
            <span>Fielding</span>
          </div>
          <div class="survey-stage pending" data-short-label="Report">
            <button class="stage-dot" type="button" aria-describedby="week2-first-report-info" aria-label="Week 2 first report details"></button>
            <span class="stage-info-panel" id="week2-first-report-info" role="tooltip"><strong>First report</strong> Scheduled for June 23, 2026. The first public report will include the current complete-response count and aggregate item results.</span>
            <span>First Report</span>
          </div>
          <div class="survey-stage pending" data-short-label="Refresh">
            <button class="stage-dot" type="button" aria-describedby="week2-refresh-info" aria-label="Week 2 refresh details"></button>
            <span class="stage-info-panel" id="week2-refresh-info" role="tooltip"><strong>Refreshes</strong> After the first report posts, this survey will refresh each Tuesday morning while the response window remains open.</span>
            <span>Refreshes</span>
          </div>
          <div class="survey-stage pending" data-short-label="Final">
            <button class="stage-dot" type="button" aria-describedby="week2-final-info" aria-label="Week 2 final report details"></button>
            <span class="stage-info-panel" id="week2-final-info" role="tooltip"><strong>Final report</strong> Final close: Tuesday, July 7, 2026, 21 days after the first production invitation send. Results will be marked final after the CTS export is reviewed.</span>
            <span>Final</span>
          </div>
        </div>
        <div class="survey-lane-next">
          <span>Next</span>
          <strong>First report June 23</strong>
        </div>
      </div>
      <div class="survey-lane" style="--progress-width: 59.2%;">
        <div class="survey-lane-label">
          <a href="{week_1_report_url}">Week 1</a>
          <span>Divorce and Remarriage</span>
        </div>
        <div class="survey-stage-track" aria-label="Week 1 has posted preliminary results and is in the refresh period.">
          <div class="survey-stage done" data-short-label="Page">
            <button class="stage-dot" type="button" aria-describedby="week1-placeholder-info" aria-label="Week 1 placeholder details"></button>
            <span class="stage-info-panel" id="week1-placeholder-info" role="tooltip"><strong>Week 1 placeholder</strong> The Divorce and Remarriage public page was created before invitations were sent, giving readers a stable report URL.</span>
            <span>Placeholder</span>
          </div>
          <div class="survey-stage done" data-short-label="Sent">
            <button class="stage-dot" type="button" aria-describedby="week1-fielding-info" aria-label="Week 1 fielding details"></button>
            <span class="stage-info-panel" id="week1-fielding-info" role="tooltip"><strong>Fielding</strong> 409 CTS email invitations were sent. The survey remains open during the three-week response window.</span>
            <span>Fielding</span>
          </div>
          <div class="survey-stage done" data-short-label="Report">
            <button class="stage-dot" type="button" aria-describedby="week1-first-report-info" aria-label="Week 1 first report details"></button>
            <span class="stage-info-panel" id="week1-first-report-info" role="tooltip"><strong>First report posted</strong> Public results currently show 33 complete responses as of the June 16 refresh.</span>
            <span>First Report</span>
          </div>
          <div class="survey-stage active" data-short-label="Refresh">
            <button class="stage-dot" type="button" aria-describedby="week1-refresh-info" aria-label="Week 1 refresh details"></button>
            <span class="stage-info-panel" id="week1-refresh-info" role="tooltip"><strong>Refreshing</strong> Current public responses: 33 complete. The report refreshes each Tuesday morning while the survey remains open, until final close on Wednesday, July 1, 2026.</span>
            <span>Refreshes</span>
          </div>
          <div class="survey-stage pending" data-short-label="Final">
            <button class="stage-dot" type="button" aria-describedby="week1-final-info" aria-label="Week 1 final report details"></button>
            <span class="stage-info-panel" id="week1-final-info" role="tooltip"><strong>Final report</strong> Final close target: Wednesday, July 1, 2026, 21 days after the first Week 1 production invitation window. Final reporting will preserve respondent privacy thresholds.</span>
            <span>Final</span>
          </div>
        </div>
        <div class="survey-lane-next">
          <span>Next</span>
          <strong>Tuesday refresh</strong>
        </div>
      </div>
    </div>
  </section>

  <section class="item-rotation-feature" aria-labelledby="item-rotation-heading">
    <p class="section-label">Participant-generated questions</p>
    <h2 id="item-rotation-heading">How nominated items rotate into the survey</h2>
    <p>Participant-nominated items move through a rolling three-week pipeline. Participants first submit suggested survey items, eligible nominations are then polished into a ballot for participant voting, and the top 3 voted items become live 0-100 credence-slider survey items in a later weekly survey.</p>
    <figure class="item-rotation-figure">
      <img src="../assets/participant-nominated-item-rotation.png" alt="Circular infographic showing the participant-nominated item rotation: nomination week, voting week, survey week, and then the cycle repeats." width="1600" height="893">
      <figcaption>New nominations enter the pipeline while earlier nominations move toward participant voting and live survey use. This keeps the participant-generated item stream moving without making every weekly survey about the same topic.</figcaption>
    </figure>
  </section>

  <details class="accordion-block">
    <summary>
      <span class="accordion-label">Survey structure</span>
      <span class="accordion-title" role="heading" aria-level="2">How the weekly cycle works</span>
      <span class="accordion-hint">Expand to view the six-part weekly survey cycle.</span>
    </summary>
    <div class="accordion-content">
      <p>Each Weekly Survey will include six parts:</p>
      {weekly_structure_list}
      <p class="callout"><strong>Participant-nominated ballot rule:</strong> {participant_ballot_note}</p>
      <p>The cycle is cumulative: participant suggestions submitted in one weekly survey are reviewed by CTS with AI assistance, polished, reduced to a 7-item ballot, ranked by active participants, and the top 3 ranked items become live survey items in the following week's survey. If fewer than 7 suitable participant nominations are available, CTS adds AI-created seed items to complete the ballot.</p>
      <p>The regular rhythm is Tuesday-centered. First preliminary reports and refreshes to still-open preliminary reports are prepared on Tuesday morning, and the next survey's placeholder report page is published before the next CTS survey launches Tuesday evening. Invitations are sent through the CTS email invitation system in daily batches of up to 100 until all eligible participants have been invited.</p>
      <p>Each weekly survey remains open for three weeks from the first invitation send. The exact final close date is posted on the weekly public page before invitations go out, adjusted if the first send date changes, and reused through report refreshes and finalization. Preliminary reports are refreshed each Tuesday morning until the response window closes, with optional earlier updates when responses materially change, then marked final after the final export is reviewed.</p>
      <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>
    </div>
  </details>

  <h2>What each report will include</h2>
  <ul>
    <li><strong>Issue:</strong> the weekly CTS-administered topic and the reason it was selected.</li>
    <li><strong>Administered items:</strong> the exact wording of the 12 CTS-provided survey items.</li>
    <li><strong>Participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week's participant vote.</li>
    <li><strong>Credence results:</strong> summary statistics for slider responses across all live survey items.</li>
    <li><strong>Subgroup comparisons:</strong> denominational, role, ministry-experience, or other comparisons when sample size permits.</li>
    <li><strong>Participant-nominated item ballot:</strong> the ranked result from voting on last week's 7 AI-polished participant-nominated ballot items.</li>
    <li><strong>Suggestion text box:</strong> a summary of suggested survey items when they can be shared responsibly.</li>
    <li><strong>Last week's results summary and link:</strong> the brief summary and primary CTS website link included in the survey.</li>
    <li><strong>Preview of upcoming topics:</strong> the topics for the next three weeks featured to allow for mental preparation.</li>
    <li><strong>Data release:</strong> a link to raw or prepared data when privacy and formatting checks are complete.</li>
  </ul>

  <p class="callout">Raw data will not include direct email identifiers in public files. Participant attributes may be grouped or suppressed when needed to avoid accidental identification. Free-text suggestions may be edited, grouped, or withheld before publication to protect privacy and keep item wording usable. See the <a href="{privacy_url}">Privacy &amp; Data Release</a> page for the current policy.</p>
</div>
""",
    ),
    Page(
        key="week-001-report",
        output=WEEK_1_REPORT_OUTPUT,
        nav_label="Week 1",
        title="Week 1 Report: Divorce and Remarriage",
        eyebrow="Preliminary results",
        description=(
            "Preliminary Week 1 Christian Thought Survey results on Divorce and "
            "Remarriage, including slider distributions, key tensions, ballot "
            "outcomes, and privacy-safe data notes."
        ),
        content="""
<div class="wp-content">
  <p>This is the stable public page for the first revived weekly Christian Thought Survey report. The current full report is managed as a report artifact and should not be overwritten by the generic site builder. As of the June 16, 2026 refresh, the preliminary report showed 33 complete responses from 409 invitations.</p>

  <div class="status-grid">
    <div class="status-card">
      <span>Topic</span>
      <strong>Divorce and Remarriage</strong>
      <p>12 CTS-administered credence-slider items will focus on this topic.</p>
    </div>
    <div class="status-card">
      <span>Live items</span>
      <strong>15 slider items</strong>
      <p>12 featured-topic items plus 3 independent items, all using 0-100 credence sliders.</p>
    </div>
    <div class="status-card">
      <span>Report status</span>
      <strong>Preliminary results</strong>
      <p>Public interpretation, charts, ballot results, and data notes are posted and refreshed each Tuesday morning while the survey remains open.</p>
    </div>
  </div>

  <h2>Planned report sections</h2>
  <div class="report-grid">
    <section class="report-card">
      <h3>Executive summary</h3>
      <p>A short public brief naming the most striking patterns, pastoral implications, and limits of the response pool.</p>
    </section>
    <section class="report-card">
      <h3>15-item overview</h3>
      <p>Mean, IQR Range, Doubt/Dogma, observed 10-bin distribution shape, and a concise interpretation for all live slider items.</p>
    </section>
    <section class="report-card">
      <h3>Key tensions</h3>
      <p>The items and themes with significant disagreement, spread, or subgroup contrast.</p>
    </section>
    <section class="report-card">
      <h3>Distribution visuals</h3>
      <p>Compact observed 10-bin sparklines for every credence item, using light neighbor smoothing, a shared fixed 0-100 scale, and a 100% guide line when sample size permits.</p>
    </section>
    <section class="report-card">
      <h3>Correlations and scatterplots</h3>
      <p>Exploratory correlation views only where the sample size, subgroup quality, and privacy thresholds justify them.</p>
    </section>
    <section class="report-card">
      <h3>Ballot results</h3>
      <p>The ranked participant-nominated item ballot and the top items selected for the following week's live survey.</p>
    </section>
  </div>

  <h2>Report sections</h2>
  <figure>
    <table>
      <thead>
        <tr>
          <th>Section</th>
          <th>What appears here</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Field dates and response count</td>
          <td>Survey window, completed responses, and any response-quality notes.</td>
          <td>Posted</td>
        </tr>
        <tr>
          <td>Featured-topic items</td>
          <td>12 Divorce and Remarriage item summaries with 0-100 credence distributions.</td>
          <td>Posted</td>
        </tr>
        <tr>
          <td>Independent items</td>
          <td>3 orthogonal live items chosen for relevance and meaningful participant spread.</td>
          <td>Posted</td>
        </tr>
        <tr>
          <td>Key tensions</td>
          <td>Items where disagreement is substantial enough to merit interpretation.</td>
          <td>Posted</td>
        </tr>
        <tr>
          <td>Participant ballot</td>
          <td>7 ranked participant-nominated or seed items, with winners for the next survey.</td>
          <td>Posted</td>
        </tr>
        <tr>
          <td>Data release</td>
          <td>Prepared data or a release note after privacy and formatting review.</td>
          <td>Posted</td>
        </tr>
      </tbody>
    </table>
  </figure>

  <h2>Preview of upcoming topics</h2>
  <ul>
    <li><strong>Week 2:</strong> Pornography and the Church.</li>
    <li><strong>Week 3:</strong> Pastoral Authority and Accountability.</li>
    <li><strong>Week 4:</strong> Women in Church Leadership.</li>
  </ul>

  <p class="callout"><strong>Data note:</strong> Public files will not include email addresses or direct identifiers. Free-text suggestions may be edited, grouped, or withheld before publication to protect participants and keep survey-item wording usable.</p>

  <div class="button-row">
    <a class="button light" href="{weekly_url}">Back to report index</a>
    <a class="button light" href="{privacy_url}">Privacy &amp; Data Release</a>
  </div>
</div>
""",
        in_nav=False,
    ),
    Page(
        key="week-002-report",
        output=WEEK_2_REPORT_OUTPUT,
        nav_label="Week 2",
        title="Week 2 Survey: Pornography and the Church",
        eyebrow="Survey placeholder",
        description=(
            "Placeholder page for Christian Thought Survey Week 2 on Pornography "
            "and the Church, including fielding dates, planned survey items, and "
            "reporting schedule."
        ),
        content="""
<div class="wp-content">
  <p>This is the stable public page for the second revived weekly Christian Thought Survey report. The current page is managed as a weekly report artifact and should not be overwritten by the generic site builder.</p>

  <div class="status-grid">
    <div class="status-card">
      <span>Status</span>
      <strong>Survey open</strong>
      <p>Participant invitations are sent through the CTS email invitation system.</p>
    </div>
    <div class="status-card">
      <span>Topic</span>
      <strong>Pornography and the Church</strong>
      <p>12 CTS-administered credence-slider items focus on this topic.</p>
    </div>
    <div class="status-card">
      <span>First report</span>
      <strong>June 23, 2026</strong>
      <p>The first preliminary report is planned for one week after launch.</p>
    </div>
  </div>

  <p class="callout"><strong>Data note:</strong> Public files will not include email addresses, direct identifiers, respondent-level rows, or raw free-text suggestions. Participant attributes may be grouped or suppressed when needed to avoid accidental identification.</p>

  <div class="button-row">
    <a class="button light" href="{weekly_url}">Back to report index</a>
    <a class="button light" href="{week_1_report_url}">Week 1 Preliminary Report</a>
    <a class="button light" href="{privacy_url}">Privacy &amp; Data Release</a>
  </div>
</div>
""",
        in_nav=False,
    ),
    Page(
        key="participant-pool",
        output="participant-pool/index.html",
        nav_label="Participant Pool",
        title="Why These Participants Are Worth Hearing",
        eyebrow="Participant pool",
        description=(
            "The Christian Thought Survey participant pool is not a random sample "
            "of all Christians. It is an intentionally assembled panel of people "
            "with clear ministry involvement, chosen for serious engagement and "
            "breadth across church traditions and regions."
        ),
        content="""
<div class="wp-content">
  <p>The original CTS participant pool was assembled roughly three years before the 2026 weekly project. Participants were selected because they appeared to have meaningful involvement in Christian ministry, and because the project aimed to hear from a range of denominational and regional contexts rather than from one narrow church network.</p>

  <p>The pool is also valuable because these participants did more than provide an email address. In the original project, they supplied background information such as ministry role, years in ministry, denominational setting, region, and other profile details, and they participated in an extensive survey of roughly 200 items across a large swath of doctrinal, practical, and sociological issues facing the church today.</p>

  <p>The revived weekly project begins by reaching out first to those earlier participants who were willing to be contacted by email. The participant-quality claims on this page apply most directly to the initial 406 invited participants from that earlier pool. As the panel grows, CTS will do its utmost to invite subsequent participants who meet the same general standard of ministry involvement, seriousness, and breadth.</p>

  <p>That means the early weekly results should be read as the views of an intentionally ministry-focused panel, not as an official denominational poll or a statistically random survey of American ministers.</p>

  <h2>What participant quality means here</h2>
  <div class="report-grid">
    <section class="report-card">
      <h3>Clear ministry involvement</h3>
      <p>The pool was built around people whose public roles or stated work indicated real participation in Christian ministry, pastoral leadership, teaching, or related church service.</p>
    </section>
    <section class="report-card">
      <h3>Serious survey engagement</h3>
      <p>The earlier long-form survey required patience and careful thought. Participants answered roughly 200 items across theological, practical, and sociological issues, giving CTS unusually rich context for interpreting later weekly responses.</p>
    </section>
    <section class="report-card">
      <h3>Denominational breadth</h3>
      <p>CTS intentionally sought a range of Christian traditions so that reports would not merely reflect one denomination, school, or ministry subculture.</p>
    </section>
    <section class="report-card">
      <h3>Regional breadth</h3>
      <p>The focus was primarily the United States, with attention to hearing from ministers in different regions rather than treating one local context as the whole picture.</p>
    </section>
  </div>

  <h2>How to read the results</h2>
  <p>Because the participant pool is ministry-focused and intentionally assembled, CTS results are especially useful for seeing how thoughtful ministers and ministry-adjacent Christian leaders reason about current issues. The results are less useful for estimating exactly what all Christians, all pastors, or all members of a denomination believe.</p>

  <p>The earlier profile data also makes future analysis more useful. When privacy thresholds allow, weekly responses can be compared with prior information such as years in ministry, denominational family, region, and earlier patterns of belief across the original 200-item survey.</p>

  <p class="callout"><strong>Important limitation:</strong> Participant quality does not remove sampling limits. Every weekly report should still state the current response count, distinguish preliminary from final results, and avoid subgroup claims unless the number of respondents is large enough to protect privacy and support a responsible comparison.</p>

  <h2>Why the panel can become more valuable</h2>
  <p>The weekly format gives CTS a chance to strengthen the panel over time. Existing participants can suggest clearer survey items, invite attention to issues the administrator may have missed, and help identify questions that matter to active ministry. Additional ministers can also be invited as the project matures, especially where a tradition, region, or ministry context is underrepresented, while preserving the same basic expectations for ministry participation and thoughtful engagement.</p>

  <p class="callout"><strong>Current ministers are welcome to request consideration.</strong> If you are currently serving in ministry and would like to participate in future CTS weekly surveys, please use the <a href="{contact_url}">Contact &amp; Weekly Survey Participation</a> page to introduce yourself. CTS is especially interested in thoughtful ministers who can help broaden the panel across traditions, regions, and ministry contexts.</p>

  <p>The goal is not to claim that CTS participants speak for the whole church. The goal is more modest and, hopefully, more useful: to provide a disciplined window into how a diverse set of ministry-involved Christians think through doctrine, practice, and contemporary church life.</p>

  <div class="button-row">
    <a class="button light" href="{weekly_url}">Current weekly reports</a>
    <a class="button light" href="{privacy_url}">Privacy &amp; Data Release</a>
    <a class="button light" href="{overview_url}">Legacy overview</a>
    <a class="button light" href="{contact_url}">Request participation</a>
  </div>
</div>
""",
        in_nav=False,
    ),
    Page(
        key="herding-cats",
        output="herding-cats/index.html",
        nav_label="Herding Cats",
        title="Herding Cats and other silly ventures",
        eyebrow="Survey humility",
        description=(
            "A lighthearted note on why theology surveys are hard to word well, "
            "easy to critique, and still worth doing carefully."
        ),
        content="""
<div class="wp-content">
  <section class="herding-note" aria-labelledby="herding-note-heading">
    <div>
      <h2 id="herding-note-heading">Survey wording is where the trouble starts.</h2>
      <p>Writing surveys for theological leaders is a little like herding cats, except the cats have read the footnotes, spotted three possible meanings of <em>authority</em>, and would like to know why the question did not distinguish between at least five denominational contexts.</p>
      <p>CTS tries to write items that are clear enough to answer, fair enough to trust, and short enough to finish before the participant's coffee gets cold. That is a worthy aim. It is also, on many days, a comedy of theological calibration.</p>
    </div>
    <p class="herding-aside"><span>The survey designer's dilemma</span><strong>Precise enough to be fair. Plain enough to answer. Brief enough to survive.</strong></p>
  </section>

  <h2>The neutral sentence problem</h2>
  <p>The same survey item can sound suspicious for opposite reasons. Conservative theologians may hear a progressive assumption tucked into the framing. Progressive theologians may hear a conservative assumption doing quiet work in the categories. Both reactions can be sincere, thoughtful, and inconveniently plausible.</p>

  <p>Pastor-theologians add another layer of useful difficulty. They notice when a phrase sounds tidy on a form but lands awkwardly in the life of a congregation. They ask whether the wording is too broad, too narrow, too abstract, too loaded, too soft, too sharp, or missing the pastoral qualifier that would keep the whole thing from wobbling.</p>

  <div class="herding-complaint-grid" aria-label="Common survey wording tensions">
    <section class="herding-complaint-card conservative">
      <span>From one angle</span>
      <h3>Too progressive</h3>
      <p>The wording seems to smuggle in cultural accommodation before the participant has even touched the slider.</p>
    </section>
    <section class="herding-complaint-card progressive">
      <span>From another</span>
      <h3>Too conservative</h3>
      <p>The same wording seems to carry inherited assumptions as if they were simply the neutral starting point.</p>
    </section>
    <section class="herding-complaint-card pastoral">
      <span>From the pulpit</span>
      <h3>Too tidy</h3>
      <p>The sentence may be technically clear and still miss the pastoral messiness people actually carry.</p>
    </section>
    <section class="herding-complaint-card practical">
      <span>From the respondent</span>
      <h3>Too long</h3>
      <p>Every helpful caveat makes the item fairer, right up until the question becomes a paragraph in formalwear.</p>
    </section>
  </div>

  <section class="herding-tradeoffs" aria-labelledby="herding-tradeoffs-heading">
    <div>
      <h2 id="herding-tradeoffs-heading">Why the project keeps going anyway</h2>
      <p>The goal is not to produce perfect sentences that float above every tradition untouched. Those sentences do not appear to exist, and if they do, they are probably too long for a 0-100 slider.</p>
      <p>The more modest goal is to ask disciplined, transparent, revisable questions that help reveal where thoughtful Christian leaders agree, where they differ, and where the wording itself needs another pass.</p>
    </div>
    <ul>
      <li><strong>Precision</strong> has to be balanced against readability.</li>
      <li><strong>Neutrality</strong> has to be balanced against recognizable theological language.</li>
      <li><strong>Pastoral nuance</strong> has to be balanced against respondent fatigue.</li>
      <li><strong>Breadth</strong> has to be balanced against the fact that every tradition names the terrain differently.</li>
    </ul>
  </section>

  <p class="callout herding-thanks"><strong>Thank you to CTS participants.</strong> Your patience makes the project possible. Thank you for answering imperfect questions carefully, suggesting better wording when something feels off, and accepting that some limitations are built into this kind of work. The survey will never keep everyone perfectly happy, but your understanding helps it become more honest, more useful, and less silly than it otherwise would be.</p>

  <p class="herding-close">CTS welcomes thoughtful correction, better phrasing, and participant-nominated survey items. The aim is not to make every question immune to complaint. The aim is to keep improving the questions while learning something worthwhile together.</p>

  <div class="button-row">
    <a class="button light" href="{weekly_url}">Current weekly reports</a>
    <a class="button light" href="{contact_url}">Suggest an item</a>
    <a class="button light" href="{privacy_url}">Privacy &amp; Data Release</a>
  </div>
</div>
""",
    ),
    Page(
        key="archive",
        output="previous-results-archive/index.html",
        nav_label="Archive",
        title="Previous Results Archive",
        eyebrow="Reference library",
        description=(
            "A gathered archive for the original CTS long-form surveys, item-level "
            "pages, mini-surveys, and public results reports."
        ),
        content="""
<div class="wp-content">
  <p>The original Christian Thought Survey project produced long-form surveys, item-level pages, mini-surveys, and extensive result reports. Those materials are gathered here as a reference archive for readers who want to revisit the earlier CTS work.</p>

  <p>The current 2026 weekly survey materials now live on the <a href="{weekly_url}">Weekly Survey Reports</a> page so the legacy archive can remain focused on the earlier project.</p>

  <h2>Major results pages</h2>
  <ul>
    <li><a href="https://christianthoughtsurvey.wordpress.com/cts-2024-results/">2024 Full Results</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/cts-2023-results/">2023 Full Results</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/2023a-stats/">2023 Limited Results</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/2022b-stats/">2022 Results</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/results-preliminary/">Combined Stats</a></li>
  </ul>

  <h2>Supplemental pages</h2>
  <ul>
    <li><a href="https://christianthoughtsurvey.wordpress.com/mini-surveys/">Mini-Surveys</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/christianity-donald-trump-mini-survey/">Christianity &amp; Donald Trump Mini-Survey</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/a-facebook-surprise/">A Facebook Surprise</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/all-2023a-items/">All 2023 Items</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/cts-q-a/">CTS Q&amp;A</a></li>
    <li><a href="https://christianthoughtsurvey.wordpress.com/citation-policy/">Citation Policy</a></li>
  </ul>

  <p>Individual 2022-2023 item pages remain published and can still be reached through their direct URLs and tags.</p>
</div>
""",
    ),
    Page(
        key="privacy",
        output="privacy-data-release/index.html",
        nav_label="Privacy",
        title="Privacy &amp; Data Release",
        eyebrow="Participant protection",
        description=(
            "How Christian Thought Survey handles participant contact information, "
            "survey responses, free-text suggestions, and public data releases."
        ),
        content="""
<div class="wp-content">
  <p>Christian Thought Survey collects responses from people who are currently or previously engaged in full-time ministry. The project is designed for public reporting, but participant contact information and identifying details should not be exposed in public files.</p>

  <h2>Contact information</h2>
  <ul>
    <li>Email addresses are used for survey invitations, reminders, follow-up questions, and opt-out handling.</li>
    <li>Email addresses, names, and direct contact details are not included in public results files.</li>
    <li>MailerLite keeps survey participants and newsletter/update subscribers in separate groups: <code>CTS Participants</code> for survey invitations and <code>CTS Newsletter</code> for report notices and general CTS updates.</li>
    <li>The newsletter signup form collects email address, name, ministry status, and a brief interest motivation note so CTS can understand newsletter readership without adding newsletter-only subscribers to the survey participant panel.</li>
    <li>Participants may unsubscribe from MailerLite emails or ask CTS to remove them from future invitations.</li>
  </ul>

  <h2>Survey responses</h2>
  <ul>
    <li>Live survey items use 0-100 credence sliders unless a future survey clearly says otherwise.</li>
    <li>Weekly reports may summarize aggregate results, distribution shapes, and subgroup comparisons when sample size permits.</li>
    <li>Subgroups may be combined, suppressed, or withheld when reporting them could make participants identifiable.</li>
  </ul>

  <h2>Participant-nominated items</h2>
  <ul>
    <li>Free-text suggestions are treated as administrative inputs, not as public survey responses.</li>
    <li>Suggestions may be corrected, combined, clarified, shortened, or withheld before appearing on a participant-nominated item ballot.</li>
    <li>CTS uses AI assistance to polish nominations for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, likely participant tension, and pastoral or theological relevance.</li>
    <li>Each weekly ballot should contain 7 items. If fewer than 7 suitable participant nominations are available, CTS may add AI-created seed items to complete the ballot.</li>
    <li>CTS will not intentionally publish a suggestion in a way that identifies the participant who submitted it.</li>
  </ul>

  <h2>Data releases</h2>
  <ul>
    <li>Public data releases will remove direct email identifiers before publication.</li>
    <li>Prepared datasets may group participant attributes such as role, tradition, or ministry experience to reduce identification risk.</li>
    <li>Raw exports should be reviewed before release for accidental identifiers in free-text fields or small subgroups.</li>
  </ul>

  <p class="callout">The practical rule is simple: report results openly, protect participants carefully, and do not publish raw contact information.</p>
</div>
""",
    ),
    Page(
        key="overview",
        output="overview/index.html",
        nav_label="Overview",
        title="Legacy Survey Overview",
        eyebrow="Original project",
        description=(
            "Background on the 2022-2024 long-form Christian Thought Survey project "
            "and links to the original results archive."
        ),
        content="""
<div class="wp-content">
  <p>This page describes the original long-form Christian Thought Survey project. The current front page now focuses on the 2026 weekly survey format, but the earlier project remains important background for interpreting the archive.</p>

  <p>The 2022-2024 CTS surveys asked Christian leaders and committed believers to respond to large sets of doctrinal, practical, and sociological items. The project emphasized 0-100 credence responses so participants could register fine-grained levels of agreement rather than choose only from coarse multiple-choice categories.</p>

  <h2>What the original surveys emphasized</h2>
  <ul>
    <li>Broad comparisons across denominations and traditions.</li>
    <li>Item-level reporting across roughly 200 survey statements.</li>
    <li>Correlations involving ministry experience, conservatism, age, and other participant attributes.</li>
    <li>Participant reports and public-facing summaries.</li>
  </ul>

  <p>The 2026 project keeps the same concern for precise wording and credence measurement, but the current weekly survey process is documented separately on the <a href="{weekly_url}">Weekly Survey Reports</a> page.</p>

  <div class="button-row">
    <a class="button light" href="{archive_url}">Browse the archive</a>
    <a class="button light" href="{weekly_url}">Current weekly reports</a>
  </div>
</div>
""",
    ),
    Page(
        key="newsletter",
        output="newsletter/index.html",
        nav_label="Newsletter",
        title="Newsletter Signup",
        eyebrow="Updates",
        description=(
            "Sign up for Christian Thought Survey report notices, topic previews, "
            "and occasional articles without joining the weekly survey participant panel."
        ),
        content="""
<div class="wp-content">
  <p>This signup is for readers who would like Christian Thought Survey result notices, topic previews, and occasional articles, but who are not asking to join the weekly survey participant panel.</p>

  <p>The weekly survey participant panel is kept separately and is intended for people who are currently or previously engaged in full-time ministry. If that describes you and you want to be considered for survey participation, use the <a href="{contact_url}">Contact &amp; Weekly Survey Participation</a> page instead.</p>

  <p>The newsletter form asks for your email address, name, ministry status, and a brief note about why you are interested. For ministry status, a short note such as current full-time ministry, previous full-time ministry, volunteer or lay ministry, or not in ministry is enough. Those details help CTS understand who is following the project without moving newsletter-only subscribers into the survey participant group.</p>

  <div class="mailerlite-embed">
    {mailerlite_newsletter_form_embed}
  </div>

  <p class="form-note">Newsletter subscribers are kept in the separate <code>CTS Newsletter</code> MailerLite group. See <a href="{privacy_url}">Privacy &amp; Data Release</a> for the current data handling policy.</p>
</div>
""",
    ),
    Page(
        key="email-confirmation",
        output=NEWSLETTER_CONFIRMATION_OUTPUT,
        nav_label="Confirmation",
        title="Email Subscription Confirmed",
        eyebrow="Email subscription",
        description="Confirmation page for Christian Thought Survey email subscribers.",
        content="""
<div class="wp-content">
  <p>Thank you for confirming your subscription to Christian Thought Survey updates.</p>
  <p>CTS keeps general updates separate from weekly survey participation. Newsletter/update subscribers receive report notices, topic previews, and general CTS announcements. Weekly survey links are sent through the separate CTS Participants audience.</p>
  <p>CTS weekly surveys are intended for people who are currently or previously engaged in full-time ministry. Participation is optional, and every email should include an unsubscribe option.</p>
  <div class="button-row">
    <a class="button light" href="{home_url}">Return to the CTS home page</a>
    <a class="button light" href="{weekly_url}">View report index</a>
  </div>
</div>
""",
        in_nav=False,
        show_nav=False,
        robots="noindex",
    ),
    Page(
        key="automation-log",
        output=AUTOMATION_DAILY_LOG_OUTPUT,
        nav_label="Automation Log",
        title="Daily Automation Log",
        eyebrow="Operational log",
        description=(
            "A simple public-safe daily log of Christian Thought Survey automation "
            "status activity."
        ),
        content=render_automation_daily_log_content(),
        in_nav=False,
        show_nav=False,
        robots="noindex,nofollow,noarchive",
    ),
    Page(
        key="contact",
        output="contact/index.html",
        nav_label="Contact",
        title="Contact &amp; Weekly Survey Participation",
        eyebrow="Participation",
        description=(
            "Participation details for Christian ministers who want CTS weekly survey "
            "invitations, future item suggestions, or data and citation follow-up."
        ),
        content="""
<div class="wp-content">
  <p>The 2026 project will begin with prior CTS participants who indicated that email follow-up is welcome. If you are currently or previously engaged in full-time ministry and would like to be considered for later invitations, participant voting, future survey-item suggestions, or data/citation questions, use the form below.</p>

  <p>This form is the first eligibility and interest request. Potential participants who appear to fit the ministry-participant focus may later receive a separate private profile survey so CTS can collect the same broad participant-background fields used for the 2023 survey pool.</p>

  <p>If you are not asking to join the weekly survey participant panel but would like result notices, topic previews, and occasional CTS articles, use the <a href="{newsletter_url}">Newsletter Signup</a> instead.</p>

  <h2>How the weekly cycle works</h2>
  <p>Each Weekly Survey will include six parts:</p>
  {weekly_structure_list}
  <p class="callout"><strong>Participant-nominated ballot rule:</strong> {participant_ballot_note}</p>
  <p>The regular rhythm is Tuesday-centered: first preliminary reports and refreshes to still-open preliminary reports are prepared Tuesday morning, and the next survey's placeholder report page is published before the next CTS survey launches Tuesday evening. Invitations are sent in daily batches of up to 100 until all eligible participants have been invited.</p>
  <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>

  <p class="callout"><strong>Participation note:</strong> CTS weekly survey participation is intended for people who are currently or previously engaged in full-time ministry.</p>

  <div class="surveyol-embed">
    <iframe title="CTS 2026 Participation Request" src="{surveyol_embed_url}" loading="lazy"></iframe>
  </div>

  <p class="form-note">If the embedded form does not load, <a href="{surveyol_form_url}">open the CTS participation form in a new tab</a>. The same full-time ministry participation note applies.</p>
  <p class="form-note">Contact information is used for CTS participation and follow-up only. See <a href="{privacy_url}">Privacy &amp; Data Release</a> for the current data handling policy.</p>
</div>
""",
    ),
]


NAV = [(page.key, page.output, page.nav_label) for page in PAGES if page.in_nav]


def rel_prefix(output: str) -> str:
    parent = Path(output).parent
    if str(parent) == ".":
        return ""
    return "../" * len(parent.parts)


def page_url(prefix: str, output: str) -> str:
    if output == "index.html":
        return f"{prefix}index.html"
    return f"{prefix}{Path(output).parent.as_posix()}/"


def canonical_url(output: str) -> str:
    if output == "index.html":
        return f"{SITE_URL}/"
    if Path(output).parent.as_posix() == ".":
        return f"{SITE_URL}/{output}"
    return f"{SITE_URL}/{Path(output).parent.as_posix()}/"


def document_title(page: Page) -> str:
    title = strip_entities(page.title)
    if page.key == "home":
        return title
    return f"{title} | {SITE_NAME}"


def robots_content(page: Page) -> str:
    return page.robots or DEFAULT_ROBOTS


def is_indexable(page: Page) -> bool:
    return "noindex" not in robots_content(page)


def schema_page_type(page: Page) -> str:
    if page.key in {"weekly", "archive"}:
        return "CollectionPage"
    if page.key == "contact":
        return "ContactPage"
    if page.key in {"overview", "participant-pool", "herding-cats"}:
        return "AboutPage"
    return "WebPage"


def breadcrumb_items(page: Page) -> list[dict[str, object]]:
    items: list[dict[str, object]] = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": canonical_url("index.html"),
        }
    ]
    if page.output == "index.html":
        return items
    if page.output.startswith("weekly-survey-reports/") and page.output != "weekly-survey-reports/index.html":
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Weekly Survey Reports",
                "item": canonical_url("weekly-survey-reports/index.html"),
            }
        )
        position = 3
    else:
        position = 2
    items.append(
        {
            "@type": "ListItem",
            "position": position,
            "name": strip_entities(page.title),
            "item": canonical_url(page.output),
        }
    )
    return items


def json_for_script(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")


def render_structured_data(page: Page) -> str:
    if not is_indexable(page):
        return ""
    canonical = canonical_url(page.output)
    page_id = f"{canonical}#webpage"
    breadcrumb_id = f"{canonical}#breadcrumb"
    web_page: dict[str, object] = {
        "@type": schema_page_type(page),
        "@id": page_id,
        "url": canonical,
        "name": strip_entities(page.title),
        "description": page.description,
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "image": OG_IMAGE,
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": OG_IMAGE,
            "width": 1600,
            "height": 900,
            "caption": OG_IMAGE_ALT,
        },
        "dateModified": SITEMAP_LASTMOD,
    }
    if page.output != "index.html":
        web_page["breadcrumb"] = {"@id": breadcrumb_id}
    graph: list[dict[str, object]] = [
        {
            "@type": "Organization",
            "@id": f"{SITE_URL}/#organization",
            "name": SITE_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/assets/cts-logo.png",
            },
            "sameAs": [WP_SITE],
        },
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "url": SITE_URL,
            "name": SITE_NAME,
            "description": SITE_DESCRIPTION,
            "publisher": {"@id": f"{SITE_URL}/#organization"},
            "inLanguage": "en-US",
        },
        web_page,
    ]
    if page.output != "index.html":
        graph.append(
            {
                "@type": "BreadcrumbList",
                "@id": breadcrumb_id,
                "itemListElement": breadcrumb_items(page),
            }
        )
    return f'\n  <script type="application/ld+json">{json_for_script({"@context": "https://schema.org", "@graph": graph})}</script>'


def sitemap_priority(page: Page) -> str:
    priorities = {
        "home": "1.0",
        "weekly": "0.9",
        "week-001-report": "0.8",
        "week-002-report": "0.8",
        "newsletter": "0.7",
        "contact": "0.7",
        "participant-pool": "0.6",
        "herding-cats": "0.6",
        "archive": "0.6",
        "overview": "0.5",
        "privacy": "0.4",
    }
    return priorities.get(page.key, "0.5")


def sitemap_changefreq(page: Page) -> str:
    frequencies = {
        "home": "weekly",
        "weekly": "weekly",
        "week-001-report": "weekly",
        "week-002-report": "weekly",
        "newsletter": "monthly",
        "contact": "monthly",
        "participant-pool": "monthly",
        "herding-cats": "monthly",
        "archive": "yearly",
        "overview": "yearly",
        "privacy": "yearly",
    }
    return frequencies.get(page.key, "monthly")


def fill_links(html: str, prefix: str) -> str:
    links = {
        "home_url": page_url(prefix, "index.html"),
        "weekly_url": page_url(prefix, "weekly-survey-reports/index.html"),
        "week_1_report_url": page_url(prefix, WEEK_1_REPORT_OUTPUT),
        "week_2_report_url": page_url(prefix, WEEK_2_REPORT_OUTPUT),
        "participant_pool_url": page_url(prefix, "participant-pool/index.html"),
        "herding_cats_url": page_url(prefix, "herding-cats/index.html"),
        "newsletter_confirmation_url": page_url(prefix, NEWSLETTER_CONFIRMATION_OUTPUT),
        "archive_url": page_url(prefix, "previous-results-archive/index.html"),
        "privacy_url": page_url(prefix, "privacy-data-release/index.html"),
        "overview_url": page_url(prefix, "overview/index.html"),
        "newsletter_url": page_url(prefix, "newsletter/index.html"),
        "contact_url": page_url(prefix, "contact/index.html"),
        "surveyol_form_url": SURVEYOL_FORM_URL,
        "surveyol_embed_url": SURVEYOL_EMBED_URL,
        "mailerlite_newsletter_form_embed": MAILERLITE_NEWSLETTER_FORM_EMBED,
        "weekly_structure_list": WEEKLY_STRUCTURE_LIST,
        "response_rule_note": RESPONSE_RULE_NOTE,
        "participant_ballot_note": PARTICIPANT_BALLOT_NOTE,
    }
    return html.format(**links)


def render_nav(active_key: str, prefix: str) -> str:
    items = []
    for key, output, label in NAV:
        current = ' aria-current="page"' if key == active_key else ""
        items.append(f'<a href="{page_url(prefix, output)}"{current}>{escape(label)}</a>')
    return "\n        ".join(items)


def render_head(page: Page, prefix: str) -> str:
    title = escape(document_title(page))
    description = escape(page.description)
    canonical = canonical_url(page.output)
    robots = escape(robots_content(page))
    structured_data = render_structured_data(page)
    extra_head = f"\n  {MAILERLITE_UNIVERSAL_SCRIPT}" if page.key == "newsletter" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="{SITE_NAME}">
  <meta name="theme-color" content="{THEME_COLOR}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:site_name" content="Christian Thought Survey">
  <meta property="og:locale" content="en_US">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1600">
  <meta property="og:image:height" content="900">
  <meta property="og:image:alt" content="{OG_IMAGE_ALT}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <meta name="twitter:image:alt" content="{OG_IMAGE_ALT}">
  <link rel="icon" href="{prefix}assets/cts-logo.png">
  <link rel="stylesheet" href="{prefix}assets/styles.css?v={CSS_VERSION}">
  {CLOUDFLARE_ANALYTICS}{structured_data}{extra_head}
</head>"""


def render_header(page: Page, prefix: str) -> str:
    nav_links = (
        f"""      <div class="nav-links">
        {render_nav(page.key, prefix)}
      </div>"""
        if page.show_nav
        else ""
    )
    return f"""<body class="page-{page.key}">
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header">
    <nav class="nav" aria-label="Primary">
      <a class="brand" href="{page_url(prefix, "index.html")}">
        <img src="{prefix}assets/cts-logo.png" alt="CTS logo" width="42" height="42">
        <span>Christian Thought Survey</span>
      </a>
{nav_links}
    </nav>
  </header>"""


def render_home(page: Page, prefix: str) -> str:
    content = fill_links(page.content, prefix)
    return f"""  <main id="content">
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-inner">
        <div class="hero-copy">
          <p class="eyebrow">{escape(page.eyebrow)}</p>
          <h1 id="page-title">{page.title}</h1>
          <p class="lede"><strong>Christian Thought Survey is being revived as a weekly research project for Christian ministers.</strong> Each Weekly Survey will begin with last week's results summary and link, then a Featured Topic banner and <strong>◉ Main topic...</strong> introduction before 12 CTS-administered items, 3 participant-vote-determined questions, a 7-item AI-polished participant-nominated item ballot, a suggestion text box, and a preview of upcoming topics.</p>
          <div class="button-row">
            <a class="button" href="{page_url(prefix, WEEK_1_REPORT_OUTPUT)}">Latest Weekly Report</a>
            <a class="button secondary" href="{page_url(prefix, "weekly-survey-reports/index.html")}">All Weekly Reports</a>
          </div>
        </div>
      </div>
    </section>
{content}
  </main>"""


def render_standard(page: Page, prefix: str) -> str:
    content = fill_links(page.content, prefix)
    return f"""  <main id="content">
    <section class="page-heading" aria-labelledby="page-title">
      <div class="container">
        <p class="eyebrow">{escape(page.eyebrow)}</p>
        <h1 id="page-title">{page.title}</h1>
        <p class="lede">{escape(page.description)}</p>
      </div>
    </section>
    <section class="content-band">
      <article class="article-shell">
{content}
      </article>
    </section>
  </main>"""


def render_footer(prefix: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="footer-inner">
      <p>Christian Thought Survey. Site updated {UPDATED}.</p>
      <p><a href="{WP_SITE}/">WordPress archive</a></p>
    </div>
  </footer>
</body>
</html>
"""


def strip_entities(value: str) -> str:
    return value.replace("&amp;", "&")


def render_page(page: Page) -> str:
    prefix = rel_prefix(page.output)
    body = render_home(page, prefix) if page.key == "home" else render_standard(page, prefix)
    return "\n".join(
        [
            render_head(page, prefix),
            render_header(page, prefix),
            body,
            render_footer(prefix),
        ]
    )


def write_page(page: Page) -> None:
    path = ROOT / page.output
    if page.output in REPORT_MANAGED_OUTPUTS and path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_page(page), encoding="utf-8")


def write_404() -> None:
    page = Page(
        key="404",
        output="404.html",
        nav_label="Not Found",
        title="Page Not Found",
        eyebrow="404",
        description="The requested Christian Thought Survey page could not be found.",
        content="""
<div class="wp-content">
  <p>The page you were looking for is not part of the current Christian Thought Survey site.</p>
  <div class="button-row">
    <a class="button light" href="{home_url}">Return home</a>
    <a class="button light" href="{archive_url}">Browse the archive</a>
  </div>
</div>
""",
        robots="noindex",
    )
    path = ROOT / page.output
    path.write_text(render_page(page), encoding="utf-8")


def write_sitemap() -> None:
    urls = []
    for page in PAGES:
        if not is_indexable(page):
            continue
        urls.append(
            "\n".join(
                [
                    "  <url>",
                    f"    <loc>{escape(canonical_url(page.output))}</loc>",
                    f"    <lastmod>{SITEMAP_LASTMOD}</lastmod>",
                    f"    <changefreq>{sitemap_changefreq(page)}</changefreq>",
                    f"    <priority>{sitemap_priority(page)}</priority>",
                    "  </url>",
                ]
            )
        )
    sitemap = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *urls,
            "</urlset>",
            "",
        ]
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def write_robots() -> None:
    robots = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {SITE_URL}/sitemap.xml",
            "",
        ]
    )
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def main() -> int:
    for page in PAGES:
        write_page(page)
    write_404()
    write_sitemap()
    write_robots()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
