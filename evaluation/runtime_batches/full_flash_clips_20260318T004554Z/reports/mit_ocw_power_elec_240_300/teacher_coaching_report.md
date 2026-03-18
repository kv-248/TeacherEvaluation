# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_power_elec_240_300/run_20260318T005835Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api_hybrid`
- Report shape: `feedback_first_v1`

## At a Glance

This session shows strong room engagement and an alert presence. Opportunities exist to refine gesture size, soften facial expressions, and maintain an open posture during transitions. Focusing on these areas can enhance overall delivery and approachability.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 2. Soften the visible facial tone

- Why it matters: A more relaxed facial tone can make explanations feel warmer and less guarded.
- What we saw: 00:00-00:15 showed a flatter or tighter visible facial tone than the rest of the clip. 00:15-00:30 showed a flatter or tighter visible facial tone than the rest of the clip.
- What to try next: Reset the face between sentences and let the expression relax before the next point.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 3. Open the stance between points

- Why it matters: A more open posture tends to read as more confident and easier to approach.
- What we saw: 00:30-00:45 showed a more guarded arm-and-shoulder position between teaching points. 00:45-01:00 showed a more guarded arm-and-shoulder position between teaching points.
- What to try next: Let the elbows open slightly and release any folded or guarded arm positions between points.
- Review at: 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### Open-palm explanatory delivery

- Evidence: 00:00-00:15 included open-palm explanatory gestures that supported the explanation.
- What to repeat: Keep the same open-palm gesture shape when emphasizing key ideas.
- Review at: 00:00-00:15
- Confidence: medium

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### Upright confident presence

- Evidence: 00:00-00:15 held an upright, settled stance rather than a collapsed or guarded one.
- What to repeat: Keep the same upright, settled stance between points and transitions.
- Review at: 00:00-00:15
- Confidence: medium


## Moment-by-Moment Evidence

### 00:45-01:00 - Closed Posture

![Evidence frame](coaching_moments/moment_01_0045_0100.jpg)

- Observed behavior: closed posture / over animated delivery / tense or neutral affect
- Metric evidence: Overall 47.6; room scan 71.9; presence 59.1; natural movement 17.3.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Let the elbows open slightly and release any folded or guarded arm positions between points.

QC confidence: `medium`

### 00:00-00:15 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0000_0015.jpg)

- Observed behavior: distributed room engagement / upright confident presence / alert room presence
- Metric evidence: Overall 55.4; room scan 77.3; presence 83.9; natural movement 26.1.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:30-00:45 - Closed Posture

![Evidence frame](coaching_moments/moment_03_0030_0045.jpg)

- Observed behavior: closed posture / over animated delivery / tense or neutral affect
- Metric evidence: Overall 54.7; room scan 88.1; presence 63.8; natural movement 21.0.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Let the elbows open slightly and release any folded or guarded arm positions between points.

QC confidence: `medium`

## Reliability Notes

- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Reuse the left-center-right room sweep that already looks natural.
- Keep the same open-palm gesture shape when emphasizing key ideas.
- Keep the same quick room checks that make the lecture feel attentive.
- Keep the same upright, settled stance between points and transitions.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether the face resets between points instead of staying tight through the whole sentence.
- Check whether transitions keep the elbows and shoulders open instead of folding inward.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 51.9 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 80.9 | strong |
| Confidence/presence | 70.4 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
