# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_cs230_240_300/run_20260318T011500Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

This session shows good distributed room engagement. Focus on tightening gesture size to avoid distraction and increasing room-checking behavior for better responsiveness. Also, consider softening your facial tone and ensuring a deliberate room sweep to include all students.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 2. Increase room-checking behavior

- Why it matters: Alert room-facing behavior helps the lecture feel more responsive and attentive.
- What we saw: 00:00-00:15 showed fewer quick room checks and a less visibly alert scan. 00:15-00:30 showed fewer quick room checks and a less visibly alert scan.
- What to try next: Build in quick audience checks after transitions instead of staying fixed on notes or a single spot.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45
- Confidence: medium


## Additional Observation Inventory

### Soften the visible facial tone (watch item)

- Evidence: 00:00-00:15 showed a flatter or tighter visible facial tone than the rest of the clip.
- Suggested response: Check whether the face resets between points instead of staying tight through the whole sentence.
- Review at: 00:00-00:15
- Confidence: medium

### Deliberately sweep the room (watch item)

- Evidence: 00:45-01:00 stayed more fixed on one part of the room than on a left-center-right sweep.
- Suggested response: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:45-01:00
- Confidence: medium

## Low-Confidence Watchlist

### Soften the visible facial tone

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 showed a flatter or tighter visible facial tone than the rest of the clip.
- What to monitor next: Check whether the face resets between points instead of staying tight through the whole sentence.
- Review at: 00:00-00:15
- Confidence: medium

### Deliberately sweep the room

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:45-01:00 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to monitor next: Check whether the next explanation visibly reaches more than one side of the room.
- Review at: 00:45-01:00
- Confidence: medium


## Moment-by-Moment Evidence

### 00:45-01:00 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0045_0100.jpg)

- Observed behavior: low face visibility / uneven room scan / over animated delivery
- Metric evidence: Overall 43.1; room scan 54.1; presence 68.4; natural movement 22.0.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `medium`

### 00:30-00:45 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0030_0045.jpg)

- Observed behavior: distributed room engagement
- Metric evidence: Overall 52.5; room scan 78.0; presence 80.5; natural movement 24.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `low`

### 00:15-00:30 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_03_0015_0030.jpg)

- Observed behavior: low face visibility / over animated delivery / reduced alertness
- Metric evidence: Overall 47.6; room scan 79.6; presence 73.2; natural movement 19.4.
- Qwen interpretation: Qwen sees the teacher mainly oriented to board or screen content.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `low`

## Reliability Notes

- Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Reuse the left-center-right room sweep that already looks natural.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether transitions now include a visible room check before the next explanation.
- Check whether the face resets between points instead of staying tight through the whole sentence.
- Check whether the next explanation visibly reaches more than one side of the room.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 47.0 | limited |
| Natural movement | 16.3 | limited |
| Eye-contact distribution | 75.4 | strong |
| Confidence/presence | 74.5 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
