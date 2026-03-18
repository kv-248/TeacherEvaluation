# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_how_to_speak_300_360/run_20260318T010546Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

This session shows strong room presence and distributed engagement. Consider refining gesture size to match emphasis and ensure a quicker return to audience-facing orientation after board checks. Overall, the teaching is effective, with minor adjustments suggested for even greater impact.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45
- Confidence: medium

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium


## Additional Observation Inventory

### Turn back toward the audience sooner (watch item)

- Evidence: 00:00-00:15 spent longer than needed turned away from the audience after checks.
- Suggested response: Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Review at: 00:00-00:15
- Confidence: low

## Low-Confidence Watchlist

### Turn back toward the audience sooner

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:00-00:15 spent longer than needed turned away from the audience after checks.
- What to monitor next: Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Review at: 00:00-00:15
- Confidence: low


## Moment-by-Moment Evidence

### 00:30-00:45 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_01_0030_0045.jpg)

- Observed behavior: low face visibility / over animated delivery / open palm explaining
- Metric evidence: Overall 43.4; room scan 77.2; presence 69.6; natural movement 15.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur; stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `low`

### 00:15-00:30 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0015_0030.jpg)

- Observed behavior: distributed room engagement / alert room presence
- Metric evidence: Overall 57.0; room scan 84.6; presence 82.6; natural movement 26.0.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:00-00:15 - Low Audience Orientation

![Evidence frame](coaching_moments/moment_03_0000_0015.jpg)

- Observed behavior: low face visibility / low audience orientation / over animated delivery
- Metric evidence: Overall 45.8; room scan 72.7; presence 70.8; natural movement 15.8.
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

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 49.6 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 81.1 | strong |
| Confidence/presence | 74.7 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
