# CTS Weekly Survey Runbook

Use this runbook for each weekly CTS cycle.

For the detailed participant-nominated ballot scoring and tie-breaking protocol, use `PARTICIPANT_NOMINATED_BALLOT_PROTOCOL.md`.

For topic/item tension preflights, use `TOPIC_BANK_TENSION_REVIEW.md` and `NEXT_3_TOPIC_ITEM_REVIEW.md`. For older CTS seed themes, use `LEGACY_200_ITEM_INDEX.md` and `data/public/legacy-200-items.json`. For the Week 1 seed audit, use `WEEK_1_ITEM_AUDIT.md`.

## Weekly Cadence

- Monday: send the heads-up email for the Thursday survey, naming the current CTS-administered topic and previewing the next 3 planned general topics. MailerLite may be used for general announcements and report notices, but the identity-bearing survey invitation should come from the SurveyOL Email collector.
- Tuesday: finalize the SurveyOL survey, including the 7-item AI-polished participant-nominated ballot and the SurveyOL Email collector settings.
- Wednesday: test the SurveyOL Email collector invitation path, export shape, last week's results summary and link, and preview of upcoming topics.
- Thursday: send the actual SurveyOL Email collector invitation.
- Friday: export results, publish public summary, and prepare next week's participant-vote items.

## Build The Survey

1. Select one CTS-administered topic from `CTS 2026 Weekly Topic Bank.md`.
2. Review the selected topic for clarity and tension potential before fielding it, then add the narrow Featured Topic header image and the topic's 12 survey items as required 0-100 credence sliders.
3. Add the narrow Independent Items header image, then add 3 participant-vote-determined live survey items from the previous week's ballot. These items should be semantically clear, orthogonal to the weekly CTS-administered topic, not copied from the current topic bank, and likely to generate meaningful tension or spread. For Week 1 only, use the seeded items in `WEEK_1_SURVEY_TEMPLATE.md`.
4. Add the participant-nominated item ballot. Review participant suggestions with AI assistance, polish them for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance, and reduce them to 7 ballot items. If fewer than 7 suitable participant nominations are available, add AI-created seed items to complete the ballot. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas, but ballot items should be rewritten for current clarity and should not be copied mechanically.
5. Save a brief item-audit note for the 3 independent live items and 7 ballot items before finalizing SurveyOL.
6. Add a text box for future participant-nominated survey items.
7. Add a brief last-week results summary and a link to the public weekly report page. For Week 1, use the no-previous-results placeholder.
8. Add a preview of upcoming topics. The topics for the next three weeks should be featured to allow for mental preparation.
9. Confirm the full-time ministry participation note appears in the website/contact materials and email copy. Do not add a separate eligibility confirmation item inside the weekly SurveyOL survey unless CTS intentionally reintroduces one.
10. Keep the public report URL stable before the send. Week 1 uses `https://christianthoughtsurvey.com/weekly-survey-reports/week-001-divorce-and-remarriage/`.
11. Before any full participant send, remove all closed-test wording from the SurveyOL title, intro text, previous-results placeholder, and end-of-survey page.

## Send The Survey

1. Send the Monday heads-up through the chosen announcement channel, but send the actual Thursday survey invitation through that week's SurveyOL Email collector. For closed tests, use only internal/test contacts.
2. The SurveyOL Email collector must be `Open` with `Anonymous Responses` set to `Off` so exports can include email identity for private matching. Close or do not distribute Web Link collectors unless CTS intentionally wants an unmapped public response channel.
3. Build the SurveyOL recipient list from the canonical `CTS 2026` participant registry. Include only eligible records with `Name`, `Primary Email Address`, `Participant ID`, and `Email Key`, and exclude records marked `Do Not Email? = Yes`, unsubscribed, opted out, bounced, or otherwise suppressed.
4. Include stable private join fields in SurveyOL contact fields when SurveyOL supports them: `Participant ID` and `Email Key`. If SurveyOL does not export contact custom fields, save the exact send-list crosswalk privately for that week.
5. Before any full send, invite at least one internal test recipient through the Email collector, complete the survey, export the test result, and confirm the export includes email identity or another reliable join key.
6. Send one reminder to non-respondents 24-48 hours after the Thursday survey-link email when appropriate. Prefer SurveyOL's non-response tracking so reminders do not go to people who already completed the survey.
7. Keep newsletter-only subscribers in the separate `CTS Newsletter` group. Use that group for report notices, topic previews, and general CTS updates; do not send weekly survey links to newsletter-only subscribers.
8. After each send, reconcile SurveyOL `Opted Out`, bounced, and delivery-problem records back into `CTS 2026` before the next recipient import.
9. The public newsletter form at `https://christianthoughtsurvey.com/newsletter/` collects email address, name, ministry status, and interest motivation, and should add subscribers only to `CTS Newsletter`.
10. The newsletter double opt-in thank-you page should redirect to `https://christianthoughtsurvey.com/email-confirmation/`.
11. Keep live SurveyOL respondent links and design URLs in SurveyOL or private operational notes only. Do not commit them to the public repository.

