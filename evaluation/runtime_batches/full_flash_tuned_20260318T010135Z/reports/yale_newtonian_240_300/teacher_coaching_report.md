# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_newtonian_240_300/run_20260318T012824Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

This session shows strong room presence and distributed engagement. Consider refining gesture size to match emphasis and softening facial tone for a warmer delivery. These adjustments can enhance clarity and approachability, building on your existing strengths in maintaining audience connection.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:45-01:00
- Confidence: high

### 2. Soften the visible facial tone

- Why it matters: A more relaxed facial tone can make explanations feel warmer and less guarded.
- What we saw: 00:00-00:15 showed a flatter or tighter visible facial tone than the rest of the clip. 00:45-01:00 showed a flatter or tighter visible facial tone than the rest of the clip.
- What to try next: Reset the face between sentences and let the expression relax before the next point.
- Review at: 00:00-00:15, 00:45-01:00
- Confidence: high

## Strengths to Preserve

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: high

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:45-01:00
- Confidence: high


## Moment-by-Moment Evidence

### 00:15-00:30 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_01_0015_0030.jpg)

- Observed behavior: low face visibility / over animated delivery
- Metric evidence: Overall 51.0; room scan 70.4; presence 70.8; natural movement 28.1.
- Qwen interpretation: stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

### 00:30-00:45 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0030_0045.jpg)

- Observed behavior: alert room presence / distributed room engagement
- Metric evidence: Overall 59.6; room scan 65.3; presence 78.8; natural movement 51.6.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:00-00:15 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_03_0000_0015.jpg)

- Observed behavior: over animated delivery / tense or neutral affect / open palm explaining
- Metric evidence: Overall 55.9; room scan 82.3; presence 84.5; natural movement 25.4.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

## Reliability Notes

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.

## Keep Doing

- Keep the same quick room checks that make the lecture feel attentive.
- Reuse the left-center-right room sweep that already looks natural.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether the face resets between points instead of staying tight through the whole sentence.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 54.1 | limited |
| Natural movement | 23.2 | limited |
| Eye-contact distribution | 80.7 | strong |
| Confidence/presence | 78.0 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
