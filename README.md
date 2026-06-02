# Christian Thought Survey

Static GitHub Pages mirror for the revived Christian Thought Survey site.

## Weekly Survey Structure

Each Weekly Survey is designed to include:

1. One CTS-administered topic: 12 related survey items from the CTS topic bank.
2. Three participant-vote-determined questions: 3 additional live survey items chosen based on the previous week's participant vote.
3. A participant-nominated item ballot: 7 AI-polished ballot items selected from the previous week's participant nominations. If fewer than 7 suitable participant nominations are available, CTS adds AI-created seed items to complete the ballot.
4. **A text box:** to suggest survey items to be voted on next week and possibly featured in the following week's survey.
5. Last week's results summary and link: a brief summary and a link to the primary CTS website page containing the previous week's results and reports.
6. A preview of upcoming topics: The topics for the next three weeks will be featured to allow for mental preparation.

The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses.

Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, novelty, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked items become live participant-vote-determined survey items in the following week's survey.

Independent live items and participant-nominated ballot items should be orthogonal to the weekly CTS-administered topic, non-duplicative, semantically clear, and likely to produce meaningful disagreement or spread. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas when useful, but current weekly items should be rewritten for clarity rather than copied mechanically.

## Weekly Cadence

The regular send rhythm is a Monday heads-up email followed by the actual SurveyOL survey-link email on Thursday. The Monday email names the current topic and previews the next 3 planned general topics; the Thursday survey includes that same preview of upcoming topics inside the survey itself.

## MailerLite Audience Groups

- `CTS Participants`: survey participants who may receive weekly heads-up emails, survey links, and participant reminders.
- `CTS Newsletter`: newsletter-only subscribers who may receive report notices, topic previews, and general CTS updates.
- `CTS Closed Test`: temporary/internal test recipients.

Do not send weekly survey links to `CTS Newsletter` unless a subscriber is also intentionally included in `CTS Participants`.

The generated pages reflect the new WordPress pages updated on June 1, 2026:

- Christian Thought Survey 2026
- Weekly Survey Reports
- Previous Results Archive
- Legacy Survey Overview
- Contact & Weekly Survey Participation
- Privacy & Data Release

Internal launch planning files:

- `WEEK_1_SURVEY_TEMPLATE.md`
- `WEEK_1_ITEM_AUDIT.md`
- `WEEKLY_RUNBOOK.md`
- `DATA_PIPELINE_PLAN.md`
- `WEEKLY_REPORTING_STRATEGY.md`
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
