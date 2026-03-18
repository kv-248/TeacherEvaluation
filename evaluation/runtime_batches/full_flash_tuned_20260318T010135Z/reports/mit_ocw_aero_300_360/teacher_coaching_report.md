# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_aero_300_360/run_20260318T010303Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

This session shows a teacher who effectively uses open-palm gestures to explain concepts. Opportunities exist to refine gesture size, ensure more even room engagement through deliberate sweeps, and consistently reorient towards the audience after board or note checks. These adjustments can enhance student connection and focus.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 2. Deliberately sweep the room

- Why it matters: More even attention across the room helps students feel included and keeps engagement distributed.
- What we saw: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep. 00:15-00:30 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to try next: At each major point, pause and sweep left-center-right before moving on.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 3. Turn back toward the audience sooner

- Why it matters: Audience-facing body orientation supports perceived connection and makes eye-contact cues more visible.
- What we saw: 00:00-00:15 spent longer than needed turned away from the audience after checks. 00:15-00:30 spent longer than needed turned away from the audience after checks.
- What to try next: After each board or note check, reset your shoulders and chin back toward the room.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

### Open-palm explanatory delivery

- Evidence: 00:30-00:45 included open-palm explanatory gestures that supported the explanation. 00:00-00:15 included open-palm explanatory gestures that supported the explanation.
- What to repeat: Keep the same open-palm gesture shape when emphasizing key ideas.
- Review at: 00:30-00:45, 00:00-00:15
- Confidence: medium


## Additional Observation Inventory

### Open the stance between points (watch item)

- Evidence: 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- Suggested response: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:15-00:30
- Confidence: low

## Low-Confidence Watchlist

### Open the stance between points

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- What to monitor next: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:15-00:30
- Confidence: low


## Moment-by-Moment Evidence

### 00:15-00:30 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0015_0030.jpg)

- Observed behavior: low face visibility / uneven room scan / low audience orientation
- Metric evidence: Overall 35.3; room scan 31.1; presence 58.3; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `low`

### 00:30-00:45 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0030_0045.jpg)

- Observed behavior: open palm explaining / distributed room engagement
- Metric evidence: Overall 44.8; room scan 31.0; presence 69.0; natural movement 24.7.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:00-00:15 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_03_0000_0015.jpg)

- Observed behavior: low face visibility / uneven room scan / low audience orientation
- Metric evidence: Overall 38.8; room scan 29.7; presence 69.7; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `medium`

## Reliability Notes

- Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.
- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Keep using open-palm gestures to emphasize key ideas.
- Reuse the left-center-right room sweep that already looks natural.

## Watch For

- Gesture size matching the importance of the point.
- Visible left-center-right room sweeps during explanations.
- Quick shoulder-and-chin resets back to the room after board or note checks.
- Transitions keeping elbows and shoulders open.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 38.3 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 30.3 | limited |
| Confidence/presence | 65.3 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
