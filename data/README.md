# CTS Data Pipeline Directories

This directory separates private inputs from public report outputs.

## Directory Layout

- `data/private/`: ignored by git. Put raw SurveyOL exports, contact-level files, weekly send-list crosswalks, joined identity-bearing analysis files, raw participant suggestions, and internal QA notes here.
- `data/fixtures/`: committed synthetic files used to test the pipeline before real data exists.
- `data/public/`: privacy-safe generated summaries and public chart data. These files may be committed when they are intended for GitHub Pages/public reporting.

`data/public/legacy-200-items.json` is a public reference index generated from the original WordPress item pages. It is used for seed-theme research, not for mechanically copying old items into the weekly survey cycle.

## Weekly Input Convention

Put real weekly SurveyOL exports in:

```text
data/private/surveyol/week-001.csv
```

Put the exact SurveyOL Email collector send-list crosswalk for the same week in:

```text
data/private/contact-crosswalks/week-001.csv
```

If deep reports require respondent-level participant context, create the joined private analysis file only under `data/private/`, then produce public aggregate outputs from that private source. Never commit raw exports, contact crosswalks, joined files, names, email addresses, participant IDs, or unreviewed free-text suggestions.

Then generate a public summary:

```bash
python3 scripts/cts_report_pipeline.py summarize \
  --config reporting/week-001.config.json \
  --input data/private/surveyol/week-001.csv \
  --output data/public/week-001-summary.json
```

The generated summary should contain aggregate slider statistics, endpoint counts for Doubt/Dogma reporting, and public display distribution series only. It must not contain names, email addresses, participant IDs, or raw free-text suggestions.

Canonical public reports use the summary to display `Item`, `Mean`, `IQR Range`, `Doubt/Dogma`, and an observed 10-bin distribution sparkline with light neighbor smoothing. In `Doubt/Dogma`, the left non-endpoint/doubt count is yellow and the right endpoint/dogma count is red. Median and low/middle/high band counts may remain in the JSON for analysis and fallback rendering, but they are not primary report columns.

## Dry Run With Synthetic Data

```bash
python3 scripts/cts_report_pipeline.py summarize \
  --config reporting/week-001.config.json \
  --input data/fixtures/week-001-surveyol-synthetic.csv \
  --output /tmp/week-001-summary.synthetic.json
```
