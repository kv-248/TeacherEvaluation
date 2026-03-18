# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_prog_method_240_300/run_20260318T012043Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

This session highlights strong open-palm explanatory gestures and an alert, confident presence. Opportunities exist to refine gesture size for impact and ensure consistent audience orientation and room scanning. Focus on intentional movement and audience connection will enhance delivery.

Reliability: high.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: high

## Strengths to Preserve

### Open-palm explanatory delivery

- Evidence: 00:00-00:15 included open-palm explanatory gestures that supported the explanation. 00:45-01:00 included open-palm explanatory gestures that supported the explanation.
- What to repeat: Keep the same open-palm gesture shape when emphasizing key ideas.
- Review at: 00:00-00:15, 00:45-01:00, 00:30-00:45
- Confidence: high

### Alert room presence

- Evidence: 00:15-00:30 kept the head and eyes visibly engaged with the room. 00:30-00:45 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: high

### Upright confident presence

- Evidence: 00:15-00:30 held an upright, settled stance rather than a collapsed or guarded one. 00:45-01:00 held an upright, settled stance rather than a collapsed or guarded one.
- What to repeat: Keep the same upright, settled stance between points and transitions.
- Review at: 00:15-00:30, 00:45-01:00
- Confidence: high


## Additional Observation Inventory

### Turn back toward the audience sooner (watch item)

- Evidence: 00:00-00:15 spent longer than needed turned away from the audience after checks.
- Suggested response: Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Review at: 00:00-00:15
- Confidence: medium

### Deliberately sweep the room (watch item)

- Evidence: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep.
- Suggested response: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:00-00:15
- Confidence: medium

## Low-Confidence Watchlist

### Turn back toward the audience sooner

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 spent longer than needed turned away from the audience after checks.
- What to monitor next: Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Review at: 00:00-00:15
- Confidence: medium

### Deliberately sweep the room

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to monitor next: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:00-00:15
- Confidence: medium


## Moment-by-Moment Evidence

### 00:00-00:15 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0000_0015.jpg)

- Observed behavior: uneven room scan / low audience orientation / over animated delivery
- Metric evidence: Overall 48.8; room scan 48.9; presence 69.2; natural movement 28.3.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `high`

### 00:45-01:00 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0045_0100.jpg)

- Observed behavior: upright confident presence / alert room presence / open palm explaining
- Metric evidence: Overall 58.1; room scan 66.5; presence 76.9; natural movement 30.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:30-00:45 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_03_0030_0045.jpg)

- Observed behavior: low face visibility / over animated delivery / open palm explaining
- Metric evidence: Overall 54.3; room scan 69.3; presence 74.5; natural movement 26.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

## Reliability Notes

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.

## Keep Doing

- Keep the same open-palm gesture shape when emphasizing key ideas.
- Keep the same quick room checks that make the lecture feel attentive.
- Keep the same upright, settled stance between points and transitions.

## Watch For

- ["Check whether gesture size matches the importance of the point instead of peaking on routine lines.", "Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.", "Check whether the next explanation visibly reaches more than one side of the room."], "confidence_notes

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 51.9 | limited |
| Natural movement | 21.1 | limited |
| Eye-contact distribution | 61.9 | moderate |
| Confidence/presence | 75.2 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
