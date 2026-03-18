# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_quantum_240_300/run_20260318T013148Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

This report highlights opportunities to refine gesture size and audience orientation. Strengths include an alert room presence and distributed room engagement. Focus on tightening gestures and turning back to the audience sooner after board or note checks. Continue to leverage your natural room sweeps.

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
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45
- Confidence: medium

## Strengths to Preserve

### Alert room presence

- Evidence: 00:45-01:00 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:45-01:00
- Confidence: low

### Distributed room engagement

- Evidence: 00:45-01:00 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:45-01:00
- Confidence: low


## Additional Observation Inventory

### Deliberately sweep the room (watch item)

- Evidence: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep.
- Suggested response: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:00-00:15
- Confidence: low

### Open the stance between points (watch item)

- Evidence: 00:00-00:15 showed a more guarded arm-and-shoulder position between teaching points. 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- Suggested response: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:00-00:15, 00:15-00:30
- Confidence: medium

## Low-Confidence Watchlist

### Deliberately sweep the room

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to monitor next: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:00-00:15
- Confidence: low

### Open the stance between points

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 showed a more guarded arm-and-shoulder position between teaching points. 00:15-00:30 showed a more guarded arm-and-shoulder position between teaching points.
- What to monitor next: Check whether transitions keep the elbows and shoulders open instead of folding inward.
- Review at: 00:00-00:15, 00:15-00:30
- Confidence: medium


## Moment-by-Moment Evidence

### 00:00-00:15 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0000_0015.jpg)

- Observed behavior: low face visibility / uneven room scan / low audience orientation
- Metric evidence: Overall 37.0; room scan 51.0; presence 59.6; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `low`

### 00:45-01:00 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0045_0100.jpg)

- Observed behavior: distributed room engagement / alert room presence
- Metric evidence: Overall 46.6; room scan 76.5; presence 72.1; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `low`

### 00:15-00:30 - Low Audience Orientation

![Evidence frame](coaching_moments/moment_03_0015_0030.jpg)

- Observed behavior: low face visibility / low audience orientation / closed posture
- Metric evidence: Overall 39.5; room scan 60.9; presence 62.3; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: After each board or note check, reset your shoulders and chin back toward the room.

QC confidence: `low`

## Reliability Notes

- Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.
- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Keep the same quick room checks that make the lecture feel attentive.
- Reuse the left-center-right room sweep that already looks natural.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Check whether the next explanation visibly reaches more than one side of the room.
- Check whether transitions keep the elbows and shoulders open instead of folding inward.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 41.6 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 65.8 | moderate |
| Confidence/presence | 65.1 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
