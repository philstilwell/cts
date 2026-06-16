# CTS MailerLite Send Plan

## Audience Groups

Current live MailerLite groups, last verified June 2, 2026. Recheck counts and group targeting directly in MailerLite before every send:

- `CTS Participants`: use for weekly survey heads-up emails, survey-link emails, and participant reminders.
- `CTS Newsletter`: use for newsletter-only subscribers who want CTS updates, report notices, and general project news but should not receive weekly survey links unless they also join the participant group.
- `CTS Closed Test`: use only for closed-test sends and internal verification.

Full-launch survey audience: `CTS Participants` group.

Newsletter/update audience: `CTS Newsletter` group. A person may belong to both `CTS Participants` and `CTS Newsletter`, but newsletter-only subscribers should not be added to `CTS Participants` unless they explicitly opt into weekly survey participation and fit the full-time ministry participation focus.

Newsletter signup form:

- MailerLite form name: `CTS Newsletter Signup`
- MailerLite form ID: `189209938164188719`
- Embedded form key: `EQ6WXD`
- Connected group: `CTS Newsletter` only
- Public site page: https://christianthoughtsurvey.com/newsletter/
- Double opt-in thank-you URL: https://christianthoughtsurvey.com/email-confirmation/
- Fields collected: email address, name, ministry status, and interest motivation.
- Purpose: result notices, topic previews, and occasional CTS articles for readers who want updates without joining the weekly survey participant panel.

Closed test recipients:

- Store and verify current test-recipient addresses inside MailerLite or in a private operational note. Do not commit personal recipient addresses to the public repository.

Closed test SurveyOL link: store the current respondent link in a private operational note. Do not commit live respondent links or SurveyOL design URLs to the public repository.

Closed test MailerLite status: verify the `CTS Closed Test` group directly in MailerLite before test sends. The survey-link email should only target that internal group during testing.

Do not send to the full `CTS Participants` group until SurveyOL has a clean response count, all production-facing survey text has no closed-test wording, and the MailerLite campaign target is confirmed.

Shared email design:

- Include a small CTS logo at the top of every email, above the greeting.
- Recommended image settings: 48-64 px wide, left aligned, alt text `Christian Thought Survey logo`.
- Logo source: https://christianthoughtsurvey.com/assets/cts-logo.png
- If MailerLite does not handle the remote image cleanly, upload the logo into MailerLite and use the uploaded image block instead.

## Email 1: Weekly Newsletter / Report Notice

Timing: Tuesday morning after the newest weekly report is published or refreshed.

Subject:

Christian Thought Survey is restarting soon

Body:

[Small CTS logo, 48-64 px wide, above greeting]

Hello,

I have fond memories of and deep appreciation for your participation in our 200-item 2023 survey. You can still find the extensive results at our new site: https://christianthoughtsurvey.com

I've decided to revive the CTS project in a less demanding, more sustainable, and more immediately useful form. Christian Thought Survey is moving to shorter weekly surveys that will take fewer than ten minutes to complete.

The expectation is that this weekly rhythm will provide timely insights to participating ministers in a dynamic age of shifting Christian doctrines and practices. Your responses will also help reflect the pulse of Christianity today.

Our first weekly survey will focus on Divorce and Remarriage. It will include 12 related credence-slider items, three independent items chosen for relevance and meaningful participant spread, a chance to vote on nominated items for future surveys, an item nomination text box, last week's results summary and link as the weekly cycle develops, and a preview of the next 3 planned general topics.

Looking ahead, the next 3 planned CTS-administered topics are Pornography and the Church, Pastoral Authority and Accountability, and Women in Church Leadership.

You will receive the first survey link on Tuesday evening in a separate SurveyOL invitation email. Participation is optional, and you can unsubscribe from future CTS emails at any time.

Thank you,

Phil
Christian Thought Survey

## Email 2: Survey Link

Timing: Tuesday evening survey launch. Send through the SurveyOL Email collector, up to 100 participant invitations per day until all eligible potential participants have been invited.

Subject:

CTS weekly survey link: Divorce and Remarriage

Body:

[Small CTS logo, 48-64 px wide, above greeting]

Hello,

The first revived Christian Thought Survey weekly survey is now ready. It should take fewer than ten minutes.

Survey link:
[Insert the current SurveyOL respondent link from private operational notes.]

This week's topic is Divorce and Remarriage.

The weekly surveys are intended for people who are currently or previously engaged in full-time ministry. We'll use 0-100 credence sliders for the survey items. You will also see three independent items chosen for relevance and meaningful participant spread, have a chance to vote on nominated items for future surveys, suggest additional items, and preview the next 3 planned general topics.

Much appreciated,

Phil
Christian Thought Survey

## Email 3: Reminder

Timing: 24-48 hours after the Tuesday survey-link email, only if appropriate.

Subject:

Reminder: CTS weekly survey

Body:

[Small CTS logo, 48-64 px wide, above greeting]

Hello,

This is a brief reminder that the current CTS weekly survey is still open.

Survey link:
[Insert the current SurveyOL respondent link from private operational notes.]

If you have already completed it, thank you. If not, your response would help test the weekly survey format.

Thank you,

Phil
Christian Thought Survey

## Closed Test Procedure

1. Create a temporary MailerLite group named `CTS Closed Test`.
2. Add only the two closed test recipients.
3. Add the small CTS logo image block to the top of each email template.
4. Send or preview Email 2 with the SurveyOL closed-test link from private operational notes.
5. Confirm both recipients receive the message and can open the survey.
6. Confirm SurveyOL received the closed-test responses.
7. Before any bulk campaign, copy/reset the SurveyOL survey or delete/exclude all closed-test responses so authentic results begin from a clean dataset.
8. Do not schedule any bulk campaign until the closed test is reviewed and response quarantine is complete.
