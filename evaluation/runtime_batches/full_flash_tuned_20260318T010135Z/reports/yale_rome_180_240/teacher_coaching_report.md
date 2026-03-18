# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_rome_180_240/run_20260318T013337Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

The teacher demonstrates strong presence and alertness. Key areas for growth include refining gesture size to match emphasis and ensuring a more deliberate, even room scan. Additionally, reducing extended note-reading and softening facial tone could enhance connection.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45
- Confidence: medium

### 2. Deliberately sweep the room

- Why it matters: More even attention across the room helps students feel included and keeps engagement distributed.
- What we saw: 00:00-00:15 stayed more fixed on one part of the room than on a left-center-right sweep. 00:15-00:30 stayed more fixed on one part of the room than on a left-center-right sweep.
- What to try next: At each major point, pause and sweep left-center-right before moving on.
- Review at: 00:00-00:15, 00:15-00:30
- Confidence: medium

## Strengths to Preserve

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### Upright confident presence

- Evidence: 00:00-00:15 held an upright, settled stance rather than a collapsed or guarded one. 00:15-00:30 held an upright, settled stance rather than a collapsed or guarded one.
- What to repeat: Keep the same upright, settled stance between points and transitions.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium


## Additional Observation Inventory

### Soften the visible facial tone (watch item)

- Evidence: 00:30-00:45 showed a flatter or tighter visible facial tone than the rest of the clip.
- Suggested response: Check whether the face resets between points instead of staying tight through the whole sentence.
- Review at: 00:30-00:45
- Confidence: medium

### Reduce extended note-reading (watch item)

- Evidence: 00:30-00:45 repeatedly pulled attention down to notes instead of back to the room.
- Suggested response: Check whether note glances stay brief and return to the room within the same teaching beat.
- Review at: 00:30-00:45
- Confidence: medium

## Low-Confidence Watchlist

### Soften the visible facial tone

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:30-00:45 showed a flatter or tighter visible facial tone than the rest of the clip.
- What to monitor next: Check whether the face resets between points instead of staying tight through the whole sentence.
- Review at: 00:30-00:45
- Confidence: medium

### Reduce extended note-reading

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:30-00:45 repeatedly pulled attention down to notes instead of back to the room.
- What to monitor next: Check whether note glances stay brief and return to the room within the same teaching beat.
- Review at: 00:30-00:45
- Confidence: medium


## Moment-by-Moment Evidence

### 00:00-00:15 - Uneven Room Scan

![Evidence frame](coaching_moments/moment_01_0000_0015.jpg)

- Observed behavior: uneven room scan / over animated delivery / open palm explaining
- Metric evidence: Overall 50.6; room scan 50.1; presence 80.5; natural movement 24.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur; stance is often static.
- Coaching implication: At each major point, pause and sweep left-center-right before moving on.

QC confidence: `medium`

### 00:45-01:00 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0045_0100.jpg)

- Observed behavior: upright confident presence / alert room presence / distributed room engagement
- Metric evidence: Overall 64.9; room scan 60.3; presence 90.5; natural movement 61.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:30-00:45 - Note Reading

![Evidence frame](coaching_moments/moment_03_0030_0045.jpg)

- Observed behavior: over animated delivery / tense or neutral affect / note reading
- Metric evidence: Overall 54.3; room scan 66.3; presence 88.1; natural movement 18.4.
- Qwen interpretation: Qwen sees repeated note-reading or notes-focused attention; stance is often static; posture looks closed or slouched in several samples.
- Coaching implication: Raise notes closer to eye level and rehearse short glance-return cycles during key explanations.

QC confidence: `medium`

## Reliability Notes

- ["Hand visibility drops in parts of the clip, so gesture labels are less certain.", "Face coverage dropped below 95%
- audience orientation and facial scores are less stable.", "Hand coverage dropped

## Keep Doing

- Keep the same quick room checks that make the lecture feel attentive.
- Keep the same upright, settled stance between points and transitions.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether the next explanation visibly reaches more than one side of the room.
- Check whether the face resets between points instead of staying tight through the whole sentence.
- Check whether note glances stay brief and return to the room within the same teaching beat.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 55.1 | moderate |
| Natural movement | 30.3 | limited |
| Eye-contact distribution | 63.3 | moderate |
| Confidence/presence | 87.2 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
