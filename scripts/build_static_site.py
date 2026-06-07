#!/usr/bin/env python3
"""Build the static GitHub Pages version of the revived CTS pages."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://christianthoughtsurvey.com"
WP_SITE = "https://christianthoughtsurvey.wordpress.com"
UPDATED = "June 3, 2026"
SURVEYOL_FORM_URL = "https://www.surveyol.com/r/C33E5B3"
SURVEYOL_EMBED_URL = "https://www.surveyol.com/s2/1BA7FF3"
WEEK_1_REPORT_OUTPUT = "weekly-survey-reports/week-001-divorce-and-remarriage/index.html"
NEWSLETTER_CONFIRMATION_OUTPUT = "email-confirmation/index.html"
OG_IMAGE = f"{SITE_URL}/assets/cts-research-overview.png"
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
  <li><strong>One CTS-administered topic:</strong> 12 related survey items from the CTS topic bank.</li>
  <li><strong>Three participant-vote-determined questions:</strong> 3 additional live survey items chosen based on the previous week's participant vote. These are intentionally independent from the weekly CTS-administered topic.</li>
  <li><strong>A participant-nominated item ballot:</strong> 7 AI-polished ballot items selected from the previous week's participant nominations, with AI-created seed items added only when fewer than 7 suitable participant nominations are available. Ballot items are selected for clarity, relevance, novelty, and likely participant tension.</li>
  <li><strong>A text box:</strong> to suggest survey items to be voted on next week and possibly featured in the following week's survey.</li>
  <li><strong>Last week's results summary and link:</strong> a brief summary and a link to the primary CTS website page containing the previous week's results and reports.</li>
  <li><strong>A preview of upcoming topics:</strong> The topics for the next three weeks will be featured to allow for mental preparation.</li>
</ol>"""
RESPONSE_RULE_NOTE = "The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses."
PARTICIPANT_BALLOT_NOTE = "Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, likely participant tension, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked eligible items become live participant-vote-determined survey items in the following week's survey."


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
            "A weekly research project for Christian ministers, built around 12 "
            "CTS-administered survey items, 3 participant-vote-determined questions, "
            "credence sliders, a 7-item AI-polished participant-nominated item ballot, survey-item suggestions, "
            "last week's results summary and link, and a preview of upcoming topics."
        ),
        content="""
<section class="content-band shade report-spotlight-band">
  <div class="container latest-report">
    <div class="latest-report-copy">
      <p class="section-label">Latest weekly report</p>
      <h2>Week 1: Divorce and Remarriage</h2>
      <p class="section-copy">For most visitors, weekly results should be the fastest path through the site. The Week 1 report page is already live as the stable destination, and it will be filled after responses are reviewed.</p>
      <div class="report-meta-grid" aria-label="Latest report status">
        <div class="meta-chip">
          <span>Status</span>
          <strong>Results pending</strong>
        </div>
        <div class="meta-chip">
          <span>Publication rhythm</span>
          <strong>Friday reports</strong>
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
      <span class="report-status pending">Pending</span>
      <strong>Report page ready</strong>
      <p>Once Week 1 responses are reviewed, the report will hold the summary, key tensions, chart previews, ballot results, and data-release notes.</p>
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
            "The collection point for weekly Christian Thought Survey reports and the "
            "six-part weekly survey process."
        ),
        content="""
