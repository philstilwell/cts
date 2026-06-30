# CTS Weekly Survey Runbook

Use this runbook for each weekly CTS cycle.

For the detailed participant-nominated ballot scoring and tie-breaking protocol, use `PARTICIPANT_NOMINATED_BALLOT_PROTOCOL.md`.

For topic/item tension preflights, use `TOPIC_BANK_TENSION_REVIEW.md` and `NEXT_3_TOPIC_ITEM_REVIEW.md`. For older CTS seed themes, use `LEGACY_200_ITEM_INDEX.md` and `data/public/legacy-200-items.json`. For the Week 1 seed audit, use `WEEK_1_ITEM_AUDIT.md`.

## Weekly Cadence

- Tuesday morning: publish the first weekly report for any survey launched one week earlier, and refresh every still-open survey report that has already received its first preliminary report. Preliminary reports should clearly state the exact final close date and that the survey remains open until that date.
- Tuesday evening: create the placeholder public report page for the new survey, launch the new weekly SurveyOL survey, and begin sending invitations through the SurveyOL Email collector. Send up to 100 participant invitations per day until all eligible potential participants have been sent that week's invitation.
- Wednesday through Saturday at 11:30 AM Eastern, if needed: continue SurveyOL Email collector invitation batches of up to 100 per day until the full eligible participant list has been invited.
- Starting 12 days after the first production invitation date, run the manual reminder due check. When it reports due, complete the audited manual reminder workflow instead of enabling automated reminder follow-up.
- Every week: before any survey-invitation send, remove or suppress from SurveyOL and `CTS 2026` any address that appears on SurveyOL's no-send/unsubscribed list or is otherwise marked do-not-email in the registry.
- Historical external email-tool unsubscribe evidence should be reflected in `CTS 2026` when known, but the recurring SurveyOL invitation-scope blocker is the current SurveyOL plus `CTS 2026` suppression state unless CTS explicitly reintroduces another active workflow dependency in `CTS_PROCESS_COORDINATION.md` and `automation/weekly-process.json`.
- Every weekly survey remains open for 3 weeks from its first invitation send. Calculate the final close date as the first production invitation send date plus 20 days, normally a Tuesday for Tuesday evening launches, and post that exact date on the weekly survey's public page before invitations go out. Close the SurveyOL collector after that date, export the final raw results privately, and regenerate the public report as final.
- Every weekly SurveyOL Email collector should launch with automatic `Reminder Follow-up` off. Send reminders only through a later manual reminder pass after the live invitation table has been exported or extracted, duplicate-audited, and converted into a reminder candidate list.
- Every new weekly SurveyOL survey should include, near the top, a brief encapsulation of the newest weekly report plus a link to the full report.
- Every new weekly SurveyOL survey must be reviewed and approved by the CTS owner before the first production invitation batch. This review replaces any standing internal test-send requirement; perform a test send only when the owner explicitly asks for one or when a specific technical uncertainty warrants it.
- The Reports page includes a rolling survey control board under the weekly report grid. Any automation that changes a survey's public status on that board should commit the changed public/source files to `main`, publish through `scripts/publish_static_site.py`, and verify the live page before reporting the board update as complete.

## Active Reminders

- Monday afternoon: run the list-hygiene audit before the next survey sends.
- Tuesday morning: publish first preliminary reports, refresh still-open preliminary reports, create the report encapsulation, and update the site.
- Tuesday morning after the report cycle: check whether any survey has reached its posted final close date, then close and finalize reports as needed.
- Tuesday evening: create the placeholder public report page, launch the new SurveyOL Email collector survey, and send the first invitation batch.
- Wednesday through Saturday at 11:30 AM Eastern: check whether eligible participants remain uninvited, regenerate the invitation-scope automation status board, and send the next guarded invitation batch only if the recurring hygiene checks and any still-relevant launch-time send gates are clear. At minimum, the automatic-reminder-off gate must stay recorded and clear on the invitation board until invitations are finished.
- Daily after a survey has reached first invitation date plus 12 days, until the reminder pass is completed or explicitly skipped: run `surveyol-reminder-due-check`; if it opens a review gate, run the audited manual reminder pass.