## Participant Profile Intake

The public Contact & Weekly Survey Participation form is only the eligibility and interest front door. When a potential participant appears to be currently or previously engaged in full-time ministry, send the private `CTS 2026 Participant Profile Survey` documented in `PARTICIPANT_PROFILE_SURVEY.md`.

Do not link the participant-profile survey publicly. Add or confirm a person in the `CTS 2026` participant registry only after eligibility review and profile completion, then include them in SurveyOL weekly recipient imports only when they meet the outreach filter. Store raw profile exports under `data/private/participant-profiles/`, and never commit names, email addresses, or individual profile rows.

## Closed-Test Response Quarantine

Closed-test submissions made through the real SurveyOL respondent link count as real SurveyOL responses. They are not automatically quarantined from later authentic survey responses.

Before any full participant send, do one of the following:

1. Preferred: copy or reset the tested SurveyOL survey so the public launch starts with zero responses.
2. Acceptable: delete all closed-test responses from SurveyOL before the public launch, after confirming no authentic responses have arrived.
3. Fallback: export closed-test responses separately, record their SurveyOL response numbers, start times, and UTM parameters, and exclude them from the private raw export before generating public reports.

For Week 1, closed-test responses `#1` and `#2` were deleted from SurveyOL on June 2, 2026 before public launch. SurveyOL was rechecked on June 3, 2026 after title/text cleanup and still showed no responses so far. Recheck the SurveyOL summary again immediately before the Thursday send.

For Week 1, the anonymous Web Link collector was closed on June 10, 2026 and the Email collector was left open with `Anonymous Responses` set to `Off` so private exports can be mapped back to the `CTS 2026` registry.

## Export And Report

1. Export SurveyOL responses after the response window closes.
2. Save the private raw export in `data/private/surveyol/week-###.csv`. Do not commit raw exports.
3. Normalize email addresses and join the private export to the `CTS 2026` participant registry before subgroup or deep analysis. Flag unmatched rows and resolve them before publishing a report.
4. Save any joined identity-bearing analysis file under `data/private/`. Do not commit joined files, contact crosswalks, names, email addresses, participant IDs, or raw free-text suggestions.
5. Generate the public summary JSON with `scripts/cts_report_pipeline.py` and the matching `reporting/week-###.config.json`.
6. Review the generated summary's `quality` section for missing columns, non-numeric values, out-of-range values, unexpectedly low counts, and unexpected unmatched-response counts.
7. Summarize all 15 live slider items with count, mean, median, and distribution shape, including the S23-style smoothed sparkline series when sample size permits.
8. Identify key tensions where item-level disagreement is significant.
9. Suppress or combine subgroup comparisons when counts are too small.
10. Review free-text suggestions for accidental identifiers before using or publishing them.
11. Publish the report on the primary CTS website and link it from the reports index.

## Prepare Next Week

1. Rank the participant-nominated ballot results.
2. Select the top 3 eligible ranked ballot items for the next week's live participant-vote-determined questions.
3. Clean new text-box nominations into ballot-ready wording using the AI-assisted CTS review rubric: clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance.
4. Update the preview of upcoming topics from the topic bank before the Monday heads-up email.
5. Save the next survey draft before sending any email.

## Minimum Launch Checklist

- SurveyOL survey link works.
- The first 15 live survey items are marked required in SurveyOL.
- SurveyOL title, descriptive text, previous-results placeholder, and end-of-survey page contain no closed-test language before production send.
- SurveyOL Email collector is `Open`, `Anonymous Responses` is `Off`, and any Web Link collector is closed or intentionally excluded from the launch.
- SurveyOL recipient import comes from `CTS 2026`, excludes do-not-email records, and contains no email-only contacts with missing names.
- A test Email collector export confirms that responses can be joined back to `CTS 2026` by email identity or a stable private join key.
- The 3 independent live items and 7 participant-nominated ballot items are orthogonal to the weekly topic, non-duplicative, clear, and likely to produce meaningful disagreement or spread.
- The survey invitation email renders correctly.
- Full-time ministry participation note appears on the website/contact materials and email copy.
- Preview of upcoming topics appears inside SurveyOL and in the email copy.
- Privacy & Data Release page is public.
- Last week's results summary and link point to a public page.
- Test recipients can complete the survey.
- No mass send is scheduled until the closed test is reviewed.
- Live SurveyOL respondent links and design URLs are absent from committed public files.
