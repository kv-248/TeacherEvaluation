# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_brain_300_360/run_20260318T005631Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

The teacher demonstrates strong presence and engagement, maintaining an alert and confident posture while distributing attention across the room. Opportunities exist to enhance expressiveness through more purposeful gestures and a softer facial tone, which could further animate explanations and foster a warmer connection with the audience.

Reliability: medium.

## Top 3 Actions for the Next Lecture

### 1. Add more purposeful gesture emphasis

- Why it matters: Too little movement can flatten emphasis and make key ideas feel less animated.
- What we saw: 00:00-00:15 stayed physically still through explanation beats that could carry more emphasis. 00:15-00:30 stayed physically still through explanation beats that could carry more emphasis.
- What to try next: Choose one or two moments per minute where you deliberately use an open explanatory gesture.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium

### 2. Soften the visible facial tone

- Why it matters: A more relaxed facial tone can make explanations feel warmer and less guarded.
- What we saw: 00:00-00:15 showed a flatter or tighter visible facial tone than the rest of the clip. 00:15-00:30 showed a flatter or tighter visible facial tone than the rest of the clip.
- What to try next: Reset the face between sentences and let the expression relax before the next point.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
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

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:15-00:30 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium


## Moment-by-Moment Evidence

### 00:15-00:30 - Limited Movement

![Evidence frame](coaching_moments/moment_01_0015_0030.jpg)

- Observed behavior: limited movement / tense or neutral affect
- Metric evidence: Overall 58.2; room scan 76.9; presence 89.2; natural movement 34.1.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static; visible affect leans tense; posture looks closed or slouched in several samples.
- Coaching implication: Choose one or two moments per minute where you deliberately use an open explanatory gesture.

QC confidence: `medium`

### 00:45-01:00 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0045_0100.jpg)

- Observed behavior: distributed room engagement / upright confident presence / alert room presence
- Metric evidence: Overall 59.4; room scan 82.1; presence 90.0; natural movement 31.9.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

### 00:30-00:45 - Limited Movement

![Evidence frame](coaching_moments/moment_03_0030_0045.jpg)

- Observed behavior: limited movement / tense or neutral affect / distributed room engagement
- Metric evidence: Overall 58.5; room scan 83.2; presence 88.2; natural movement 35.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; stance is often static.
- Coaching implication: Choose one or two moments per minute where you deliberately use an open explanatory gesture.

QC confidence: `medium`

## Reliability Notes

- Hand visibility drops in parts of the clip, so gesture labels are less certain.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Keep the same quick room checks that make the lecture feel attentive.
- Keep the same upright, settled stance between points and transitions.
- Reuse the left-center-right room sweep that already looks natural.

## Watch For

- Check whether key explanation beats now have one visible gesture cue instead of a static stance.
- Check whether the face resets between points instead of staying tight through the whole sentence.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 59.6 | moderate |
| Natural movement | 36.3 | limited |
| Eye-contact distribution | 79.1 | strong |
| Confidence/presence | 89.4 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
