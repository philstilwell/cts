# CTS Operations Hardening

This file documents the local operational tooling used by the weekly CTS automations. It is designed to reduce manual handling without making unsafe sends automatic.

## Safety Model

- Raw SurveyOL exports, participant registry CSV exports, contact crosswalks, API snapshots, and sync plans belong under `data/private/`.
- `data/private/` and `.env*` files are ignored by git.
- The ops CLI does not send SurveyOL invitations or MailerLite campaigns.
- Commands that can change MailerLite or SurveyOL data default to dry-run plans and require `--apply`.
- Generated audits and dry-run plans include `human_review_required`, `human_review_reason`, and `human_review_next_action` fields. Treat `human_review_required: true` as a hard stop before imports, list mutations, newsletter sends, or survey invitations.
- The public Reports page includes a rolling survey control board. Any automation that changes that board should rebuild the static site, commit the public status update, and push to the remote before reporting completion.
- SurveyOL Email collector sending still requires a guarded human/session step unless a documented send endpoint is added later.

## API Tokens

Create private API tokens and store them outside git:

```bash
cp .env.example .env
```

Then fill only the private `.env` file:

```bash
MAILERLITE_API_TOKEN=...
SURVEYOL_API_TOKEN=...
MAILERLITE_CTS_PARTICIPANTS_GROUP_ID=...
MAILERLITE_CTS_NEWSLETTER_GROUP_ID=...
```

MailerLite's current API lists subscribers with `filter[status]` values such as `active`, `unsubscribed`, `bounced`, and `junk`, and exposes group membership endpoints. SurveyOL's developer API exposes account, contact, survey, collector, and response objects through bearer-token authentication.

## Weekly Private Inputs

Export the canonical Google Sheet `CTS 2026` participant registry as a private CSV:

```text
data/private/registry/cts-2026.csv
```

The send-list builder looks for flexible header names, but the preferred columns are:

- `Name`
- `Primary Email Address`
- `Participant ID`
- `Email Key`
- `Do Not Email?`
- `Friendly Outreach List`

Rows with missing names are excluded automatically. This protects the rule that we do not upload email addresses with no accompanying names.

## Monday Hygiene Flow

Export MailerLite suppressions:

```bash
python3 scripts/cts_ops.py --env-file .env mailerlite-suppressions \
  --output data/private/suppressions/mailerlite-global.csv
```

Build a private weekly SurveyOL send list and exact crosswalk:

```bash
python3 scripts/cts_ops.py build-send-list \
  --week week-003 \
  --registry-csv data/private/registry/cts-2026.csv \
  --suppression-csv data/private/suppressions/mailerlite-global.csv \
  --require-friendly \
  --require-participant-id \
  --require-email-key
```

Outputs:

```text
data/private/send-lists/week-003-surveyol-contacts.csv
data/private/contact-crosswalks/week-003.csv
data/private/audits/week-003-send-list-audit.json
```

Review the audit before using the send list. The audit intentionally sets `human_review_required: true` so the accepted count, rejected count, suppression exclusions, duplicate handling, and missing-name exclusions are checked before contacts are imported or invitations are sent.

## MailerLite Dry-Run Sync

Create a dry-run group alignment plan before applying anything. The snapshot/sync reads MailerLite group members across active, unsubscribed, unconfirmed, bounced, and junk statuses so suppressed records are not hidden by MailerLite's default active-only group view:

```bash
python3 scripts/cts_ops.py --env-file .env mailerlite-sync-group \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --group-id "$MAILERLITE_CTS_PARTICIPANTS_GROUP_ID" \
  --suppression-csv data/private/suppressions/mailerlite-global.csv \
  --plan-output data/private/audits/week-003-mailerlite-sync-plan.json
```

Only after reviewing the plan:

```bash
python3 scripts/cts_ops.py --env-file .env mailerlite-sync-group \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --group-id "$MAILERLITE_CTS_PARTICIPANTS_GROUP_ID" \
  --suppression-csv data/private/suppressions/mailerlite-global.csv \
  --plan-output data/private/audits/week-003-mailerlite-sync-plan-applied.json \
  --apply
```

Do not use `--remove-extra` unless you intentionally want to remove active MailerLite group members who are not in the current weekly send list.

Dry-run sync plans set `human_review_required: true`. Applied plans set it to `false` because the reviewed action has already been executed.

## SurveyOL API Snapshots

Verify the token:

```bash
python3 scripts/cts_ops.py --env-file .env surveyol-account
```

Snapshot the survey list:

```bash
python3 scripts/cts_ops.py --env-file .env surveyol-surveys \
  --output data/private/surveyol-api/surveys.json
```

Snapshot a specific survey's metadata, collectors, and responses:

```bash
python3 scripts/cts_ops.py --env-file .env surveyol-snapshot \
  --week week-003 \
  --survey-id SURVEYOL_SURVEY_GUID \
  --out-dir data/private/surveyol-api
```

The snapshot also stores survey pages and page-level questions so a preflight can compare the live SurveyOL structure against the weekly template.

Sync missing SurveyOL contacts from a private send list with a dry-run first:

```bash
python3 scripts/cts_ops.py --env-file .env surveyol-sync-contacts \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --plan-output data/private/audits/week-003-surveyol-contact-plan.json
```

Apply only after review:

```bash
python3 scripts/cts_ops.py --env-file .env surveyol-sync-contacts \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --plan-output data/private/audits/week-003-surveyol-contact-plan-applied.json \
  --apply
```

## What Remains Guarded

The scripts harden list preparation, suppression reconciliation, API snapshots, contact sync, and exact crosswalk creation. They do not yet automate:

- SurveyOL survey creation from copy/paste blocks.
- SurveyOL Email collector batch sending.
- MailerLite campaign creation/sending.
- Google Sheets direct writeback to `CTS 2026`.

Those should remain guarded until the exact APIs and field mappings are proven with one or two production cycles.
