# CTS Data Pipeline Plan

This document defines the first practical data pipeline for weekly CTS reporting. It is safe to create before real responses arrive because it uses synthetic test data and keeps raw/private data ignored by git.

## Pipeline Goal

Convert a private SurveyOL export into a privacy-safe public summary that can feed:

- Google Sheets reporting dashboards.
- Static screenshot/PDF report assets.
- GitHub Pages HTML/JavaScript charts.
- Future interactive item explorers.

## Current Pipeline Layers

1. `CTS 2026`: canonical private participant registry and outreach status source.
2. `data/private/`: private, ignored inputs.
3. `reporting/week-001.config.json`: week-specific item and reporting configuration.
4. `scripts/cts_report_pipeline.py`: CSV-to-summary builder.
5. `schemas/public-weekly-summary.schema.json`: public summary shape.
6. `data/public/`: public, privacy-safe generated outputs.
7. `data/fixtures/`: synthetic data for dry runs.

## Participant Mapping Layer

Deep reports depend on a reliable private join between SurveyOL responses and the `CTS 2026` participant registry. The preferred path is:

1. Build each week's SurveyOL send list from `CTS 2026`, filtering out records with no `Name`, no usable `Primary Email Address`, no `Participant ID`, no `Email Key`, `Do Not Email? = Yes`, unsubscribed, opted out, bounced, or otherwise suppressed.
2. Send the weekly survey through a SurveyOL Email collector with `Anonymous Responses` set to `Off`. Close or avoid distributing Web Link collectors unless CTS intentionally wants an unmapped public response channel.
3. Include stable private join keys in SurveyOL contact fields when available: `Participant ID` and `Email Key`.
4. Save the exact weekly send-list crosswalk privately in `data/private/contact-crosswalks/week-###.csv`.
5. After export, normalize response email addresses by trimming whitespace and lowercasing, join responses to `CTS 2026`, and flag unmatched responses before producing any deep report.
6. Run subgroup and correlation analysis from the joined private file only after minimum-n suppression rules are in place.

## Week 1 Command

After exporting SurveyOL results, save the raw CSV here:

```text
data/private/surveyol/week-001.csv
```

Then run:

```bash
python3 scripts/cts_report_pipeline.py summarize \
  --config reporting/week-001.config.json \
  --input data/private/surveyol/week-001.csv \
  --output data/public/week-001-summary.json
```

Before publishing `data/public/week-001-summary.json`, review the `quality` section for:

- Missing item columns.
- Non-numeric slider values.
- Out-of-range slider values.
- Unexpectedly low `n`.

## Closed-Test Quarantine

SurveyOL preview-mode test responses are not included in real results, but submissions through the real respondent link are included. Closed-test rows must therefore be removed before building public summaries.

For Week 1, use one of these paths before the full launch or before final reporting:

1. Start the public launch from a copied/reset SurveyOL survey with zero responses.
2. Delete closed-test responses in SurveyOL before collecting authentic responses.
3. Export the raw SurveyOL file, save a private closed-test copy, remove known closed-test rows, and only then save the cleaned authentic export as `data/private/surveyol/week-001.csv`.

Do not let the public summary pipeline ingest closed-test rows. Known closed-test indicators include response numbers created before launch, test-recipient email addresses, UTM parameters from any test campaign, and any archived closed-test copy or title suffix.

## What The Script Produces

For each of the 15 live slider items:

- `n`
- mean
- median, retained for analysis but not foregrounded in the canonical public display
- min/max
- Q1/Q3
- interquartile range
- standard deviation
- disagreement score
- Doubt/Dogma endpoint-count metric: non-endpoint responses from 1-99, endpoint responses exactly 0 or 100, and their derived ratio
- key-tension flag and reasons
- simple histogram counts
- S23-style half-boundary bucket counts
- observed 10-bin display percentage series with light neighbor smoothing for public sparkline charts
- S23-style smoothed percentage series retained for reference/audit, capped at 100 if rendered

The script counts free-text suggestions but does not output raw suggestion text.

Canonical public reports should render the 15-item overview as `Item`, `Mean`, `IQR Range`, `Doubt/Dogma`, and `Distribution`. The distribution column should use observed 10-bin sparklines with light neighbor smoothing, a shared fixed 0-100 scale, a visible 100% marker at the top of the plot area, a plain white chart field, and no auxiliary grid lines. Keep median and low/middle/high band counts available in the JSON for analysis, but do not use them as primary result-display columns.

## Privacy Rules

- Raw SurveyOL exports stay in `data/private/`.
- Exact send-list crosswalks and joined identity-bearing analysis files stay in `data/private/`.
- Public JSON must not contain names, emails, participant IDs, direct contact fields, or raw free-text suggestions.
- Subgroup reporting should not be added until suppression thresholds are implemented and tested.
- Public files should contain aggregates only.

## Google Sheets Wiring

Near-term reports can use Google Sheets as the charting surface:

1. Import or paste `data/public/week-001-summary.json` or a derived CSV into a public-chart workbook.
2. Use the recovered S23 distribution-series logic for 10-bin sparkline panels, capping public display values at 100 and anchoring the shared chart scale at 100.
3. Screenshot only the public chart panels.
4. Publish screenshots alongside the written weekly report.

The next automation step should produce a Google Sheets-friendly CSV from the same public summary JSON.

## Not Yet Automated

- SurveyOL Email collector invitation sending.
- Direct Google Sheets writeback to `CTS 2026`.
- Google Sheets workbook population.
- Screenshot capture from Google Sheets.
- Weekly report HTML generation from summary JSON.
- Subgroup/correlation reporting.

`scripts/cts_ops.py` now provides a hardened local bridge for MailerLite suppression exports, SurveyOL API snapshots, private weekly send-list/crosswalk generation, and dry-run contact/group sync plans. SurveyOL export download and response snapshots are API-assisted when a SurveyOL API token is available, but SurveyOL Email collector batch sending remains guarded until a documented send endpoint is confirmed.

Operational JSON outputs that gate a risky action use `human_review_required`, `human_review_reason`, and `human_review_next_action` so automations can stop cleanly before imports, external list mutations, newsletter sends, or survey invitations.
