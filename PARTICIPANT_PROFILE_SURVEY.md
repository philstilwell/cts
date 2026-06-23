# CTS Participant Profile Survey

Use this protocol for the private participant-profile survey sent after a potential participant has been reviewed and appears to fit the CTS weekly survey panel.

The public Contact & Weekly Survey Participation form is only the interest and eligibility front door. The participant-profile survey is a separate, unlinked SurveyOL survey used to collect the same broad profile information available for the 2023 participant pool.

## Current SurveyOL Form

- Survey title: `CTS 2026 Participant Profile Survey`
- Store the private respondent link in `data/private/participant-profile-survey-link.md` or another non-public operational note.
- Do not commit the respondent link or SurveyOL design URL to the public repository.
- Status at creation: open, anonymous responses on, multiple responses off, responses `0`.

Keep the link out of public CTS pages and public repo files. It is not a security boundary, but it should function as a private follow-up form sent only after eligibility review.

Implementation note: SurveyOL's copy/paste importer initially created the introductory paragraph as a textbox question. It has been corrected in SurveyOL to a `Text (Descriptive)` block, so the first response field is now `Full name`. The canonical field structure below remains the source of truth for future rebuilds.

## Workflow

1. Potential participant submits the public participation request form.
2. CTS reviews whether the person is currently or previously engaged in full-time ministry.
3. If approved, CTS sends the private participant-profile survey link.
4. After the profile is complete, CTS adds or confirms the person in the current CTS participant registry and invitation workflow.
5. Keep update-only readers out of the weekly survey participant workflow unless they explicitly opt into survey participation and fit the ministry-participant focus.

## Source Schema

The profile fields are based on the old `S23 - CTS` Google Sheet, especially the profile columns before the 200 survey item responses.

Core fields to preserve:

- Name and email address.
- Ministry eligibility and current/previous ministry status.
- Denomination or fellowship family.
- Evangelical and fundamentalist self-identification.
- Birth year and year first identifying as Christian.
- Religious, secular, Bible college, and seminary education/training.
- Part-time and full-time ministry experience.
- Current full-time, part-time, or half-time-plus religious education/ministry status.
- Old Testament and New Testament reading familiarity in primary language and original languages.
- Local religious context estimates: religiously unaffiliated, Christian identification, and church attendance.
- Current location and countries lived in.
- Optional demographics: gender, marital status, number of children, and race/ethnicity.

## SurveyOL Copy/Paste Draft

Survey title:

```text
CTS 2026 Participant Profile Survey
```

Questions:

```text
[Text]
This private profile survey is for approved CTS weekly survey participants. It helps CTS compare new participant profiles with the 2023 participant pool. Please answer as accurately as is practical. Optional demographic fields may be left blank.

[Textbox List][Required]
Contact information
Full name
Email address

[Dropdown][Required]
Which statement best describes your ministry background?
I am currently engaged in full-time ministry.
I was previously engaged in full-time ministry.
I am in part-time ministry but have not been in full-time ministry.
I am not currently or previously engaged in full-time ministry.
Prefer to explain in the final comment box.

[Dropdown][Required]
What is your primary current or most recent ministry role?
Lead or senior pastor
Associate or assistant pastor
Missionary or church planter
Chaplain
Professor, teacher, or trainer
Youth, children, or family ministry
Worship or creative ministry
Parachurch or nonprofit ministry
Church administration or operations
Other ministry role

[Dropdown][Required]
What is your primary denominational or fellowship family?
Southern Baptist
Baptist, other
Non-denominational or independent
Assembly of God
Church of Christ
Presbyterian or Reformed
Methodist or Wesleyan
Lutheran
Anglican or Episcopal
Pentecostal or charismatic, other
Roman Catholic
Eastern Orthodox
Anabaptist or Mennonite
Restorationist
Other Protestant
Other Christian tradition
Prefer not to say

[Textbox]
If you selected other or want to clarify your denomination/fellowship, please specify.

[Multiple Choice][Required]
Do you identify as evangelical?
Yes
No
Unsure
Prefer not to say

[Multiple Choice][Required]
Do you identify as fundamentalist?
Yes
No
Unsure
Prefer not to say

[Textbox List][Required]
Year and education profile
Birth year
Year you first identified as Christian
Approximate years of formal secular post-secondary education
Approximate years of formal religious/theological education outside Bible college or seminary
Approximate years in Bible college
Approximate years in seminary or graduate theological education

[Textbox List][Required]
Ministry experience and current status
Approximate years in part-time ministry
Approximate years in full-time ministry
Currently in full-time ministry? (Yes/No)
Currently in part-time ministry? (Yes/No)
Currently in half-time or greater religious education/training? (Yes/No)

[Textbox List][Required]
Bible reading familiarity
Approximate times read the Old Testament in your primary language
Approximate times read the Old Testament in Hebrew
Approximate times read the New Testament in your primary language
Approximate times read the New Testament in Greek

[Textbox List][Required]
Local context and location
Approximate percent of people in your community who are religiously unaffiliated or nones
Approximate percent of people in your community who identify as Christian
Approximate average weekly attendance of your current or most recent local church/ministry context
Current country
Current state/province/region
Number of countries lived in for one year or more

[Textbox List]
Optional demographics
Gender
Marital status
Number of children
Race/ethnicity

[Comment Box]
Is there any additional context CTS should know when interpreting your participant profile?
```

## Handling Rules

- Do not link this survey publicly from the CTS website.
- Send the profile survey only after eligibility review.
- Store raw profile exports only under `data/private/`.
- Do not commit names, email addresses, or individual profile rows.
- Use profile fields in public reports only as grouped aggregates, and suppress subgroup reporting when counts are too small.
