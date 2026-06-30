# Participant-Nominated Ballot Protocol

Use this protocol for the participant-nominated item ballot in each weekly CTS survey.

## Purpose

The ballot keeps participant-generated questions in the weekly survey cycle while preserving CTS standards for clarity, neutrality, theological/pastoral relevance, and credence-slider suitability.

Ballot items should also be intentionally orthogonal to the weekly CTS-administered topic. They should not be copied from the current 50-topic bank or from recent live survey items, though the older 200-item CTS survey may be indexed as a reference pool for possible themes or seed ideas when needed. Use `LEGACY_200_ITEM_INDEX.md` or `data/public/legacy-200-items.json` for that reference pool.

## Weekly Rule

Each weekly survey includes a 7-item participant-nominated item ballot.

1. Collect participant suggestions from the previous week's survey text box.
2. Remove accidental identifiers, private details, duplicates, and unusable fragments.
3. Use CTS review with AI assistance to polish viable nominations into standalone survey-item statements.
4. Score the polished items with the rubric below.
5. Place the top 7 suitable items on the next weekly ballot.
6. If fewer than 7 suitable participant nominations are available, first use eligible participant-originated carryovers when they are still fresh, orthogonal, and not too recently used as live items; then add AI-created seed items only as needed until the ballot has 7 items.
7. Active participants rank the 7 ballot items.
8. The top 3 ranked eligible items become live participant-vote-determined survey items in the following week's survey.

## Polishing Standard

Polishing may correct grammar, simplify wording, combine near-duplicates, remove identifying details, make the item credence-slider ready, and reduce loaded language. Polishing should not reverse or materially distort the participant's substantive direction.

## Assessment Rubric

Score each viable candidate from 0 to 2 on each criterion:

- Clarity: the item can be understood quickly without extra context.
- Credence-slider suitability: the item can be rated meaningfully from 0 to 100.
- Neutrality: the wording does not push participants toward one answer.
- Breadth: the item is likely to interest more than a tiny subset of participants.
- Orthogonality: the item is independent from the weekly CTS-administered topic.
- Novelty: the item does not duplicate the current topic bank or recent live items.
- Tension potential: the item is likely to produce meaningful disagreement or a wide distribution rather than a near-unanimous response.
- Pastoral/theological relevance: the item connects meaningfully to ministry, doctrine, practice, or Christian thought.

Total possible score: 16.

## Tie Handling

When items are tied for the final ballot slots, prefer the item that:

1. Has higher pastoral/theological relevance.
2. Has higher tension potential.
3. Has higher breadth.
4. Adds more topical diversity to the ballot.
5. Has not appeared recently in a live survey or ballot.

## AI-Created Seed Items

Use AI-created seed items only when fewer than 7 suitable participant nominations or eligible participant-originated carryovers are available. Seed items should follow the same rubric and should be broad enough to rank against participant-nominated items. Seed items must be sufficiently distinct from the next few planned CTS-administered weekly topics, especially the topics previewed in the current survey, so the optional ballot does not pre-run an upcoming topic block. Seed items may draw inspiration from the older 200-item CTS survey when useful, but should be rewritten as clear, current, orthogonal items rather than copied mechanically. Keep an internal note identifying which ballot items were participant-originated and which were CTS/AI seed items.

## Audit Trail

For each weekly ballot, keep a local note with:

- Raw participant suggestion, unless it contains sensitive identifying details.
- Polished ballot wording.
- Rubric score.
- Whether the item was participant-originated or CTS/AI seeded.
- Reason for excluding any otherwise plausible nomination.
