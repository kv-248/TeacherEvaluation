# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_give_lecture_180_240/run_20260318T011624Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

The instructor demonstrates strong room engagement and a confident, alert presence. However, there's a tendency for gestures to be larger than necessary, which could be distracting. Focusing on more controlled movements will enhance clarity and impact.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

## Strengths to Preserve

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### Upright confident presence

- Evidence: 00:00-00:15 held an upright, settled stance rather than a collapsed or guarded one. 00:15-00:30 held an upright, settled stance rather than a collapsed or guarded one.
- What to repeat: Keep the same upright, settled stance between points and transitions.
- Review at: 00:00-00:15, 00:15-00:30
- Confidence: medium


## Moment-by-Moment Evidence

### 00:45-01:00 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_01_0045_0100.jpg)

- Observed behavior: over animated delivery / distributed room engagement
- Metric evidence: Overall 59.5; room scan 85.9; presence 81.4; natural movement 39.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

### 00:15-00:30 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0015_0030.jpg)

- Observed behavior: distributed room engagement / upright confident presence / alert room presence
- Metric evidence: Overall 66.3; room scan 93.0; presence 91.8; natural movement 37.0.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:00-00:15 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_03_0000_0015.jpg)

- Observed behavior: over animated delivery / distributed room engagement
- Metric evidence: Overall 65.6; room scan 82.6; presence 90.1; natural movement 43.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

### 00:30-00:45 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_04_0030_0045.jpg)

- Observed behavior: over animated delivery / open palm explaining / distributed room engagement
- Metric evidence: Overall 60.2; room scan 94.2; presence 85.5; natural movement 23.5.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur; stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `medium`

## Reliability Notes

- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Reuse the left-center-right room sweep that already looks natural.
- Keep the same quick room checks that make the lecture feel attentive.
- Keep the same upright, settled stance between points and transitions.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 60.9 | moderate |
| Natural movement | 24.1 | limited |
| Eye-contact distribution | 90.3 | strong |
| Confidence/presence | 87.2 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
