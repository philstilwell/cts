# Christian Thought Survey

Static GitHub Pages mirror for the revived Christian Thought Survey site.

## Weekly Survey Structure

How the weekly cycle works:

1. Last week's results summary and link: a brief summary and a link to the primary CTS website page containing the previous week's results and reports.
2. One CTS-administered topic: the Featured Topic header image appears immediately before a `◉ Main topic...` introduction line, followed by 12 related survey items from the CTS topic bank.
3. Three participant-vote-determined questions: 3 additional live survey items chosen based on the previous week's participant vote. These are intentionally independent from the weekly CTS-administered topic.
4. A participant-nominated item ballot: 7 AI-polished ballot items selected from the previous week's participant nominations, with AI-created seed items added only when fewer than 7 suitable participant nominations are available. Ballot items are selected for clarity, relevance, novelty, and likely participant tension.
5. **A text box:** to suggest survey items to be voted on next week and possibly featured in the following week's survey.
6. A preview of upcoming topics: The topics for the next three weeks will be featured to allow for mental preparation.

The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses.

Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, novelty, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked items become live participant-vote-determined survey items in the following week's survey.

Independent live items and participant-nominated ballot items should be orthogonal to the weekly CTS-administered topic, non-duplicative, semantically clear, and likely to produce meaningful disagreement or spread. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas when useful, but current weekly items should be rewritten for clarity rather than copied mechanically.

## Weekly Cadence

The regular weekly rhythm is Tuesday-centered. Tuesday morning is the report window: publish the first preliminary report for any survey launched one week earlier and refresh every still-open preliminary report. Tuesday evening is the new survey launch window: create the placeholder public report page, open the SurveyOL Email collector, and send the first batch of up to 100 participant invitations. Continue sending up to 100 invitations per day until all eligible participants have been invited. Each weekly survey remains open for three weeks from the first invitation send, so the placeholder page and each preliminary report must show the exact final close date calculated as the first production invitation date plus 21 days. Preliminary reports are refreshed each Tuesday morning until that posted close date, then the collector is closed and the report is regenerated as final. A SurveyOL no-send, opt-out, bounce, delivery-problem, or registry do-not-email record suppresses that address from future survey invitations.

## Legacy MailerLite Note

Mailerlite-related pages and notes remain in the repository for historical/public-site continuity, but MailerLite is no longer part of the operational weekly survey process. The active invitation workflow now trusts SurveyOL's no-send list plus the canonical `CTS 2026` registry only.

The generated pages reflect the new WordPress pages updated on June 1, 2026:

- Christian Thought Survey 2026
- Weekly Survey Reports
- Week 1 Report: Divorce and Remarriage
- Previous Results Archive
- Legacy Survey Overview
- Newsletter Signup
- Email Subscription Confirmed
- Contact & Weekly Survey Participation
- Privacy & Data Release

Internal launch planning files:

- `WEEK_1_SURVEY_TEMPLATE.md`
- `WEEK_1_ITEM_AUDIT.md`
- `WEEKLY_RUNBOOK.md`
- `CTS_OPERATIONS_HARDENING.md`
- `DATA_PIPELINE_PLAN.md`
- `WEEKLY_REPORTING_STRATEGY.md`
- `PARTICIPANT_PROFILE_SURVEY.md`
- `PARTICIPANT_NOMINATED_BALLOT_PROTOCOL.md`
- `TOPIC_BANK_TENSION_REVIEW.md`
- `NEXT_3_TOPIC_ITEM_REVIEW.md`
- `LEGACY_200_ITEM_INDEX.md`
- `MAILERLITE_SEND_PLAN.md`

Run the static build with:

```bash
python3 scripts/build_static_site.py
```

Refresh the legacy 200-item reference index with:

```bash
python3 scripts/build_legacy_item_index.py
```

Build private weekly send lists and API sync plans with:

```bash
python3 scripts/cts_ops.py --help
```

Mirror the active CTS private env values into the Codex-wide fallback file after any token rotation with:

```bash
python3 scripts/cts_ops.py sync-env --target ~/.codex/cts.env
```

Update the public-safe automation log source with:

```bash
python3 scripts/update_automation_daily_log.py --help
```

Audit the local CTS cron definitions to confirm they all require public automation-log updates with:

```bash
python3 scripts/audit_cts_cron_logging.py
```
