# Christian Thought Survey

Static GitHub Pages mirror for the revived Christian Thought Survey site.

## Weekly Survey Structure

Each Weekly Survey is designed to include:

1. One CTS-administered topic with 12 related survey items from the already-generated topic bank.
2. Three participant-vote-determined questions. The first week is seeded by AI; later weeks use the previous week's active-participant vote.
3. A ballot of participant-nominated survey items from the previous week. These nominations are cleaned up by AI before release, and the top 3 vote-getters become live survey items the following week.
4. Links to the primary CTS website page containing the previous week's results.
5. A compact sample of the previous week's results, such as an infographic-style summary.

All survey items are credence-based slider items. The participant-nominated survey item fields are text boxes because they collect possible future items rather than survey-item responses.

The generated pages reflect the new WordPress pages updated on June 1, 2026:

- Christian Thought Survey 2026
- Weekly Survey Reports
- Previous Results Archive
- Legacy Survey Overview
- Contact & Weekly Survey Participation

Run the static build with:

```bash
python3 scripts/build_static_site.py
```
