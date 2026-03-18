# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_deconstruction_180_240/run_20260318T012158Z/full_segment_reference.mp4`
- Analyzed duration: `60.00s`
- Window count: `4`
- Report mode: `llm_api`
- Report shape: `feedback_first_v1`

## At a Glance

The instructor demonstrates strong room presence and engagement, effectively using open-palm gestures. Opportunities exist to refine gesture size for emphasis and to ensure quicker re-orientation towards the audience after board or note checks.

Reliability: high.

## Top 3 Actions for the Next Lecture

### 1. Tighten the peak size of gestures

- Why it matters: Large bursts of motion can distract from the teaching point when they are not tightly timed.
- What we saw: 00:00-00:15 had gesture peaks that looked larger than the teaching point required. 00:15-00:30 had gesture peaks that looked larger than the teaching point required.
- What to try next: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: high

## Strengths to Preserve

### Open-palm explanatory delivery

- Evidence: 00:45-01:00 included open-palm explanatory gestures that supported the explanation.
- What to repeat: Keep the same open-palm gesture shape when emphasizing key ideas.
- Review at: 00:45-01:00
- Confidence: medium

### Alert room presence

- Evidence: 00:00-00:15 kept the head and eyes visibly engaged with the room. 00:15-00:30 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: high

### Distributed room engagement

- Evidence: 00:00-00:15 showed attention moving across more than one part of the room. 00:30-00:45 showed attention moving across more than one part of the room.
- What to repeat: Reuse the left-center-right room sweep that already looks natural.
- Review at: 00:00-00:15, 00:30-00:45, 00:45-01:00
- Confidence: high

## Low-Confidence Watchlist

### Turn back toward the audience sooner

- Why it stays on the watchlist: The signal is visible, but it is not yet sustained enough to justify real corrective feedback.
- What we saw: 00:15-00:30 spent longer than needed turned away from the audience after checks.
- What to monitor next: Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.
- Review at: 00:15-00:30
- Confidence: medium


## Moment-by-Moment Evidence

### 00:30-00:45 - Over Animated Delivery

![Evidence frame](coaching_moments/moment_01_0030_0045.jpg)

- Observed behavior: over animated delivery / open palm explaining / distributed room engagement
- Metric evidence: Overall 53.8; room scan 79.1; presence 75.7; natural movement 28.8.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur; stance is often static.
- Coaching implication: Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.

QC confidence: `high`

### 00:45-01:00 - Distributed Room Engagement

![Evidence frame](coaching_moments/moment_02_0045_0100.jpg)

- Observed behavior: distributed room engagement / upright confident presence / alert room presence
- Metric evidence: Overall 58.6; room scan 71.8; presence 76.4; natural movement 31.3.
- Qwen interpretation: Qwen sees the teacher mainly addressing the audience; open-palm explanatory gestures recur.
- Coaching implication: Reuse the left-center-right room sweep that already looks natural.

QC confidence: `medium`

## Reliability Notes

- Tracking quality is stable enough for formative review, but the outputs remain heuristic proxies rather than direct teaching-quality measures.

## Keep Doing

- Keep the same open-palm gesture shape when emphasizing key ideas.
- Keep the same quick room checks that make the lecture feel attentive.
- Reuse the left-center-right room sweep that already looks natural.
- Keep the same upright, settled stance between points and transitions.

## Watch For

- Check whether gesture size matches the importance of the point instead of peaking on routine lines.
- Check whether board or note checks end with a quick shoulder-and-chin reset back to the room.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 57.3 | moderate |
| Natural movement | 26.1 | limited |
| Eye-contact distribution | 74.3 | moderate |
| Confidence/presence | 77.1 | strong |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
