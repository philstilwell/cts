#!/usr/bin/env python3
"""Build the static GitHub Pages version of the revived CTS pages."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WP_SITE = "https://christianthoughtsurvey.wordpress.com"
UPDATED = "June 1, 2026"
SURVEYOL_FORM_URL = "https://www.surveyol.com/r/C33E5B3"
SURVEYOL_EMBED_URL = "https://www.surveyol.com/s2/1BA7FF3"


@dataclass(frozen=True)
class Page:
    key: str
    output: str
    nav_label: str
    title: str
    eyebrow: str
    description: str
    content: str


PAGES = [
    Page(
        key="home",
        output="index.html",
        nav_label="Home",
        title="Christian Thought Survey 2026",
        eyebrow="Returning in 2026",
        description=(
            "A weekly research project for Christian ministers, built around carefully "
            "worded survey items, 0-100 credence sliders, and public reports."
        ),
        content="""
<section class="content-band">
  <div class="container two-column">
    <div>
      <p class="section-label">What changes in 2026?</p>
      <h2>Shorter surveys, faster reports, cleaner data.</h2>
      <p class="section-copy">The revived project keeps the original CTS concern for precise wording and fine-grained measurement, but changes the rhythm to one focused issue at a time.</p>
    </div>
    <div class="wp-content">
      <ul>
        <li><strong>Shorter weekly surveys:</strong> each issue receives a focused set of no more than ten items.</li>
        <li><strong>Credence-based responses:</strong> slider responses preserve more precision than ordinary agree/disagree choices.</li>
        <li><strong>Minister-focused panel:</strong> the first invitations will go to prior CTS participants who were willing to be contacted by email.</li>
        <li><strong>Open reporting:</strong> weekly summaries will be written for public reading, while data releases will be structured for responsible reanalysis.</li>
        <li><strong>Participant-directed topics:</strong> respondents will help choose the next issue, with submitted wording refined before publication.</li>
      </ul>
    </div>
  </div>
</section>

<section class="content-band shade">
  <div class="container two-column">
    <div>
      <p class="section-label">Current status</p>
      <h2>The 2026 weekly cycle is being prepared.</h2>
    </div>
    <div class="wp-content">
      <p>Reports are planned for Fridays so pastors and other ministry leaders can reflect on the results before Sunday. Public summaries will be posted here, and the project is being designed so appropriately prepared raw data can be shared for independent analysis.</p>
      <p>When the first weekly survey is fielded, this site will point to the current survey, the current report, the topic-vote result, and the raw-data download policy.</p>
      <p>The original 2022-2024 CTS materials remain available in the archive. They are being kept as a reference library while the front of the site shifts toward weekly reports.</p>
      <div class="button-row">
        <a class="button light" href="{weekly_url}">Weekly Survey Reports</a>
        <a class="button light" href="{archive_url}">Previous Results Archive</a>
      </div>
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
        <span>Report format, publication plan, and the first report index.</span>
      </a>
      <a class="path-card" href="{archive_url}">
        <strong>Previous Results Archive</strong>
        <span>Links to earlier full results, mini-surveys, items, and policy pages.</span>
      </a>
      <a class="path-card" href="{contact_url}">
        <strong>Contact &amp; Participation</strong>
        <span>Invitation notes for ministers, topic suggestions, and data questions.</span>
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
            "The collection point for weekly Christian Thought Survey reports once the "
            "2026 cycle begins."
        ),
        content="""
<div class="wp-content">
  <p>This page will collect the weekly Christian Thought Survey reports once the 2026 cycle begins. Each report will focus on one doctrinal, practical, or sociological issue of interest to Christian ministers.</p>

  <h2>Report format</h2>
  <ul>
    <li><strong>Issue:</strong> the weekly topic and the reason it was selected.</li>
    <li><strong>Items:</strong> the exact wording of all survey statements or questions.</li>
    <li><strong>Credence results:</strong> summary statistics for 0-100 slider responses.</li>
    <li><strong>Subgroup comparisons:</strong> denominational, role, ministry-experience, or other comparisons when sample size permits.</li>
    <li><strong>Next-topic vote:</strong> the ranked result from the weekly topic ballot.</li>
    <li><strong>Data release:</strong> a link to raw or prepared data when privacy and formatting checks are complete.</li>
  </ul>

  <h2>Report index</h2>
  <figure>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Topic</th>
          <th>Status</th>
          <th>Report</th>
          <th>Data</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Upcoming</td>
          <td>First weekly topic</td>
          <td>In preparation</td>
          <td>Pending</td>
          <td>Pending</td>
        </tr>
      </tbody>
    </table>
  </figure>

  <p class="callout">Raw data will not include direct email identifiers in public files. Participant attributes may be grouped or suppressed when needed to avoid accidental identification.</p>
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
  <p>The original Christian Thought Survey project produced long-form surveys, item-level pages, mini-surveys, and extensive result reports. Those materials are now gathered here as an archive while the front of the site shifts toward weekly 2026 reports.</p>

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
        key="overview",
        output="overview/index.html",
        nav_label="Overview",
        title="Legacy Survey Overview",
        eyebrow="Original project",
        description=(
            "Background on the 2022-2024 long-form Christian Thought Survey project "
            "and how it informs the revived weekly format."
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

  <p>The weekly 2026 project keeps the same concern for precise wording and credence measurement, but it changes the rhythm: shorter weekly surveys, faster reports, and more deliberate public release of reusable data.</p>

  <div class="button-row">
    <a class="button light" href="{archive_url}">Browse the archive</a>
  </div>
</div>
""",
    ),
    Page(
        key="contact",
        output="contact/index.html",
        nav_label="Contact",
        title="Contact &amp; Weekly Survey Participation",
        eyebrow="Participation",
        description=(
            "Contact and participation notes for ministers, ministry leaders, topic "
            "suggestions, and data or citation questions."
        ),
        content="""
<div class="wp-content">
  <p>The 2026 project will begin with prior CTS participants who indicated that email follow-up is welcome. If you are a Christian minister or ministry leader and would like to be considered for later invitations, topic suggestions, or data/citation questions, use the form below.</p>

  <p>Weekly surveys are intended to be short: usually no more than ten items on one issue, plus a vote on the following week's topic.</p>

  <div class="surveyol-embed">
    <iframe title="CTS 2026 Participation Request" src="{surveyol_embed_url}" loading="lazy"></iframe>
  </div>

  <p class="form-note">If the embedded form does not load, <a href="{surveyol_form_url}">open the SurveyOL form in a new tab</a>.</p>
</div>
""",
    ),
]


