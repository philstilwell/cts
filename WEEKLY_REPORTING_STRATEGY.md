# CTS Weekly Reporting Strategy

This document is a planning reference for deciding what kinds of reports Christian Thought Survey should publish during the revived weekly survey cycle. It is intentionally strategic rather than implementation-specific, so it can guide both Google Sheets-based reporting and future interactive GitHub Pages reports.

## Working Recommendation

Use a dual reporting model:

1. Publish a public interactive weekly report on the CTS website.
2. Produce a static one-page PDF or PNG summary for email, archive, and quick sharing.
3. Use Google Sheets charts/screenshots as the near-term production method while the first SurveyOL exports are being standardized.
4. Keep Google Sheets as the long-term backup and prototyping environment even after interactive reports mature.

The interactive report can become the primary public experience once the pipeline is stable. Until then, a well-designed Google Sheet that produces screenshot-ready chart panels is likely the fastest path to attractive, reliable public reports. Static report images should remain even later because they are easy to email, cite, archive, and compare week by week.

## Reviewed Reference Materials

Public old-site materials reviewed:

- [Christian Thought Survey Demographics PDF](https://christianthoughtsurvey.wordpress.com/wp-content/uploads/2024/01/general-stats-final-b.pdf)
- [2024 Full Results](https://christianthoughtsurvey.wordpress.com/cts-2024-results/)
- [2023 Full Results](https://christianthoughtsurvey.wordpress.com/cts-2023-results/)
- [2023 Limited Results](https://christianthoughtsurvey.wordpress.com/2023a-stats/)
- [2022 Results](https://christianthoughtsurvey.wordpress.com/2022b-stats/)
- [Combined Stats](https://christianthoughtsurvey.wordpress.com/results-preliminary/)
- Representative item pages such as [Item 1](https://christianthoughtsurvey.wordpress.com/item-1/)

Private CTS 2026 participant registry reviewed only at the structural/header level. It should not be linked from public documents or exposed in public report files.

## What The Old Reports Did Well

The old reports had several strengths worth preserving:

- They showed real distributions, not just averages.
- They included a substantial demographic snapshot of the participant pool.
- They made the survey feel data-rich and serious.
- Google Sheets made it possible to create charts quickly without a complex publishing stack.
- The item-level charts were compact enough to scan quickly.
- The one-page demographics PDF gave readers an immediate sense of who the participants were.

The demographics PDF is especially useful as a model for a "participant context" dashboard. It reported 406 completed surveys, movement toward or away from conservatism, participant education, region, ministry experience, Bible reading history, congregation size, and broad participant-pool averages such as evangelical/fundamentalist identification and ministry status.

## What Should Improve

The old approach also had limits:

- Static screenshots and PDFs do not let readers filter, hover, or drill into results.
- Dense axes and labels can become difficult to read, especially on mobile.
- Spreadsheet screenshots can look less polished than purpose-built report pages.
- Word clouds are visually memorable but weak as evidence; they should be treated as secondary texture, not primary analysis.
- Item-level charts need more context: sample size, median, uncertainty or spread, and plain-language interpretation.
- Subgroup comparisons need clear privacy thresholds and consistent suppression rules.

## Participant Data To Consider

The private CTS 2026 participant registry appears to contain 599 rows and includes a 396-contact "Friendly Outreach List = Yes" subset. This contact-level data should support outreach, response tracking, and aggregate composition checks, but it should not become public reporting data.

Useful aggregate dimensions available from the participant registry include:

- Religious identification.
- Belief in Jesus' divinity.
- Year of birth and approximate age.
- Year of Christian conversion and years since conversion.
- Denomination or fellowship affiliation.
- Evangelical and fundamentalist self-identification.
- Religious education, secular education, Bible college, and seminary experience.
- Part-time and full-time ministry years.
- Current full-time and part-time ministry status.
- Scripture reading history.
- Local community religious composition.
- Main-service weekly attendance.
- Current location and broad region.
- Countries lived outside native country.
- Gender, marital status, children, and race.
- Data-quality flags and fields to reconfirm.

The source-field map indicates that old stance-response columns were intentionally excluded from the current participant registry. Treat the registry as contact/demographic infrastructure, not as the source of weekly item results.

## Core Report Types

### 1. Weekly Public Brief

This should be the standard report linked from the CTS website each Friday.

Recommended sections:

- Topic, field dates, response count, and response window.
- A 3-5 sentence executive summary.
- A one-line reminder that participants are current or former full-time ministers.
- A 15-item overview: 12 CTS-administered topic items plus 3 participant-vote-determined items.
- Item cards with mean, IQR, Doubt/Dogma, standard deviation, and distribution.
- A short "what ministers may notice" interpretation section.
- A "Key tensions" section naming the items or themes where participants significantly disagree.
- Ballot results showing which participant-nominated items were ranked highest.
- The next 3 planned topics.
- Methodology and privacy note.

#### Canonical Weekly Results Display

Use the Week 1 revised results display as the standard for weekly survey reports unless a future report has a clearly documented reason to depart from it.

##### 15-Item Overview Table

The public overview table should use exactly these reader-facing columns:

- `Item`: item number, short label, and full survey statement.
- `Mean`: average 0-100 credence score.
- `IQR`: interquartile range, with the pop-up explanation used in Week 1.
- `Doubt/Dogma`: shown as `n:m`, where `n` is the count of non-endpoint responses from 1-99 and `m` is the count of endpoint responses exactly 0 or 100. Include the explanatory pop-up used in Week 1.
- `Distribution`: an observed 10-bin sparkline with light neighbor smoothing, using the shared fixed 0-100 report scale and a visible 100% marker.

Do not include `Median` or `Low / Mid / High` as columns in the overview table. Keep low/middle/high band counts in the public JSON for analysis and fallback rendering, but do not foreground them in the primary report table.

##### Item-Level Detail Cards

Each item card should show the same visual grammar as Week 1:

- Four compact stat boxes: `Mean`, `IQR`, `Doubt/Dogma`, and `SD`.
- No `Median` stat box.
- A left-side label reading `Observed 10-bin distribution`.
- A right-side 10-bin sparkline on a plain white field.
- A 100% guide line and fully visible `100%` label.
- No appended `low X, middle Y, high Z; n=...` legend text.

##### Sparkline Rendering

The public sparkline is a display of observed 10-bin response percentages with light neighbor smoothing. The older S23-smoothed series may remain in the JSON for audit/history, but it should not drive the public bar heights because endpoint padding can visually overstate endpoint-heavy items.

- Use 10 bins: 0-10, 10-20, ..., 90-100.
- Count observed responses directly into the 10 bins, with 90-100 including exact 100.
- Add only 3% of each natural neighboring bin to the plotted value. Do not pad endpoints.
- Store this reader-facing series as `distribution.display_percentages`.
- Public renderers must not fall back to `s23_smoothed_percentages` for bar heights. If `display_percentages` is absent, compute the observed-smoothed display series from `simple_counts` and `n`.
- Use a fixed public display scale of 0-100 after capping, with no visual headroom above 100.
- Draw the 100% guide line at the top of the plot area so a true 100% bin reaches the marker.
- Use a plain white chart field without background tint or auxiliary grid lines.
- Color low bins with brick, middle bins with gold, and high bins with teal.

### 2. Interactive Item Explorer

This should be embedded inside each weekly report or linked as an expandable section.

Recommended controls:

- Toggle between all responses and eligible subgroups.
- Sort items by mean, IQR/spread, Doubt/Dogma, distribution shape, or item order.
- Hover for exact counts and percentages.
- Switch chart mode between distribution, dot-and-interval, and subgroup heatmap.
- Download static chart image or summary CSV where appropriate.

### 3. One-Page Static Dashboard

This should preserve the spirit of the old demographics PDF, but be cleaner and more readable.

Recommended content:

- Topic name and week number.
- Total completed responses.
- Top 3 strongest consensus items.
- Top 3 key tensions or most contested items.
- Mini distribution strips for all 15 live items.
- Ballot winner list.
- Respondent composition snapshot.
- Link/QR code to the full interactive report.

### 4. Ballot And Nominations Report

This should document how participant-generated material moves through the weekly cycle.

Recommended content:

- The 7 AI-polished ballot items.
- Ranking results using a Borda-style score or equivalent rank-choice summary.
- The top 3 items selected for the next week's live survey.
- Count of raw nominations received.
- Count excluded or merged, without exposing identifying text.
- Short note explaining that AI polishing improves clarity, neutrality, credence-slider suitability, breadth, novelty, and pastoral/theological relevance.

### 5. Participant Composition Dashboard

This should be published periodically, not necessarily every week.

Recommended cadence:

- Small composition strip in every weekly report.
- Fuller demographic dashboard monthly or quarterly.

Recommended dimensions:

- Current or former full-time ministry status.
- Denominational or fellowship family.
- Ministry years.
- Region.
- Age band.
- Education bands.
- Congregation size bands.

### 6. Quarterly Pulse Report

Every 10-13 weeks, publish a synthesis report that looks across topics.

Recommended content:

- Highest-consensus items across the quarter.
- Most polarizing items.
- Repeated patterns by ministry experience, denomination family, or region when sample size permits.
- Topic participation trends.
- Participant-nominated themes that keep returning.
- A preview of planned future topics.

### 7. Data And Methods Appendix

Each weekly report should link to a consistent methods page or appendix.

Recommended content:

- Survey dates.
- Survey platform.
- Response format: 0-100 credence sliders.
- Meaning of 0, 50, and 100.
- How participant-nominated items are polished and scored.
- Subgroup suppression rules.
- Data-release policy.
- Known limitations.

## Best Chart Types For 0-100 Credence Sliders

### Use In Every Weekly Report

- Mini histogram strips for each live item.
- Dot-and-interval charts showing median and interquartile range.
- Ranked item table with mean, IQR, Doubt/Dogma, standard deviation, and distribution shape.
- Diverging distribution bars using 0-33, 34-66, and 67-100 bands only as secondary or fallback summaries when a simple broad-band view is useful.

## Google Sheets Sparkline Distribution Formula

Google Sheets' [`SPARKLINE`](https://support.google.com/docs/answer/3093289) function creates a miniature chart inside a single cell. The old Google Sheets chart shown in the S23 workbook uses this formula pattern:

```gs
=SPARKLINE(AL18:AL27,{"charttype","column";"ymax",120;"ymin",0;"color","charcoal"})
```

Important distinction: the `SPARKLINE` formula is mainly the display layer. The more important and more carefully honed formulas are the formulas that produce the values in `AL18:AL27`. Those cells transform raw 0-100 credence responses into a compact, smoothed percentage distribution. Preserve that distribution-series method as a first-class part of the reporting system, not as incidental helper-cell logic.

What it does:

- `AL18:AL27` supplies the plotted data. It is a carefully designed 10-value distribution series for a single survey item, not the raw 0-100 credence responses themselves.
- `"charttype","column"` makes the sparkline a tiny vertical-column histogram inside one cell.
- `"ymin",0` forces the chart baseline to zero.
- `"ymax",120` forces a shared vertical scale. This is important because it lets item sparklines be compared visually. Without a shared `ymax`, every sparkline auto-scales and weak patterns can look as strong as major patterns.
- `"color","charcoal"` sets the column color. A hex value such as `"#334155"` can be used if a named color is inconsistent.

### Preserve The Historical S23 Distribution-Series Formula

The `Filt` tab in the old `S23 — CTS` workbook uses this formula architecture for item column `AL`. Preserve it as a documented reference and possible analytical helper, but use the observed-smoothed `display_percentages` series for public report bars.

```gs
AL17 = COUNT(AL33:AL)
```

Rows `AL6:AL15` count responses into 10-point credence buckets while splitting exact boundary values across neighboring buckets. For example:

```gs
AL6  = COUNTIFS(AL$33:AL,">="&$AK5,AL$33:AL,"<"&$AK6)
       +(COUNTIF(AL$33:AL,"="&$AK5)/2)
       +(COUNTIF(AL$33:AL,"="&$AK6)/2)

AL7  = COUNTIFS(AL$33:AL,">"&$AK6,AL$33:AL,"<"&$AK7)
       +(COUNTIF(AL$33:AL,"="&$AK6)/2)
       +(COUNTIF(AL$33:AL,"="&$AK7)/2)

...

AL15 = COUNTIFS(AL$33:AL,">"&$AK14,AL$33:AL,"<="&$AK15)
       +(COUNTIF(AL$33:AL,"="&$AK14)/2)
       +(COUNTIF(AL$33:AL,"="&$AK15)/2)
```

Rows `AL5` and `AL16` pad the endpoints:

```gs
AL5  = AL6
AL16 = AL15
```

Rows `AL18:AL27` then create the actual sparkline series by converting each bucket to a percentage of total responses and adding 3% of the neighboring bucket values:

```gs
AL18 = ((AL5*0.03+AL6+AL7*0.03)/AL$17)*100
AL19 = ((AL6*0.03+AL7+AL8*0.03)/AL$17)*100
AL20 = ((AL7*0.03+AL8+AL9*0.03)/AL$17)*100
AL21 = ((AL8*0.03+AL9+AL10*0.03)/AL$17)*100
AL22 = ((AL9*0.03+AL10+AL11*0.03)/AL$17)*100
AL23 = ((AL10*0.03+AL11+AL12*0.03)/AL$17)*100
AL24 = ((AL11*0.03+AL12+AL13*0.03)/AL$17)*100
AL25 = ((AL12*0.03+AL13+AL14*0.03)/AL$17)*100
AL26 = ((AL13*0.03+AL14+AL15*0.03)/AL$17)*100
AL27 = ((AL14*0.03+AL15+AL16*0.03)/AL$17)*100
```

Why this is worth preserving as a reference:

- Exact boundary responses such as 10, 20, 50, and 100 are handled gracefully instead of being forced awkwardly into one bucket.
- Endpoint padding keeps the first and last visible buckets from behaving differently just because they have only one natural neighbor.
- The 3% adjacent-bucket smoothing keeps the mini-chart readable without erasing strong distribution features.
- S23 display values must be capped at 100% if rendered, because endpoint-heavy items can otherwise exceed 100% visually even though no bin can represent more than the full response count.
- The values become percentages, so the shape can be compared across items with different response counts.
- The method preserves the "pulse" of all credences much better than a mean or median alone.

For revived CTS public reports, keep the basic insight that the sparkline displays a prepared distribution series, but make that series the endpoint-aware observed-smoothed `display_percentages` field. Use a shared report-level maximum:

```gs
=SPARKLINE(AL18:AL27,{"charttype","column";"ymin",0;"ymax",$B$2;"color","#334155"})
```

Where `$B$2` contains the fixed public display maximum for the whole report:

```gs
=100
```

This gives all 15 item sparklines the same scale and makes a true 100% bin reach the 100% marker.

When creating the revived CTS reporting sheet, keep the recovered S23 formula architecture available as a reference, but build the public `display_percentages` from direct 10-point observed buckets plus 3% natural-neighbor smoothing. A direct generic formula is possible:

```gs
=LET(
  raw,FILTER(Responses!B2:B,ISNUMBER(Responses!B2:B)),
  n,COUNT(raw),
  bins,MAP(SEQUENCE(10,1,0,10),LAMBDA(lo,COUNTIFS(raw,">="&lo,raw,IF(lo=90,"<=100","<"&lo+10)))),
  padded,HSTACK(0,bins,0),
  display,MAP(SEQUENCE(10),LAMBDA(i,((INDEX(padded,1,i)*0.03+INDEX(padded,1,i+1)+INDEX(padded,1,i+2)*0.03)/n)*100)),
  SPARKLINE(display,{"charttype","column";"ymin",0;"ymax",$B$2;"color","#334155"})
)
```

Recommended cut points for 0-100 credence sliders:

- 0
- 10
- 20
- 30
- 40
- 50
- 60
- 70
- 80
- 90
- 100

For public display, exact cut-point responses should stay in the observed bin where the survey value naturally lands; exact 100 belongs in the 90-100 bin. Boundary splitting belongs only to the archived S23 reference method.

Use the sparkline in public results when there is enough data to make the distribution meaningful. Recommended minimums:

- All-response item sparkline: show at `n >= 30`; prefer `n >= 50`.
- Subgroup sparkline: show only at `n >= 30`; otherwise use a simpler summary or suppress the subgroup view.
- If `n < 30`, show `n`, mean, IQR, Doubt/Dogma, and perhaps a 3-band summary instead of a 10-bin sparkline.

### Use For Deeper Analysis

- Full histograms or density plots for individual item pages.
- Ridgeline plots for comparing all 12 topic items at once.
- Heatmaps for item-by-subgroup medians.
- Consensus/disagreement scatterplot: item median on one axis, spread on the other.
- Slope charts when a recurring item is asked again in a later survey.
- Ballot rank charts showing Borda score, first-place votes, and top-3 frequency.

## Key Tensions

Each weekly report should include a short "Key tensions" section when the data shows meaningful disagreement. This section should be descriptive and pastoral rather than combative: the point is to help ministers see where thoughtful participants are divided, not to manufacture controversy.

Good candidates for "Key tensions":

- Items with high interquartile range or standard deviation.
- Items with visibly bimodal or multi-peaked distributions.
- Items where a large share of responses cluster near both low and high credence values.
- Items where subgroup medians diverge meaningfully and the subgroup counts pass privacy thresholds.
- Items where the written interpretation reveals an unresolved practical or doctrinal tension.

Recommended presentation:

- Name 2-4 key tensions when they exist.
- Pair each tension with one compact distribution chart.
- Include the relevant `n`, median, and disagreement score.
- Use neutral wording such as "Participants divided over..." or "A notable tension appeared around..."
- Avoid implying that disagreement is bad; disagreement may identify an area where ministers need more careful categories.
- If the week shows strong consensus and no major tension, say that directly instead of forcing a "Key tensions" section.

## Scatterplot And Correlation Reports

Scatterplots should be available as a higher-value reporting tool when the sample size and data quality support them. They should not be a default element in every weekly report, because correlations can easily look more meaningful than they are.

Best CTS use cases:

- Item-to-item relationships among the 15 live credence-slider items.
- A topic item compared with ministry years, age band, education years, or congregation size.
- Repeated-item change over time when the same or similar item appears in later surveys.
- Participant-nominated ballot preference compared with a related live survey item.
- Consensus/disagreement maps where each point is an item, with median on one axis and spread on the other.

Recommended thresholds:

- Overall scatterplot: show at `n >= 50`; prefer `n >= 100`.
- Subgroup scatterplot: show only when each displayed subgroup has `n >= 30`; prefer `n >= 50`.
- Trendline or correlation coefficient: show only when the relationship is visually clear enough to interpret and the variables are suitable.
- Sensitive or identifying outliers: suppress, aggregate, jitter, or omit the chart.

Recommended public presentation:

- Show `n` directly on the chart.
- Use transparent points, small point size, and optional jitter so overlapping 0-100 responses remain visible.
- Add a simple trendline only when it clarifies rather than decorates.
- Prefer Spearman correlation for bounded credence sliders and ordinal-ish variables; use Pearson only when the relationship is plausibly linear.
- Include a plain-language caveat that correlations are descriptive and not causal.
- Avoid publishing large fishing-expedition correlation grids without a clear interpretive purpose.

Google Sheets is sufficient for early scatterplot screenshots, especially for one or two carefully chosen relationships. HTML5/JavaScript scatterplots become more valuable when the report needs hover details, filtering, subgroup toggles, point transparency, marginal distributions, or multiple coordinated views. For GitHub Pages, Observable Plot or Plotly can both produce polished interactive scatterplots from prepared public summary data.

### Avoid As Primary Evidence

- Word clouds as the main result for free-text material.
- Pie charts with many categories.
- Averages without distribution shape.
- Subgroup comparisons without visible sample sizes.

## Interactive Charting Recommendation

For the static GitHub Pages site, use precomputed summary JSON and client-side charts.

Recommended stack:

- SurveyOL export CSV stays private.
- A local Python script with pandas cleans the export and produces public summary JSON.
- Public JSON contains only aggregate results, never names, emails, or raw free-text suggestions.
- GitHub Pages renders reports using HTML/CSS/JavaScript.
- Use Observable Plot for elegant, branded statistical charts, or Plotly if faster hover/tooling matters more than visual restraint.
- Keep Google Sheets available for quick validation, chart prototyping, and static PDF/PNG output.

Practical first choice: start with Google Sheets plus a static dashboard for Week 1, then build the first interactive item explorer from the same exported data before Week 2 or Week 3.

## Google Sheets Screenshot Workflow

Google Sheets can remain the report-production engine if the workbook is designed around screenshot-ready outputs rather than ordinary spreadsheet views.

Recommended workbook tabs:

- `Raw Export`: private SurveyOL export pasted/imported without public identifiers removed yet.
- `Clean Responses`: cleaned response table with names, emails, and direct identifiers removed or hidden.
- `Buckets`: 10-bin counts for each 0-100 credence item.
- `Stats`: n, mean, median retained for analysis, interquartile range, standard deviation, disagreement score, Doubt/Dogma counts, and key-tension flag for each item.
- `Ballot`: ranked-choice or Borda-style summary for the participant-nominated ballot.
- `Subgroups`: aggregate subgroup summaries that pass suppression thresholds.
- `Public Charts`: screenshot-ready chart panels only.
- `QA`: checks for missing values, out-of-range slider values, low-n subgroups, and accidental identifiers.

Recommended screenshot rules:

- Screenshot only the `Public Charts` tab or selected chart panels.
- Hide gridlines, row numbers, column letters, formulas, frozen panes, and private tabs before capturing.
- Use consistent chart dimensions every week.
- Use a fixed y-axis or shared `ymax` for comparable item sparklines.
- Include `n` directly on every chart or panel.
- Use the same item order as the survey unless a clearly labeled ranked view is being shown.
- Export or capture at high resolution so text remains readable on the website.
- Add a short written interpretation beside each screenshot on the public report page.

Recommended public outputs:

- A one-page dashboard screenshot for the weekly report.
- A 15-item sparkline distribution grid.
- A top-consensus/key-tensions panel.
- A scatterplot or correlation panel when the sample supports a useful relationship.
- A ballot results panel.
- A respondent composition panel when sample size permits.

This workflow should be treated as production-grade if the sheet is templated, tested, and kept private. The public site should display screenshots or exported chart images, not the live sheet itself, unless CTS intentionally creates a separate public-only workbook.

## Privacy And Suppression Rules

Recommended rules:

- Never publish names, email addresses, participant IDs, or direct contact fields.
- Do not publish raw free-text nominations.
- Remove accidental identifiers from nominations before any public summary.
- Publish subgroup results only when the subgroup has at least 15 responses.
- Prefer at least 20 responses for sensitive subgroup intersections.
- Combine categories when useful and honest.
- Show subgroup sample sizes directly on charts.
- Use prepared summary data for public files, not raw SurveyOL exports.
- Keep internal audit notes for participant-nominated item polishing and ballot selection.

## Style Direction

The reporting style should feel polished, public, and useful to ministers.

Recommended visual direction:

- Keep the CTS logo visible but modest.
- Use the old blue section-bar motif as a subtle inheritance, not as the whole design language.
- Use a restrained palette: dark text, white/light backgrounds, CTS blue, red accent, and one or two neutral comparison colors.
- Make the first screen communicate the topic, n, strongest finding, and most important key tension.
- Use tight dashboard typography rather than oversized marketing-style headings.
- Keep charts legible on mobile.
- Use downloadable chart images for readers who want to share or quote one result.
- Add concise written interpretation next to the charts; do not make readers infer every implication from visuals alone.

## Suggested Weekly Report Template

```text
Weekly Report: [Topic]
Fielded: [Date range]
Completed responses: [n]

Executive Summary
- Key finding 1
- Key finding 2
- Key finding 3
- Key tension, if one is significant enough to name early

Participant Context
- Current/former full-time ministry participant note
- Respondent composition snapshot

15 Live Items
- 12 CTS-administered topic items
- 3 participant-vote-determined items
- Item overview chart
- Item cards

Topic Analysis
- Strongest agreement
- Strongest disagreement
- Key tensions / most contested items
- Distribution patterns

Subgroup Notes
- Only where n permits
- Clearly show sample sizes

Participant-Nominated Ballot
- 7 polished ballot items
- Ranking outcome
- Top 3 selected for next week

Next Week
- Next survey topic
- Preview of next 3 planned topics

Methods And Data
- Slider scale
- Survey platform
- Privacy/suppression note
- Prepared data link if released
```

## Implementation Roadmap

### Before The First Public Weekly Report

- Decide the minimum public weekly report format.
- Create a reusable report page template.
- Decide the charting library for the interactive prototype.
- Create a private raw-data folder that is ignored by git.
- Create a public summary-data schema.
- Define subgroup suppression thresholds.
- Prepare the Week 1 static dashboard layout.

### Weeks 1-2

- Export SurveyOL results manually.
- Build a Google Sheets report for validation and backup.
- Create the first one-page static dashboard.
- Create the first public written weekly report.
- Draft the first summary JSON by hand or with a small script.

### Weeks 3-4

- Automate SurveyOL CSV cleaning.
- Generate weekly summary JSON automatically.
- Add interactive item charts to the GitHub Pages report.
- Add downloadable static chart images.
- Add a recurring report QA checklist.

### Quarter 1

- Publish a participant composition dashboard.
- Publish the first quarterly pulse report.
- Reassess whether Google Sheets remains a production step or becomes only a prototyping/backup tool.

## Recommended Decisions

1. Make the weekly public report the flagship product.
2. Keep the one-page static dashboard as a polished summary artifact.
3. Use the interactive report to show distribution detail, not just visual decoration.
4. Treat participant composition as context, not as the main story every week.
5. Suppress small subgroup reporting aggressively.
6. Use word clouds sparingly and only as a supplement to coded themes or nomination summaries.
7. Build the first interactive report around the 15 live credence-slider items before adding more elaborate features.
8. Keep report production simple enough to publish or refresh during the Tuesday morning report cycle without heroics.
