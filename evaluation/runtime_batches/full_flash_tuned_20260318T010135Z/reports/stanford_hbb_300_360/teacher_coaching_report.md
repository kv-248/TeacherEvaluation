# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_hbb_300_360/run_20260318T011753Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

The session shows opportunities to refine nonverbal delivery. Focus on tightening gestures, improving audience orientation after board/note checks, and ensuring a more even room scan. These adjustments can enhance student engagement and perceived connection.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 2. Turn back toward the audience sooner

- Why it matters: Audience-facing body orientation supports perceived connection and makes eye-contact cues more visible.
- What we saw: 00:00-00:15 spent longer than needed turned away from the audience after checks. 00:15-00:30 spent longer than needed turned away from the audience after checks.
- What to try next: After each board or note check, reset your shoulders and chin back toward the room.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 3. Deliberately sweep the room

- Why it matters: More even attention across the room helps students feel included and keeps engagement distributed.
- What we saw: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep. 00:15-00:30 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to try next: At each major point, pause and sweep left-center-right before moving on.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

- No single strength clearly dominated the clip; use the cited windows as manual review anchors.

## Additional Observation Inventory

### Open the stance between points (watch item)

- Evidence: 00:00-00:15 showed a more guarded arm-and-shoulder position between teaching points. 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- Suggested response: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Low-Confidence Watchlist

### Open the stance between points

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 showed a more guarded arm-and-shoulder position between teaching points. 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- What to monitor next: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium


## Moment-by-Moment Evidence

### 00:00-00:15 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0000_0015.jpg)

- Observed behavior: low face visibility / uneven room scan / low audience orientation
- Metric evidence: Overall 36.1; room scan 52.5; presence 58.2; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `medium`

### 00:15-00:30 - Best Overall

![Evidence frame](coaching_moments/moment_02_0015_0030.jpg)

- Observed behavior: mixed evidence
- Metric evidence: Overall 41.2; room scan 54.8; presence 64.1; natural movement 19.7.
- Qwen interpretation: stance is often static.
- Coaching implication: Keep this visible pattern available as a default during explanation.

QC confidence: `medium`

### 00:45-01:00 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_03_0045_0100.jpg)

- Observed behavior: uneven room scan / low audience orientation / closed posture
- Metric evidence: Overall 37.3; room scan 41.5; presence 64.1; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `medium`

## Reliability Notes

- Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.
- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Watch For

- gesture size matching the importance of the point
- quick shoulder-and-chin resets back to the room after board/note checks
- visible sweeps of attention across the room
- open elbows and shoulders during transitions

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 38.0 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 52.8 | limited |
| Confidence/presence | 62.1 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
