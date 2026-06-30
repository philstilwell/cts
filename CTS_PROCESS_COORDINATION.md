# CTS Process Coordination

This is the coordination contract for CTS recurring automations. Cron prompts, runbooks, and manual runs should agree with this file before taking external action.

## Operating Model

The weekly CTS cycle has one canonical participant registry, one survey delivery system, one public status trail, and private evidence for every risky action.

- `CTS 2026` is the canonical participant registry and outreach-status source.
- SurveyOL is the active weekly survey and invitation system.
- `data/private/` holds raw exports, contact crosswalks, private audits, operational notes, and automation ledgers.
- `data/public/` plus generated site pages are the only public data surfaces.
- `data/public/automation-daily-log.json` and `automation-daily-log/index.html` are the public-safe audit trail for every cron run, including no-op and blocked runs.
- `scripts/publish_static_site.py` is the required publishing path for public site changes. It builds the site, syncs only approved public artifacts to `gh-pages`, pushes the Pages branch, and verifies the live URL.

Historical newsletter or external email-tool evidence may be used as background only when it has already been reflected into `CTS 2026`. It is not an active SurveyOL invitation gate unless CTS explicitly reintroduces that system in this file and in `automation/weekly-process.json`.

## Weekly Flow

1. Monday draft preflight checks the next topic, item set, report link, placeholder plan, final-close-date plan, and public/private boundaries.
2. Monday list hygiene refreshes SurveyOL suppressions, SurveyOL contact duplicate evidence, the private send list, private crosswalk, and dry-run contact sync plan.
3. Tuesday morning report work publishes or refreshes preliminary reports, reviews ballot/suggestion inputs for the next survey, and keeps public close dates aligned.
4. Tuesday close check closes and finalizes only surveys that have reached their posted final close date.
5. Tuesday evening launch publishes the placeholder page, records owner approval, verifies SurveyOL collector settings, sends the first guarded SurveyOL batch, records the result, and pushes the public log.
6. Wednesday through Saturday invitation checks continue guarded SurveyOL batches of up to 100 per day until every eligible participant has been invited or a hard stop appears.
7. Starting 12 days after the first production invitation date, reminder checks may open the manual reminder workflow. Reminders are not automatic.

## Hard Gates

Stop before importing contacts, sending SurveyOL invitations, sending reminders, publishing reports, or scheduling newsletters when any relevant artifact reports `human_review_required: true`, `blocked`, `failed`, unresolved `review_required`, duplicate emails, missing identity mapping, or stale required evidence.

Before any invitation batch:

- Regenerate the relevant private status board with `scripts/cts_automation_status.py`.
- Confirm the public placeholder exists, is linked from the reports index, and shows the exact final close date as first production invitation date plus 20 days.
- Confirm `public.final-close-date-posted` is recorded in the private ledger.
- Confirm SurveyOL Email collector status is `Open`, `Anonymous Responses` is `Off`, and automatic `Reminder Follow-up` is `Off`.
- Confirm the SurveyOL Email invitation editor and sender verification are send-enabled. If sender verification does not produce a confirmation-code path or token, the editor shows a visible disabled-send banner, or the save response returns `successful:false` without increasing the invitation count, record a send blocker and do not retry the same batch until SurveyOL's send-enabled state is restored.
- Confirm `surveyol.reminder-auto-disabled` is recorded. Do not require the older automatic-reminder configuration ledger gate for recurring invitation batches.
- Reconcile SurveyOL opt-outs, bounces, delivery problems, no-send rows, and `CTS 2026` do-not-email records into the active suppression controls.
- Audit the send-list CSV, SurveyOL contacts, and, after invitations already exist, the live SurveyOL invitation rows.
- Compare the exact next batch CSV with the live SurveyOL invitation table. No address already present in SurveyOL invitations may appear in the next batch.
- Record the batch result under `send.invitation-batch-ledger` and the suppression result under `post-send.suppression-reconcile`.
- After any send, re-extract or inspect the live SurveyOL invitation table before the next risky action. If a participant reports multiple copies, record a blocker and stop invitations and reminders until the live duplicate-row audit is clean.

## Reminder Policy

SurveyOL automatic reminder follow-up is not the weekly default. Keep it off.

Manual reminders are allowed only after the first invitation date plus 12 days and only after:

- `surveyol-reminder-due-check` says the reminder window is due.
- The live SurveyOL invitation table has been exported or extracted.
- `audit-surveyol-invitations --fail-on-duplicates` is clean.
- `build-surveyol-reminder-list` produces a candidate report without unresolved review flags.
- The private ledger records the reminder audit or a `not_due` status when no reminder action is due.

Use SurveyOL's manual reminder flow for audited reminder candidates. Do not use `+ New Invitations` as a reminder mechanism.

## Public Log And Publishing

Every cron run must append or update a public-safe entry in `data/public/automation-daily-log.json`, commit relevant source/public changes to `main`, then publish through `scripts/publish_static_site.py` before reporting completion. Do not treat a `main` push alone as a completed public update, because GitHub Pages serves `gh-pages`.

Use a command shaped like:

```bash
python3 scripts/publish_static_site.py \
  --message "Publish refreshed CTS automation log" \
  --expect-text "public-safe text from the new log entry"
```

Public log entries may include counts, dates, statuses, and public URLs. They must not include respondent links, names, email addresses, participant IDs, private raw exports, contact crosswalks, or raw free-text suggestions.

## Cron Responsibilities

- `cts-weekly-survey-draft-preflight`: plan readiness only; no sends.
- `cts-weekly-list-hygiene`: refresh active SurveyOL and `CTS 2026` suppression/list evidence; no sends.
- `cts-tuesday-report-and-newsletter`: publish or refresh reports and prepare newsletter/update copy only when gates are clean.
- `cts-three-week-survey-close`: close and finalize only surveys whose posted close date has arrived.
- `cts-tuesday-survey-launch`: perform first-batch launch gates and send up to 100 SurveyOL invitations only when clear.
- `cts-invitation-batch-check`: continue guarded SurveyOL invitation batches while eligible participants remain and daily limits allow.

When a cron finds a discrepancy between its prompt and this file, this file and `automation/weekly-process.json` control; update the stale prompt before continuing.
