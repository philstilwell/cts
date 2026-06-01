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
CLOUDFLARE_ANALYTICS = "<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"b86c3e7a273f47648ae70f08866f9ec5\"}'></script><!-- End Cloudflare Web Analytics -->"
WEEKLY_STRUCTURE_LIST = """<ol class="process-list" type="A">
  <li><strong>One CTS-administered topic:</strong> 12 related survey items from the CTS topic bank.</li>
  <li><strong>Three participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week's participant vote.</li>
  <li><strong>A participant-nominated item ballot:</strong> a list of 'purified' participant-nominated survey items from the previous week that active participants can vote on for the following week.</li>
  <li>A text box to suggest survey items to be voted on next week and possibly featured in the following week's survey.</li>
  <li><strong>A previous-results summary and link:</strong> a brief summary and a link to the primary CTS website page containing the previous week's results.</li>
</ol>"""
RESPONSE_RULE_NOTE = "The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses."


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
            "A weekly research project for Christian ministers, built around 12 "
            "CTS-administered survey items, 3 participant-vote-determined questions, "
            "credence sliders, a participant-nominated item ballot, and survey-item suggestions."
        ),
        content="""
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
        <li><strong>Ongoing item voting:</strong> every weekly survey includes a 'purified' participant-nominated item ballot and a text box for next-week suggestions.</li>
      </ul>
    </div>
  </div>
</section>

<section class="content-band shade">
  <div class="container two-column">
    <div>
      <p class="section-label">Weekly structure</p>
      <h2>Every survey has a five-part rhythm.</h2>
      <p class="section-copy">The CTS administration supplies the main topic, active participants help choose participant-generated questions, and each survey collects suggestions for the next round.</p>
    </div>
    <div class="wp-content">
      {weekly_structure_list}
      <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>
    </div>
  </div>
</section>

<section class="content-band">
  <div class="container two-column">
    <div>
      <p class="section-label">Current status</p>
      <h2>The 2026 weekly cycle is being prepared.</h2>
    </div>
    <div class="wp-content">
      <p>Reports are planned for Fridays so pastors and other ministry leaders can reflect on the results before Sunday. Public summaries will be posted here, and the project is being designed so appropriately prepared raw data can be shared for independent analysis.</p>
      <p>When the first weekly survey is fielded, this site will point to the current survey, the current report, the participant-vote-determined questions, the participant-nominated item ballot, the suggestion text box, the previous-results summary and link, and the raw-data download policy.</p>
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
            "The collection point for weekly Christian Thought Survey reports and the "
            "five-part weekly survey process."
        ),
        content="""
<div class="wp-content">
  <p>This page will collect the weekly Christian Thought Survey reports once the 2026 cycle begins. Each survey will focus on one doctrinal, practical, or sociological issue of interest to Christian ministers while also carrying forward participant-vote-determined questions and future survey-item suggestions.</p>

  <h2>Weekly survey structure</h2>
  <p>Each Weekly Survey will include five parts:</p>
  {weekly_structure_list}
  <p>The cycle is cumulative: participant suggestions submitted in one weekly survey are refined, placed on the next ballot, and the top 3 selected items become live survey items in the following week's survey.</p>
  <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>

  <h2>Report format</h2>
  <ul>
    <li><strong>Issue:</strong> the weekly CTS-administered topic and the reason it was selected.</li>
    <li><strong>Administered items:</strong> the exact wording of the 12 CTS-provided survey items.</li>
    <li><strong>Participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week's participant vote.</li>
    <li><strong>Credence results:</strong> summary statistics for slider responses across all live survey items.</li>
    <li><strong>Subgroup comparisons:</strong> denominational, role, ministry-experience, or other comparisons when sample size permits.</li>
    <li><strong>Participant-nominated item ballot:</strong> the ranked result from voting on last week's 'purified' participant-nominated survey items.</li>
    <li><strong>Suggestion text box:</strong> a summary of suggested survey items when they can be shared responsibly.</li>
    <li><strong>Previous-results summary and link:</strong> the brief summary and primary CTS website link included in the survey.</li>
    <li><strong>Data release:</strong> a link to raw or prepared data when privacy and formatting checks are complete.</li>
  </ul>

  <h2>Report index</h2>
  <figure>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>CTS-administered topic</th>
          <th>Participant-vote-determined questions</th>
          <th>Participant-nominated item ballot</th>
          <th>Status</th>
          <th>Report</th>
          <th>Data</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Upcoming</td>
          <td>First weekly topic</td>
          <td>Chosen based on participant vote</td>
          <td>Opens after first participant suggestions</td>
          <td>In preparation</td>
          <td>Pending</td>
          <td>Pending</td>
        </tr>
      </tbody>
    </table>
  </figure>

  <p class="callout">Raw data will not include direct email identifiers in public files. Participant attributes may be grouped or suppressed when needed to avoid accidental identification. Free-text suggestions may be edited, grouped, or withheld before publication to protect privacy and keep item wording usable. See the <a href="{privacy_url}">Privacy &amp; Data Release</a> page for the current policy.</p>
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
  <p>The original Christian Thought Survey project produced long-form surveys, item-level pages, mini-surveys, and extensive result reports. Those materials are now gathered here as an archive while the front of the site shifts toward the 2026 weekly survey format: 12 CTS-administered items, 3 participant-vote-determined questions, a participant-nominated item ballot, a suggestion text box, and a previous-results summary and link.</p>

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

  <h2>How the weekly cycle works</h2>
  {weekly_structure_list}
  <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>

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
            "Contact and participation notes for ministers, ministry leaders, weekly "
            "survey participation, future question suggestions, and data questions."
        ),
        content="""
<div class="wp-content">
  <p>The 2026 project will begin with prior CTS participants who indicated that email follow-up is welcome. If you are currently or previously engaged in full-time ministry and would like to be considered for later invitations, participant voting, future question suggestions, or data/citation questions, use the form below.</p>

  <p>Each Weekly Survey will include five parts:</p>
  {weekly_structure_list}
  <p class="callout"><strong>Response rule:</strong> {response_rule_note}</p>

  <p class="callout"><strong>Participation note:</strong> CTS weekly survey participation is intended for people who are currently or previously engaged in full-time ministry.</p>

  <div class="surveyol-embed">
    <iframe title="CTS 2026 Participation Request" src="{surveyol_embed_url}" loading="lazy"></iframe>
  </div>

  <p class="form-note">If the embedded form does not load, <a href="{surveyol_form_url}">open the SurveyOL form in a new tab</a>. The same full-time ministry participation note applies.</p>
  <p class="form-note">Contact information is used for CTS participation and follow-up only. See <a href="{privacy_url}">Privacy &amp; Data Release</a> for the current data handling policy.</p>
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
        "privacy_url": page_url(prefix, "privacy-data-release/index.html"),
        "overview_url": page_url(prefix, "overview/index.html"),
        "contact_url": page_url(prefix, "contact/index.html"),
        "surveyol_form_url": SURVEYOL_FORM_URL,
        "surveyol_embed_url": SURVEYOL_EMBED_URL,
        "weekly_structure_list": WEEKLY_STRUCTURE_LIST,
        "response_rule_note": RESPONSE_RULE_NOTE,
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
  {CLOUDFLARE_ANALYTICS}
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
          <p class="lede"><strong>Christian Thought Survey is being revived as a weekly research project for Christian ministers.</strong> Each Weekly Survey will pair one CTS-administered topic with 12 related items, 3 participant-vote-determined questions, a participant-nominated item ballot, a suggestion text box, and a previous-results summary and link.</p>
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