These reminders can execute only when the relevant SurveyOL, Google Sheets, and GitHub access is available. If an authentication step, confirmation code, or safety check blocks a send, the reminder should stop and report the blocker rather than improvising.

Every CTS cron automation, even when it makes no public change or hits a blocker, must write a public-safe record to `data/public/automation-daily-log.json`, commit relevant source/public changes to `main`, and publish through `scripts/publish_static_site.py` before the run is considered complete. GitHub Pages serves `gh-pages`, so a `main` push alone does not refresh the live site.

## Automation Status Board

Each weekly cycle should have a private timestamped automation status board under `data/private/automation-status/`. Generate it before any risky action and again after the action is completed or blocked:

```bash
python3 scripts/cts_automation_status.py report \
  --week week-003 \
  --scope launch \
  --output data/private/automation-status/week-003-launch-status.md
```

Use these scopes:

- `launch`: required evidence before the first production SurveyOL invitation batch.
- `invitation`: recurring evidence around Wednesday-Saturday invitation batches, including any launch-time send gate that remains relevant after Tuesday, such as automatic-reminder-off verification and manual reminder audits.
- `report`: Tuesday report, newsletter, and public status update evidence.
- `close`: 20-day survey close and final-report evidence.
- `full-cycle`: complete process coverage and redundancy audit.

The status board answers three operational questions:

1. Did every required automation or guarded check for this scope run, and when?
2. Is each item `passed`, `review_required`, `blocked`, `failed`, `missing`, `stale`, `planned`, `running`, or explicitly `not_due`?
3. Does each major process area have coverage and redundancy, such as SurveyOL no-send plus registry suppression checks, send-list plus live-contact duplicate audits, dry-run plans plus human-review gates, and private raw exports plus public aggregate summaries?

Some required steps are intentionally not fully automated, especially SurveyOL survey creation, Email collector sends, public URL verification, and final approval of dry-run plans. Record those guarded steps in the private ledger instead of relying on memory:

```bash
python3 scripts/cts_automation_status.py record \
  --week week-003 \
  --id public.placeholder-page \
  --status passed \
  --note "Placeholder page and reports index verified on GitHub Pages; commit abc1234."
```

List valid IDs with:

```bash
python3 scripts/cts_automation_status.py list --scope launch
```

Do not put live SurveyOL respondent links, names, emails, participant IDs, or private raw-data details in ledger notes. Keep notes public-safe even though the ledger is stored under ignored private data.

## Report Encapsulation

Each weekly report needs a short encapsulation suitable for reuse in at least one place:

1. The top of the next weekly SurveyOL survey.

The encapsulation should be short enough to scan quickly and should include:

- the survey topic;
- response count and whether the report is preliminary or final;
- 2-4 major findings or tensions;
- a link to the full public report;
- a privacy-safe note that raw respondent identities and raw free-text suggestions are not published.

## Build The Survey