<div class="wp-content results-hub">
  <p>This page is the public hub for weekly Christian Thought Survey results. The newest report is featured first; earlier weekly reports appear below in a compact grid so readers can scan topics quickly.</p>

  <section class="latest-report-card" aria-labelledby="latest-report-heading">
    <div>
      <p class="section-label">Newest report</p>
      <h2 id="latest-report-heading">Week 1: Divorce and Remarriage</h2>
      <p>The stable report page is published now. Results, key tensions, chart previews, ballot outcomes, and data-release notes will be added after responses are reviewed.</p>
      <div class="button-row">
        <a class="button" href="{week_1_report_url}">Open Full Report</a>
      </div>
    </div>
    <dl class="report-meta-list">
      <div>
        <dt>Status</dt>
        <dd>Results pending</dd>
      </div>
      <div>
        <dt>Survey topic</dt>
        <dd>Divorce and Remarriage</dd>
      </div>
      <div>
        <dt>Report rhythm</dt>
        <dd>Friday after response review</dd>
      </div>
    </dl>
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

  <h2>Weekly report grid</h2>
  <div class="report-preview-grid">
    <a class="report-preview-card" href="{week_1_report_url}">
      <span class="report-week">Week 1</span>
      <strong>Divorce and Remarriage</strong>
      <span class="report-status pending">Results pending</span>
      <span>12 featured-topic items, 3 independent live items, a 7-item ballot, and upcoming topic previews.</span>
    </a>
  </div>

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
      <p>The regular send rhythm is a Monday heads-up email and a Thursday SurveyOL survey-link email. The Monday email names the current topic and previews the next 3 planned general topics; the Thursday survey includes that same preview of upcoming topics inside the survey itself.</p>
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
        eyebrow="Results pending",
        description=(
            "The stable Week 1 Christian Thought Survey report page for Divorce "
            "and Remarriage, prepared for public results once responses are reviewed."
        ),
        content="""
<div class="wp-content">
  <p>This is the stable public page for the first revived weekly Christian Thought Survey report. Results are not posted yet. The survey is in launch preparation, and the SurveyOL response link is distributed by email rather than posted publicly.</p>

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
      <strong>Pending responses</strong>
      <p>Public interpretation, charts, and data notes will be added after review.</p>
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
      <p>Means, medians, response counts, distribution shape, and a concise interpretation for all live slider items.</p>
    </section>
    <section class="report-card">
      <h3>Key tensions</h3>
      <p>The items and themes with significant disagreement, spread, or subgroup contrast.</p>
    </section>
    <section class="report-card">
      <h3>Distribution visuals</h3>
      <p>Compact sparkline-style distribution strips for every credence item, using a shared scale when sample size permits.</p>
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

  <h2>Results template</h2>
  <figure>
    <table>
      <thead>
        <tr>
          <th>Section</th>
          <th>What will appear here</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Field dates and response count</td>
          <td>Survey window, completed responses, and any response-quality notes.</td>
          <td>Pending</td>
        </tr>
        <tr>
          <td>Featured-topic items</td>
          <td>12 Divorce and Remarriage item summaries with 0-100 credence distributions.</td>
          <td>Pending</td>
        </tr>
        <tr>
          <td>Independent items</td>
          <td>3 orthogonal live items chosen for relevance and meaningful participant spread.</td>
          <td>Pending</td>
        </tr>
        <tr>
          <td>Key tensions</td>
          <td>Items where disagreement is substantial enough to merit interpretation.</td>
          <td>Pending</td>
        </tr>
        <tr>
          <td>Participant ballot</td>
          <td>7 ranked participant-nominated or seed items, with winners for the next survey.</td>
          <td>Pending</td>
        </tr>
        <tr>
          <td>Data release</td>
          <td>Prepared data or a release note after privacy and formatting review.</td>
          <td>Pending</td>
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
            "A signup form for readers who want Christian Thought Survey report "
            "notices, topic previews, and occasional articles without joining the "
            "weekly survey participant panel."
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
        key="contact",
        output="contact/index.html",
        nav_label="Contact",
        title="Contact &amp; Weekly Survey Participation",
        eyebrow="Participation",
        description=(
            "Contact and participation notes for ministers, ministry leaders, weekly "
            "survey participation, future survey-item suggestions, and data questions."
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
  <p>The regular send rhythm is a Monday heads-up email and a Thursday SurveyOL survey-link email.</p>
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


def fill_links(html: str, prefix: str) -> str:
    links = {
        "home_url": page_url(prefix, "index.html"),
        "weekly_url": page_url(prefix, "weekly-survey-reports/index.html"),
        "week_1_report_url": page_url(prefix, WEEK_1_REPORT_OUTPUT),
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
    title = escape(strip_entities(page.title))
    description = escape(page.description)
    canonical = canonical_url(page.output)
    robots = f'\n  <meta name="robots" content="{escape(page.robots)}">' if page.robots else ""
    extra_head = f"\n  {MAILERLITE_UNIVERSAL_SCRIPT}" if page.key == "newsletter" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Christian Thought Survey</title>
  <meta name="description" content="{description}">{robots}
  <link rel="canonical" href="{canonical}">
  <meta property="og:site_name" content="Christian Thought Survey">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} | Christian Thought Survey">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1600">
  <meta property="og:image:height" content="900">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} | Christian Thought Survey">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="icon" href="{prefix}assets/cts-logo.png">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  {CLOUDFLARE_ANALYTICS}{extra_head}
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
          <p class="lede"><strong>Christian Thought Survey is being revived as a weekly research project for Christian ministers.</strong> Each Weekly Survey will pair one CTS-administered topic with 12 related items, 3 participant-vote-determined questions, a 7-item AI-polished participant-nominated item ballot, a suggestion text box, last week's results summary and link, and a preview of upcoming topics.</p>
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


def main() -> int:
    for page in PAGES:
        write_page(page)
    write_404()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
