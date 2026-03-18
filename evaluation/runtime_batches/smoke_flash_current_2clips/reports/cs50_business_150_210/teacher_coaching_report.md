# Teacher Coaching Brief

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/cs50_business_150_210/run_20260318T003242Z/full_segment_reference.mp4`
- Analyzed duration: `59.92s`
- Window count: `4`
- Report mode: `template_fallback`
- Report shape: `feedback_first_v1`

## At a Glance

some motion spikes may be larger than needed. Best visible window: 00:15-00:30. Highest-priority adjustment: tighten the peak size of gestures.

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
- What we saw: 00:00-00:15 showed a more guarded arm-and-shoulder position between teaching points. 00:30-00:45 showed a more guarded arm-and-shoulder position between teaching points.
- What to try next: Let the elbows open slightly and release any folded or guarded arm positions between points.
- Review at: 00:00-00:15, 00:30-00:45
- Confidence: medium

## Strengths to Preserve

### Alert room presence

- Evidence: 00:15-00:30 kept the head and eyes visibly engaged with the room. 00:30-00:45 kept the head and eyes visibly engaged with the room.
- What to repeat: Keep the same quick room checks that make the lecture feel attentive.
- Review at: 00:15-00:30, 00:30-00:45
- Confidence: medium


## Additional Observation Inventory

### Turn back toward the audience sooner (action opportunity)

- Evidence: 00:00-00:15 spent longer than needed turned away from the audience after checks. 00:15-00:30 spent longer than needed turned away from the audience after checks.
- Suggested response: After each board or note check, reset your shoulders and chin back toward the room.
- Review at: 00:00-00:15, 00:15-00:30, 00:30-00:45, 00:45-01:00
- Confidence: medium


## Moment-by-Moment Evidence

### 00:00-00:15 - Low Audience Orientation

![Evidence frame](coaching_moments/moment_01_0000_0015.jpg)

- Observed behavior: low audience orientation / closed posture / over animated delivery
- Metric evidence: Overall 43.1; room scan 64.3; presence 52.5; natural movement 15.8.
- Qwen interpretation: Gemini semantic inference failed: RuntimeError: Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY.
- Coaching implication: After each board or note check, reset your shoulders and chin back toward the room.

QC confidence: `medium`

### 00:15-00:30 - Alert Room Presence

![Evidence frame](coaching_moments/moment_02_0015_0030.jpg)

- Observed behavior: alert room presence
- Metric evidence: Overall 47.6; room scan 67.2; presence 73.3; natural movement 15.8.
- Qwen interpretation: Gemini semantic inference failed: RuntimeError: Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY.
- Coaching implication: Keep the same quick room checks that make the lecture feel attentive.

QC confidence: `low`

### 00:45-01:00 - Low Audience Orientation

![Evidence frame](coaching_moments/moment_03_0045_0100.jpg)

- Observed behavior: low face visibility / low audience orientation / over animated delivery
- Metric evidence: Overall 45.9; room scan 67.4; presence 68.5; natural movement 15.8.
- Qwen interpretation: Gemini semantic inference failed: RuntimeError: Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY.
- Coaching implication: After each board or note check, reset your shoulders and chin back toward the room.

QC confidence: `low`

## Reliability Notes

- Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Keep Doing

- Keep the same quick room checks that make the lecture feel attentive.

## Technical Appendix

| Metric | Value | Band |
| --- | --- | --- |
| Overall score | 46.6 | limited |
| Natural movement | 15.8 | limited |
| Eye-contact distribution | 68.2 | moderate |
| Confidence/presence | 68.5 | moderate |

- Raw metric summary: `summary_full.md`
- Window summary: `window_summary.md`
- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run
- Coaching evidence JSON: `coaching_evidence.json`