1. Select one CTS-administered topic from `CTS 2026 Weekly Topic Bank.md`.
2. Review the selected topic for clarity and tension potential before fielding it.
3. Add a brief previous-results note and a link to the public weekly reports page. In SurveyOL, standardize the link label as `CTS REPORTS` and make it an actual rich-text hyperlink to `https://christianthoughtsurvey.com/weekly-survey-reports/`, not a pasted raw URL. Style the linked label as bold, underlined, colored to match the header accent currently used for this link (`#553e15` unless the banner palette changes), and enlarged with `X↑` twice. Add week-specific operational notes, such as a one-off apology for duplicate email reminders, only in the affected weekly survey draft; do not carry those notes forward as standing template copy.
4. Add the narrow Featured Topic header image immediately before the current-topic introduction line. Prefix that line with `◉ ` every week, for example: `◉ Main topic for the first 12 survey items: Pornography and the Church.` In SurveyOL, style the topic-introduction block so the main-topic line is bold and enlarged with `X↑` twice; highlight only the topic name with the header gold background (`#e0a550`) and dark header text (`#553e15`); keep the response-format line below it bold in black.
5. Add the topic's 12 survey items as required 0-100 credence sliders.
6. Add the narrow Independent Items header image, then add 3 participant-vote-determined live survey items from the previous week's ballot. These items should be semantically clear, orthogonal to the weekly CTS-administered topic, not copied from the current topic bank, and likely to generate meaningful tension or spread. For Week 1 only, use the seeded items in `WEEK_1_SURVEY_TEMPLATE.md`.
7. Add the participant-nominated item ballot. Review participant suggestions with AI assistance, polish them for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance, and reduce them to 7 ballot items. If fewer than 7 suitable participant nominations are available, add AI-created seed items to complete the ballot. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas, but ballot items should be rewritten for current clarity and should not be copied mechanically.
8. Save a brief item-audit note for the 3 independent live items and 7 ballot items before finalizing SurveyOL.
9. Add a text box for future participant-nominated survey items.
10. Add a preview of upcoming topics. The topics for the next three weeks should be featured to allow for mental preparation.
11. Confirm the full-time ministry participation note appears in the website/contact materials and email copy. Do not add a separate eligibility confirmation item inside the weekly SurveyOL survey unless CTS intentionally reintroduces one.
12. Create the placeholder public report page before the first SurveyOL invitation batch. The placeholder should use the stable report URL, state that the survey is open, name the topic, identify the expected first-report date, and show the exact final close date calculated as the planned first production invitation date plus 20 days. If the actual first send slips, update the page, reports index, and week config to the corrected close date before reporting the launch complete. Week 1 uses `https://christianthoughtsurvey.com/weekly-survey-reports/week-001-divorce-and-remarriage/`.
13. Before any full participant send, remove all closed-test wording from the SurveyOL title, intro text, previous-results placeholder, and end-of-survey page.
14. Present the finished SurveyOL draft or equivalent preview materials for CTS owner review, including the newest-report link, 12 topic items, 3 independent items, 7-item ballot, suggestion box, upcoming-topic preview, invitation copy, collector settings, and final-close-date plan. Record `surveyol.prelaunch-human-review` only after the owner approves the first production batch. Do not require an internal test send unless the owner asks for one.

## Send The Survey

1. Before sending the Tuesday evening survey invitation, confirm the placeholder public report page exists, is linked from the reports index, and has been pushed to GitHub Pages. For closed tests, use only internal/test contacts.
2. The SurveyOL Email collector must be `Open` with `Anonymous Responses` set to `Off` so exports can include email identity for private matching. Close or do not distribute Web Link collectors unless CTS intentionally wants an unmapped public response channel.
3. Confirm the CTS owner has reviewed the finished weekly survey and explicitly approved the first production invitation batch. Record `surveyol.prelaunch-human-review` in the private automation ledger before any production invitations are sent. This is a hard gate; an internal test send is not a standing requirement.
4. Confirm the Email collector `Reminder Follow-up` is off before the first production invitation batch, and record `surveyol.reminder-auto-disabled` in the private automation ledger. That ledger record remains a hard gate for later Wednesday-Saturday batches as well, so the invitation-scope board should surface it until all invitations are sent. Do not enable automated reminders as the standing weekly default.
5. Build the SurveyOL recipient list from the canonical `CTS 2026` participant registry. Include only eligible records with `Name`, `Primary Email Address`, `Participant ID`, and `Email Key`, and exclude records marked `Do Not Email? = Yes`, unsubscribed, opted out, bounced, or otherwise suppressed.
6. Audit the exact CSV that will be imported or used for recipient targeting with `scripts/cts_ops.py audit-email-duplicates --fail-on-duplicates`. Any duplicate normalized email address is a hard stop until corrected.
7. Export or inspect the live SurveyOL contact table before each invitation batch. If any SurveyOL contact email appears more than once, stop sending until the extra contact records are merged or deleted.
8. After any SurveyOL invitations exist, export or extract the live Email collector invitation table and audit it with `scripts/cts_ops.py audit-surveyol-invitations --fail-on-duplicates`. Any duplicate normalized invitation email is a hard stop before sending more invitations or sending reminders.
9. Before sending the exact next batch, compare that batch CSV to the fresh live invitation extract:

```bash
python3 scripts/cts_ops.py audit-batch-against-invitations \
  --batch-csv data/private/send-lists/week-XXX-batch-NNN.csv \
  --invitation-json data/private/surveyol-api/week-XXX-invitations-extract.json \
  --output data/private/audits/week-XXX-next-batch-live-audit.json \
  --fail-on-blockers
```

10. Stop if the batch-vs-live audit finds any planned recipient already present in SurveyOL invitations, any duplicate inside the batch, or any duplicate already in SurveyOL. Rebuild from a fresh extract and resolve SurveyOL rows before sending.
11. Include stable private join fields in SurveyOL contact fields when SurveyOL supports them: `Participant ID` and `Email Key`. If SurveyOL does not export contact custom fields, save the exact send-list crosswalk privately for that week.
12. Send up to 100 invitations per day until all eligible potential participants have been invited for that week's survey. Record each batch count, cumulative sent count, total eligible invitation-list count, and remaining eligible-invitation count; stop when the remaining count reaches zero.
13. For a small tail batch, prefer the simplest stable SurveyOL send path only after the batch-vs-live audit passes. If the live contact-table checkbox UI is fragile, row selection opens edit dialogs, or the remaining list is already known from the guarded send audit, use the `Recipient Email(s)` field directly with the verified remaining addresses instead of forcing another checkbox-based selection pass. Record that direct-entry fallback was used.
14. After each send, re-extract or inspect SurveyOL invitations before the next risky action. If anyone reports multiple copies, record a private blocker and do not send more invitations or reminders until the live duplicate-row audit is clean.
15. After the first production invitation batch is actually sent, verify that the public page's final close date equals that send date plus 20 days. If the actual send date differs from the planned launch date, correct the public page, reports index, reporting config, and automation ledger before the next public status update.
16. After the first production invitation batch is actually sent, record or generate the day-12 manual reminder due check:

```bash
python3 scripts/cts_ops.py surveyol-reminder-due-check \
  --week week-XXX \
  --first-invitation-date YYYY-MM-DD \
  --output data/private/audits/week-XXX-manual-reminder-due.json
```

17. After each send, reconcile SurveyOL `Opted Out`, bounced, delivery-problem, and no-send records back into `CTS 2026` and SurveyOL before the next recipient import. A SurveyOL no-send record or a registry `Do Not Email? = Yes` flag is a global CTS email suppression for future survey invitations.
    Do not let older external email-tool notes reopen the invitation gate by accident; record invitation suppression reconciliation against the active SurveyOL plus `CTS 2026` controls unless another dependency has been explicitly restored in `CTS_PROCESS_COORDINATION.md`.
18. If the suppression CSV was manually reconfirmed or regenerated without changing membership, still refresh its evidence timestamp before rerunning the invitation board so the board reflects the latest review rather than an old embedded `collected_at` date.
16. After each material send or send blocker, update `data/public/automation-daily-log.json` with a public-safe summary, commit relevant source/public changes to `main`, then run `scripts/publish_static_site.py` with an `--expect-text` from the new log entry so the live public log is verified against the private ledger.
17. Keep live SurveyOL respondent links and design URLs in SurveyOL or private operational notes only. Do not commit them to the public repository.

## Send Reminders

Reminder emails are a separate manual operation due 12 days after the first production invitation date. Do not rely on SurveyOL automated reminder follow-up as the weekly default.

1. Keep the Email collector `Reminder Follow-up` off until the reminder pass is ready.
2. Run the due check. A due result opens the manual reminder gate:

```bash
python3 scripts/cts_ops.py surveyol-reminder-due-check \
  --week week-XXX \
  --first-invitation-date YYYY-MM-DD \
  --output data/private/audits/week-XXX-manual-reminder-due.json
```

3. Export or extract the live SurveyOL Email collector invitation table, including invitation rows and their status labels.
4. Audit the invitation rows before any reminder send:

```bash
python3 scripts/cts_ops.py audit-surveyol-invitations \
  --input-json data/private/surveyol-api/week-XXX-invitations-extract.json \
  --output data/private/audits/week-XXX-invitation-duplicate-audit.json \
  --fail-on-duplicates
```

5. Build the manual reminder candidate list:

```bash
python3 scripts/cts_ops.py build-surveyol-reminder-list \
  --input-json data/private/surveyol-api/week-XXX-invitations-extract.json \
  --output-csv data/private/send-lists/week-XXX-reminder-candidates.csv \
  --report-output data/private/audits/week-XXX-reminder-candidates-report.json
```

6. Stop immediately if either invitation-row command reports `human_review_required: true`, exits nonzero, or shows any duplicate normalized invitation email. Resolve the extra invitation row in SurveyOL, re-extract, and rerun both checks before sending reminders.
7. Send reminders only from SurveyOL's `Reminder Follow-up` -> `Manually Send` flow. Select only rows that appear in the audited reminder candidate CSV. Do not use `+ NEW INVITATIONS` as a reminder mechanism.
8. The reminder candidate CSV intentionally excludes invitation rows that are missing `Sent`, already have `Clicked`, `Clicked-through`, `Started`, `Complete`, `Completed`, `Opted Out`, `Bounced`, `Reminded`, or `Thanked` status labels, or share an email address with another invitation row.
9. After sending reminders, re-export or re-extract the invitation table and verify that each intended reminder recipient has exactly one `Reminded` flag. Record `surveyol.manual-reminder-audit` and the reminder count in the private automation ledger.

## Participant Profile Intake

The public Contact & Weekly Survey Participation form is only the eligibility and interest front door. When a potential participant appears to be currently or previously engaged in full-time ministry, send the private `CTS 2026 Participant Profile Survey` documented in `PARTICIPANT_PROFILE_SURVEY.md`.

Do not link the participant-profile survey publicly. Add or confirm a person in the `CTS 2026` participant registry only after eligibility review and profile completion, then include them in SurveyOL weekly recipient imports only when they meet the outreach filter. Store raw profile exports under `data/private/participant-profiles/`, and never commit names, email addresses, or individual profile rows.

## Closed-Test Response Quarantine

Closed-test submissions made through the real SurveyOL respondent link count as real SurveyOL responses. They are not automatically quarantined from later authentic survey responses.

Before any full participant send, do one of the following:

1. Preferred: copy or reset the tested SurveyOL survey so the public launch starts with zero responses.
2. Acceptable: delete all closed-test responses from SurveyOL before the public launch, after confirming no authentic responses have arrived.
3. Fallback: export closed-test responses separately, record their SurveyOL response numbers, start times, and UTM parameters, and exclude them from the private raw export before generating public reports.

For Week 1, closed-test responses `#1` and `#2` were deleted from SurveyOL on June 2, 2026 before public launch. SurveyOL was rechecked on June 3, 2026 after title/text cleanup and still showed no responses so far. Recheck the SurveyOL summary again immediately before each production send.

For Week 1, the anonymous Web Link collector was closed on June 10, 2026 and the Email collector was left open with `Anonymous Responses` set to `Off` so private exports can be mapped back to the `CTS 2026` registry.

## Export And Report