NAV = [(page.key, page.output, page.nav_label) for page in PAGES]


def rel_prefix(output: str) -> str:
    parent = Path(output).parent
    if str(parent) == ".":
        return ""
    return "../" * len(parent.parts)


def page_url(prefix: str, output: str) -> str:
    if output == "index.html":
        return f"{prefix}index.html"
    return f"{prefix}{Path(output).parent.as_posix()}/"


def fill_links(html: str, prefix: str) -> str:
    links = {
        "home_url": page_url(prefix, "index.html"),
        "weekly_url": page_url(prefix, "weekly-survey-reports/index.html"),
        "archive_url": page_url(prefix, "previous-results-archive/index.html"),
        "overview_url": page_url(prefix, "overview/index.html"),
        "contact_url": page_url(prefix, "contact/index.html"),
        "surveyol_form_url": SURVEYOL_FORM_URL,
        "surveyol_embed_url": SURVEYOL_EMBED_URL,
    }
    return html.format(**links)


def render_nav(active_key: str, prefix: str) -> str:
    items = []
    for key, output, label in NAV:
        current = ' aria-current="page"' if key == active_key else ""
        items.append(f'<a href="{page_url(prefix, output)}"{current}>{escape(label)}</a>')
    return "\n        ".join(items)


def render_head(page: Page, prefix: str) -> str:
    title = escape(strip_entities(page.title))
    description = escape(page.description)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Christian Thought Survey</title>
  <meta name="description" content="{description}">
  <link rel="icon" href="{prefix}assets/cts-logo.png">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>"""


def render_header(page: Page, prefix: str) -> str:
    return f"""<body class="page-{page.key}">
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header">
    <nav class="nav" aria-label="Primary">
      <a class="brand" href="{page_url(prefix, "index.html")}">
        <img src="{prefix}assets/cts-logo.png" alt="CTS logo" width="42" height="42">
        <span>Christian Thought Survey</span>
      </a>
      <div class="nav-links">
        {render_nav(page.key, prefix)}
      </div>
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
          <p class="lede"><strong>Christian Thought Survey is being revived as a weekly research project for Christian ministers.</strong> Instead of asking participants to complete another long 200-item instrument, the new format will focus on one issue at a time: up to ten carefully worded survey items, mostly answered on 0-100 credence sliders, followed by a vote on the next topic.</p>
          <div class="button-row">
            <a class="button" href="{page_url(prefix, "weekly-survey-reports/index.html")}">Weekly Survey Reports</a>
            <a class="button secondary" href="{page_url(prefix, "previous-results-archive/index.html")}">Previous Results Archive</a>
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
      <p>Christian Thought Survey. Static mirror updated from WordPress on {UPDATED}.</p>
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
  <p>The page you were looking for is not part of this static CTS mirror.</p>
  <div class="button-row">
    <a class="button light" href="{home_url}">Return home</a>
    <a class="button light" href="{archive_url}">Browse the archive</a>
  </div>
</div>
""",
    )
    path = ROOT / page.output
    path.write_text(render_page(page), encoding="utf-8")


def main() -> int:
    for page in PAGES:
        write_page(page)
    write_404()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
