# CTS Data Pipeline Plan

This document defines the first practical data pipeline for weekly CTS reporting. It is safe to create before real responses arrive because it uses synthetic test data and keeps raw/private data ignored by git.

## Pipeline Goal

Convert a private SurveyOL export into a privacy-safe public summary that can feed:

- Google Sheets reporting dashboards.
- Static screenshot/PDF report assets.
- GitHub Pages HTML/JavaScript charts.
- Future interactive item explorers.

## Current Pipeline Layers

1. `data/private/`: private, ignored inputs.
2. `reporting/week-001.config.json`: week-specific item and reporting configuration.
3. `scripts/cts_report_pipeline.py`: CSV-to-summary builder.
4. `schemas/public-weekly-summary.schema.json`: public summary shape.
5. `data/public/`: public, privacy-safe generated outputs.
6. `data/fixtures/`: synthetic data for dry runs.

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

Do not let the public summary pipeline ingest closed-test rows. Known closed-test indicators include the survey title suffix `(Closed Test)`, SurveyOL response numbers created before launch, and MailerLite UTM parameters from the closed-test campaign.

## What The Script Produces

For each of the 15 live slider items:

- `n`
- mean
- median
- min/max
- Q1/Q3
- interquartile range
- standard deviation
- disagreement score
- key-tension flag and reasons
- simple histogram counts
- S23-style half-boundary bucket counts
- S23-style smoothed percentage series for sparkline charts

The script counts free-text suggestions but does not output raw suggestion text.

## Privacy Rules

- Raw SurveyOL exports stay in `data/private/`.
- Public JSON must not contain names, emails, participant IDs, direct contact fields, or raw free-text suggestions.
- Subgroup reporting should not be added until suppression thresholds are implemented and tested.
- Public files should contain aggregates only.

## Google Sheets Wiring

Near-term reports can use Google Sheets as the charting surface:

1. Import or paste `data/public/week-001-summary.json` or a derived CSV into a public-chart workbook.
2. Use the recovered S23 distribution-series logic for 10-bin sparkline panels.
3. Screenshot only the public chart panels.
4. Publish screenshots alongside the written weekly report.

The next automation step should produce a Google Sheets-friendly CSV from the same public summary JSON.

## Not Yet Automated

- SurveyOL export download.
- MailerLite send scheduling.
- Google Sheets workbook population.
- Screenshot capture from Google Sheets.
- Weekly report HTML generation from summary JSON.
- Subgroup/correlation reporting.

Those should be added after the first real export reveals the exact SurveyOL column shape.