1. Publish a preliminary first report on Tuesday morning one week after the first invitation send.
2. Refresh every still-open preliminary report each Tuesday morning until its posted final close date.
3. Optionally refresh a preliminary report outside the Tuesday cycle when responses have materially changed, such as about 10 or more new complete responses or a clear shift in a published takeaway.
4. Each preliminary refresh should show the current response count, last-updated date, exact final close date, and a note that the report will continue to be refreshed until that close date.
5. Export SurveyOL responses after the posted final close date.
6. Save the private raw export in `data/private/surveyol/week-###.csv`. Do not commit raw exports.
7. Normalize email addresses and join the private export to the `CTS 2026` participant registry before subgroup or deep analysis. Flag unmatched rows and resolve them before publishing a report.
8. Save any joined identity-bearing analysis file under `data/private/`. Do not commit joined files, contact crosswalks, names, email addresses, participant IDs, or raw free-text suggestions.
9. Generate the public summary JSON with `scripts/cts_report_pipeline.py` and the matching `reporting/week-###.config.json`.
10. Review the generated summary's `quality` section for missing columns, non-numeric values, out-of-range values, unexpectedly low counts, and unexpected unmatched-response counts.
11. Summarize all 15 live slider items with the canonical results display: `Item`, `Mean`, `IQR Range`, `Doubt/Dogma` as non-endpoint:endpoint counts, and an observed 10-bin distribution sparkline with light neighbor smoothing and a visible 100% marker. In `Doubt/Dogma`, color the left non-endpoint/doubt count green and the right endpoint/dogma count red. Do not use `Median` or `Low / Mid / High` as primary table columns.
12. Use the canonical weekly report artifact shell for every preliminary and final weekly report page. The page body must include both its week-specific class and `weekly-report-page` so it receives the shared 1120px report width and no-horizontal-page-scroll rules. The page should point `.week-report` at the public summary JSON with `data-summary-url`, set the topic labels, include `assets/weekly-report.js`, and provide placeholders for the all-item table, item-level detail cards, participant ballot table, and next-ballot table. Do not hand-build a static item table when the public JSON has item summaries and distribution series.
13. Identify key tensions where item-level disagreement is significant.
14. Suppress or combine subgroup comparisons when counts are too small.
15. Review free-text suggestions for accidental identifiers before using or publishing them.
16. Publish the report on the primary CTS website and link it from the reports index.
17. Create or update the report encapsulation for the next newsletter and the top of the next weekly SurveyOL survey.
18. Update the rolling survey control board on the Reports page when a survey moves to a new public stage, then commit the changed source/public files and publish through `scripts/publish_static_site.py`.

## Prepare Next Week

1. Rank the participant-nominated ballot results.
2. Select the top 3 eligible ranked ballot items for the next week's live participant-vote-determined questions.
3. Clean new text-box nominations into ballot-ready wording using the AI-assisted CTS review rubric: clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance. Use participant suggestions as much as possible: after current viable suggestions, prefer eligible participant-originated carryovers over new AI/seed items when they are not stale, not too recently used live, and still orthogonal.
4. Use AI-created seed items only for remaining ballot slots. Before using a seed item, compare it against the next few planned CTS-administered topics, especially the topics previewed in the current survey, and replace it if it substantially overlaps those upcoming topic blocks.
5. Update the preview of upcoming topics from the topic bank before the Tuesday report/newsletter cycle and the Tuesday evening survey launch.
6. Save the next survey draft before sending any email.

## Weekly List Hygiene

Before each SurveyOL invitation batch:

0. Run `python3 scripts/cts_ops.py env-doctor --verify-api` and stop immediately if it exits nonzero or reports `human_review_required: true`.
   If a SurveyOL token was just added or rotated, run `python3 scripts/cts_ops.py sync-env --target ~/.codex/cts.env` before the preflight so the cron path and the project path both see the same token.
1. Export or inspect SurveyOL opted-out, bounced, delivery-problem, and no-send records.
2. Treat a SurveyOL no-send, opt-out, bounce, delivery-problem, or registry do-not-email record as a global CTS email suppression.
3. Update the canonical `CTS 2026` participant registry so suppressed participants are excluded from future sends.
4. Refresh the canonical suppression artifact under `data/private/suppressions/surveyol-no-send.csv` whenever the list is rechecked, even if the member set is unchanged, so the invitation board has current evidence.
5. Record the reconciliation date and source of each suppression update in private operational notes or the participant registry.

Use `scripts/cts_ops.py` for the hardened local version of this process: verify SurveyOL API access, save the current SurveyOL no-send suppression CSV under `data/private/suppressions/surveyol-no-send.csv`, build the private SurveyOL send list, write the exact weekly contact crosswalk, and generate dry-run SurveyOL contact sync plans under `data/private/`. See `CTS_OPERATIONS_HARDENING.md`.

