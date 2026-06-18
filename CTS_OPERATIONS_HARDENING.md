# CTS Operations Hardening

This file documents the local operational tooling used by the weekly CTS automations. It is designed to reduce manual handling without making unsafe sends automatic.

## Safety Model

- Raw SurveyOL exports, participant registry CSV exports, contact crosswalks, API snapshots, and sync plans belong under `data/private/`.
- `data/private/` and `.env*` files are ignored by git.
- The ops CLI does not send SurveyOL invitations.
- Commands that can change SurveyOL data default to dry-run plans and require `--apply`.
- Generated audits and dry-run plans include `human_review_required`, `human_review_reason`, and `human_review_next_action` fields. Treat `human_review_required: true` as a hard stop before imports, list mutations, newsletter sends, or survey invitations.
- The public Reports page includes a rolling survey control board. Any automation that changes that board should rebuild the static site, commit the public status update, and push to the remote before reporting completion.
- SurveyOL Email collector sending still requires a guarded human/session step unless a documented send endpoint is added later.
- Weekly automation status boards belong under `data/private/automation-status/`. They show run timestamps, current status, missing/stale evidence, and process coverage/redundancy without exposing private participant data.

## Automation Status And Coverage

The machine-readable coverage manifest is `automation/weekly-process.json`. It defines every required automation or guarded check, the artifacts that prove it ran, the scopes where it applies, and the redundancy groups that protect risky steps.

Generate a private status board for a week and scope:

```bash
python3 scripts/cts_automation_status.py report \
  --week week-003 \
  --scope launch \
  --output data/private/automation-status/week-003-launch-status.md
```

The report includes:

- required run evidence counts and timestamps;
- per-item statuses: `passed`, `review_required`, `blocked`, `failed`, `missing`, `stale`, `planned`, `running`, and `not_due`;
- direct evidence links to private artifacts when they exist;
- next action text from `human_review_required` JSON fields when a dry-run plan is waiting;
- a coverage and redundancy table for suppression handling, duplicate protection, participant identity joins, SurveyOL state, privacy boundaries, public status, send accountability, and report quality.

Record guarded or manual confirmations in the private ledger:

```bash
python3 scripts/cts_automation_status.py record \
  --week week-003 \
  --id surveyol.closed-test-quarantine \
  --status passed \
  --note "Closed-test response count checked; production send gate clear."
```

Use `not_due` only when a process step is truly outside the current calendar gate, such as final close before the three-week response window ends. Use `review_required` when an automation has run but a human decision is still needed. Use `blocked` when the next risky action must stop.

The recurring invitation-batch check runs Wednesday through Saturday at 2:30 PM Eastern while a weekly survey still has eligible participants who have not been invited. It should regenerate the invitation-scope status board before acting, stop on any missing/stale/blocked/failed evidence, and treat `review_required` suppression reconciliation as a hard gate before another batch.

## API Tokens

Create private API tokens and store them outside git:

```bash
mkdir -p .secrets
cp .env.example .secrets/cts.env
```

Then fill only the private CTS env file:

```bash
SURVEYOL_API_TOKEN=...
```

`scripts/cts_ops.py` now auto-discovers CTS env files in these locations before every command:

- `.env`
- `.env.local`
- `.secrets/cts.env`
- `.secrets/cts-ops.env`
- `~/.codex/cts.env`

Use one standard location and keep it stable. The recommended project-local path is `.secrets/cts.env`.

Before a weekly hygiene run, invitation batch, or suppression reconciliation, run the fast environment preflight:

```bash
python3 scripts/cts_ops.py env-doctor --verify-api
```

Treat any nonzero exit or `human_review_required: true` output as a hard stop. This catches missing tokens or broken API access before the automation reaches the send gate.

SurveyOL's developer API exposes account, contact, survey, collector, and response objects through bearer-token authentication.

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
- `2026 Outreach Status`

Rows with missing names are excluded automatically. This protects the rule that we do not upload email addresses with no accompanying names.

The send-list builder also treats `2026 Outreach Status` values containing terms such as `hold`, `paused`, `suppressed`, `opted out`, `unsubscribed`, `bounced`, or `complaint` as exclusions. Use that field for temporary operational holds that should block future sends without marking the participant as a permanent `Do Not Email?` record.

