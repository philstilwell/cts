# CTS Weekly Survey Runbook

Use this runbook for each weekly CTS cycle.

For the detailed participant-nominated ballot scoring and tie-breaking protocol, use `PARTICIPANT_NOMINATED_BALLOT_PROTOCOL.md`.

For topic/item tension preflights, use `TOPIC_BANK_TENSION_REVIEW.md` and `NEXT_3_TOPIC_ITEM_REVIEW.md`. For older CTS seed themes, use `LEGACY_200_ITEM_INDEX.md` and `data/public/legacy-200-items.json`. For the Week 1 seed audit, use `WEEK_1_ITEM_AUDIT.md`.

## Weekly Cadence

- Monday: send the MailerLite heads-up email for the Thursday survey, naming the current CTS-administered topic and previewing the next 3 planned general topics.
- Tuesday: finalize the SurveyOL survey, including the 7-item AI-polished participant-nominated ballot.
- Wednesday: test the SurveyOL link, MailerLite copy, previous-results link, and preview of upcoming topics.
- Thursday: send the actual SurveyOL survey-link email.
- Friday: export results, publish public summary, and prepare next week's participant-vote items.

## Build The Survey

1. Select one CTS-administered topic from `CTS 2026 Weekly Topic Bank.md`.
2. Review the selected topic for clarity and tension potential before fielding it, then add the narrow Featured Topic header image and the topic's 12 survey items as required 0-100 credence sliders.
3. Add the narrow Independent Items header image, then add 3 participant-vote-determined live survey items from the previous week's ballot. These items should be semantically clear, orthogonal to the weekly CTS-administered topic, not copied from the current topic bank, and likely to generate meaningful tension or spread. For Week 1 only, use the seeded items in `WEEK_1_SURVEY_TEMPLATE.md`.
4. Add the participant-nominated item ballot. Review participant suggestions with AI assistance, polish them for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance, and reduce them to 7 ballot items. If fewer than 7 suitable participant nominations are available, add AI-created seed items to complete the ballot. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas, but ballot items should be rewritten for current clarity and should not be copied mechanically.
5. Save a brief item-audit note for the 3 independent live items and 7 ballot items before finalizing SurveyOL.
6. Add a text box for future participant-nominated survey items.
7. Add a brief previous-results summary and a link to the public weekly report page. For Week 1, use the no-previous-results placeholder.
8. Add a preview of upcoming topics. The topics for the next three weeks should be featured to allow for mental preparation.
9. Confirm the full-time ministry participation note appears in the website/contact materials and email copy. Do not add a separate eligibility confirmation item inside the weekly SurveyOL survey unless CTS intentionally reintroduces one.

## Send The Survey

1. Send the MailerLite heads-up email on Monday before the Thursday survey-link email.
2. Send the Thursday survey-link email only after testing the SurveyOL link in a private browser/session.
3. Send one reminder to non-respondents 24-48 hours after the Thursday survey-link email when appropriate. Do not over-message the list.
4. Keep unsubscribe handling in MailerLite. Do not manually re-add unsubscribed contacts.

## Export And Report

1. Export SurveyOL responses after the response window closes.
2. Save the private raw export in `data/private/surveyol/week-###.csv`. Do not commit raw exports.
3. Generate the public summary JSON with `scripts/cts_report_pipeline.py` and the matching `reporting/week-###.config.json`.
4. Review the generated summary's `quality` section for missing columns, non-numeric values, out-of-range values, and unexpectedly low counts.
5. Remove or separate names, email addresses, and direct identifiers before preparing public files.
6. Summarize all 15 live slider items with count, mean, median, and distribution shape, including the S23-style smoothed sparkline series when sample size permits.
7. Identify key tensions where item-level disagreement is significant.
8. Suppress or combine subgroup comparisons when counts are too small.
9. Review free-text suggestions for accidental identifiers before using or publishing them.
10. Publish the report on the primary CTS website and link it from the reports index.

## Prepare Next Week

1. Rank the participant-nominated ballot results.
2. Select the top 3 eligible ranked ballot items for the next week's live participant-vote-determined questions.
3. Clean new text-box nominations into ballot-ready wording using the AI-assisted CTS review rubric: clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance.
4. Update the preview of upcoming topics from the topic bank before the Monday heads-up email.
5. Save the next survey draft before sending any email.

## Minimum Launch Checklist

- SurveyOL survey link works.
- The first 15 live survey items are marked required in SurveyOL.
- The 3 independent live items and 7 participant-nominated ballot items are orthogonal to the weekly topic, non-duplicative, clear, and likely to produce meaningful disagreement or spread.
- MailerLite test email renders correctly.
- Full-time ministry participation note appears on the website/contact materials and email copy.
- Preview of upcoming topics appears inside SurveyOL and in the email copy.
- Privacy & Data Release page is public.
- Previous-results link points to a public page.
- Test recipients can complete the survey.
- No mass send is scheduled until the closed test is reviewed.
