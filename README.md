# Christian Thought Survey

Static GitHub Pages mirror for the revived Christian Thought Survey site.

## Weekly Survey Structure

How the weekly cycle works:

1. One CTS-administered topic: 12 related survey items from the CTS topic bank.
2. Three participant-vote-determined questions: 3 additional live survey items chosen based on the previous week's participant vote. These are intentionally independent from the weekly CTS-administered topic.
3. A participant-nominated item ballot: 7 AI-polished ballot items selected from the previous week's participant nominations, with AI-created seed items added only when fewer than 7 suitable participant nominations are available. Ballot items are selected for clarity, relevance, novelty, and likely participant tension.
4. **A text box:** to suggest survey items to be voted on next week and possibly featured in the following week's survey.
5. Last week's results summary and link: a brief summary and a link to the primary CTS website page containing the previous week's results and reports.
6. A preview of upcoming topics: The topics for the next three weeks will be featured to allow for mental preparation.

The 15 live survey items use credence sliders. The participant-nominated item ballot and suggestion text box are administrative inputs rather than survey-item responses.

Participant suggestions are reviewed by CTS with AI assistance, polished for clarity, neutrality, credence-slider suitability, breadth, novelty, and pastoral or theological relevance, and reduced to a 7-item ballot. Active participants rank those 7 items; the top 3 ranked items become live participant-vote-determined survey items in the following week's survey.

Independent live items and participant-nominated ballot items should be orthogonal to the weekly CTS-administered topic, non-duplicative, semantically clear, and likely to produce meaningful disagreement or spread. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas when useful, but current weekly items should be rewritten for clarity rather than copied mechanically.

## Weekly Cadence

The regular weekly rhythm is Tuesday-centered. Tuesday morning is the report and newsletter window: publish or refresh the report for the survey launched one week earlier, send the MailerLite newsletter to subscribers, and include a short report encapsulation plus a link. Tuesday evening is the new survey launch window: create the placeholder public report page, open the SurveyOL Email collector, and send the first batch of up to 100 participant invitations. Continue sending up to 100 invitations per day until all eligible participants have been invited. Each weekly survey remains open for three weeks from the first invitation send, after which the collector is closed and the report is regenerated as final. An unsubscribe, opt-out, bounce, or do-not-email record in either SurveyOL or MailerLite suppresses that address from both systems before future sends.

## MailerLite Audience Groups

- `CTS Participants`: survey participants who may receive weekly heads-up emails, survey links, and participant reminders.
- `CTS Newsletter`: newsletter-only subscribers who may receive report notices, topic previews, and general CTS updates.
- `CTS Closed Test`: temporary/internal test recipients.

Do not send weekly survey links to `CTS Newsletter` unless a subscriber is also intentionally included in `CTS Participants`.

The public Contact & Weekly Survey Participation page is the eligibility and interest front door for potential survey participants. Approved potential participants should receive the separate private participant-profile survey documented in `PARTICIPANT_PROFILE_SURVEY.md` before being added or confirmed in `CTS Participants`.

The public newsletter signup page is `/newsletter/`. Its MailerLite embedded form is connected only to `CTS Newsletter` and collects email address, name, ministry status, and the subscriber's motivation for interest.

MailerLite double opt-in for the newsletter form redirects confirmed subscribers to `/email-confirmation/`. That page is intentionally not linked from navigation and is marked `noindex`.

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