## Monday Hygiene Flow

Start with the environment/API preflight:

```bash
python3 scripts/cts_ops.py env-doctor --verify-api
```

Then save the current SurveyOL no-send suppression source to:

```text
data/private/suppressions/surveyol-no-send.csv
```

This file may come from a direct SurveyOL no-send or unsubscribed export, or from a normalized manual CSV built from the live SurveyOL send page. The send-list builder reads the email column generically, so the file only needs a usable email column.

Build a private weekly SurveyOL send list and exact crosswalk:

```bash
python3 scripts/cts_ops.py build-send-list \
  --week week-003 \
  --registry-csv data/private/registry/cts-2026.csv \
  --suppression-csv data/private/suppressions/surveyol-no-send.csv \
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

Before importing any generated or manually edited contact CSV, run the duplicate-email audit and treat any duplicate as a hard stop:

```bash
python3 scripts/cts_ops.py audit-email-duplicates \
  --csv data/private/send-lists/week-003-surveyol-contacts.csv \
  --output data/private/audits/week-003-send-list-duplicate-audit.json \
  --fail-on-duplicates
```

The audit normalizes email addresses by trimming whitespace and lowercasing. It reports every CSV row sharing the same normalized email so the list can be corrected before SurveyOL sees it.

## SurveyOL No-Send Source

CTS no longer uses MailerLite as an operational suppression source. The only external suppression source for weekly survey invitations is SurveyOL's no-send or unsubscribed list, which must be reflected back into `CTS 2026` before future sends.

If SurveyOL's API does not expose the needed no-send rows directly, save a private normalized CSV under `data/private/suppressions/surveyol-no-send.csv` from the live SurveyOL send page or export UI and treat that file as the current suppression authority.

## SurveyOL API Snapshots

Verify the token:

```bash
python3 scripts/cts_ops.py surveyol-account
```

Snapshot the survey list:

```bash
python3 scripts/cts_ops.py surveyol-surveys \
  --output data/private/surveyol-api/surveys.json
```

Snapshot a specific survey's metadata, collectors, and responses:

```bash
python3 scripts/cts_ops.py surveyol-snapshot \
  --week week-003 \
  --survey-id SURVEYOL_SURVEY_GUID \
  --out-dir data/private/surveyol-api
```

The snapshot also stores survey pages and page-level questions so a preflight can compare the live SurveyOL structure against the weekly template.

Export the live SurveyOL contact table and audit it for duplicate email records before importing recipients or sending another invitation batch:

```bash
python3 scripts/cts_ops.py surveyol-contacts \
  --output data/private/surveyol-api/surveyol-contacts.csv \
  --audit-output data/private/audits/surveyol-contact-duplicate-audit.json
```

If `duplicate_email_count` is greater than `0`, stop all SurveyOL invitation sends until the extra SurveyOL contact records are merged or deleted and the audit is clean.

Sync missing SurveyOL contacts from a private send list with a dry-run first:

```bash
python3 scripts/cts_ops.py surveyol-sync-contacts \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --plan-output data/private/audits/week-003-surveyol-contact-plan.json
```

The sync plan now checks both the incoming send list and the existing SurveyOL contacts for duplicate normalized emails. If duplicates are present, `duplicate_blockers` is populated, `human_review_required` remains `true`, and `--apply` is blocked.

Apply only after review:

```bash
python3 scripts/cts_ops.py surveyol-sync-contacts \
  --send-list data/private/send-lists/week-003-surveyol-contacts.csv \
  --plan-output data/private/audits/week-003-surveyol-contact-plan-applied.json \
  --apply
```

## What Remains Guarded

The scripts harden list preparation, suppression reconciliation, API snapshots, contact sync, and exact crosswalk creation. They do not yet automate:

- SurveyOL survey creation from copy/paste blocks.
- SurveyOL Email collector batch sending.
- Google Sheets direct writeback to `CTS 2026`.

Those should remain guarded until the exact APIs and field mappings are proven with one or two production cycles.