Prefer one stable private token file such as `.secrets/cts.env`, and mirror it to `~/.codex/cts.env` after any rotation. `scripts/cts_ops.py` auto-discovers both paths along with `.env`, `.env.local`, and `.secrets/cts-ops.env`, so the recurring automations should not depend on ad hoc shell exports. Include `SURVEYOL_API_TOKEN_EXPIRES_AT` with the token so `env-doctor` can warn before the next cron window when a token is missing expiry metadata or is close to expiry.

For browser-operated sends, prefer reclaiming an already authenticated SurveyOL tab in Chrome. If the Chrome extension path is unavailable, fall back to direct computer-use control of that same authenticated tab instead of opening a fresh SurveyOL sign-in loop.

Any generated audit or plan with `human_review_required: true` is a hard stop. Review the stated reason and next action before importing contacts, applying list changes, sending a newsletter, or sending SurveyOL invitations.

Before acting on the checklist above, regenerate the relevant automation status board and confirm no required item is `missing`, `stale`, `blocked`, `failed`, or unresolved `review_required`. For recurring invitation sends, treat the invitation scope as the controlling board for both list hygiene and any carry-forward launch send gate, especially `surveyol.reminder-auto-disabled`. Before any reminder send, require `surveyol.manual-reminder-audit` to be passed or explicitly recorded as `not_due`. A `review_required` item means the automation ran but a human gate is still open; record the review outcome before the next risky action.

## Minimum Launch Checklist

- SurveyOL survey link works.
- The first 15 live survey items are marked required in SurveyOL.
- SurveyOL title, descriptive text, previous-results placeholder, and end-of-survey page contain no closed-test language before production send.
- Previous-results/report references use an actual SurveyOL rich-text link labeled `CTS REPORTS`, with no raw URL visible to participants. The linked label is bold, underlined, header-accent colored (`#553e15` unless the banner palette changes), and enlarged with `X↑` twice.
- Placeholder public report page exists, is linked from the reports index, shows the exact final close date calculated from the planned first invitation date plus 20 days, and has been pushed before the first production invitation batch.
- CTS owner has reviewed the finished weekly SurveyOL survey or equivalent preview materials and explicitly approved the first production invitation batch; no internal test send is required unless explicitly requested.
- Featured Topic header image appears immediately before the `◉ Main topic...` introduction line.
- The `◉ Main topic...` introduction block is styled in SurveyOL: main-topic line bold and enlarged with `X↑` twice, topic name highlighted with `#e0a550` background and `#553e15` text, and response-format line bold in black.
- SurveyOL Email collector is `Open`, `Anonymous Responses` is `Off`, and any Web Link collector is closed or intentionally excluded from the launch.
- SurveyOL Email collector automatic `Reminder Follow-up` is off before the first production invitation batch, and `surveyol.reminder-auto-disabled` is recorded in the private automation ledger.
- SurveyOL recipient import comes from `CTS 2026`, excludes do-not-email records, and contains no email-only contacts with missing names.
- The exact SurveyOL recipient CSV and the live SurveyOL contact table have both passed duplicate-email checks.
- If any invitations already exist in the SurveyOL Email collector, the live invitation table has passed `audit-surveyol-invitations --fail-on-duplicates` and the exact next batch has passed `audit-batch-against-invitations --fail-on-blockers` before more invitations or any reminders are sent.
- The current weekly send-list audit and any sync plans have been reviewed, and no unresolved `human_review_required: true` output remains for the action about to be taken.
- The 3 independent live items and 7 participant-nominated ballot items are orthogonal to the weekly topic, non-duplicative, clear, and likely to produce meaningful disagreement or spread.
- The survey invitation email renders correctly.
- Full-time ministry participation note appears on the website/contact materials and email copy.
- Preview of upcoming topics appears inside SurveyOL and in the email copy.
- Privacy & Data Release page is public.
- Last week's results summary and link point to a public page.
- If any closed/internal test responses exist, they have been removed, quarantined, or documented before launch.
- Live SurveyOL respondent links and design URLs are absent from committed public files.
