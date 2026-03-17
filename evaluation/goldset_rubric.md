# Hybrid Goldset Review Rubric

## Purpose

This rubric is for rapid manual review of `12` goldset clips. It is intentionally lightweight so one reviewer can score a clip in a few minutes and surface failures that are useful for prompt, threshold, and coaching-report iteration.

Use this rubric to judge the teacher-facing output, not just the raw metric table. Review the generated coaching report, supporting timestamps, and any linked debug visuals when needed.

## Review Unit

One review row corresponds to one analyzed `60 s` clip sampled at `12 fps`.

Recommended review inputs per clip:
- `teacher_coaching_report.md` or `teacher_coaching_report.pdf`
- `summary_full.md`
- `window_summary.md`
- `semantic_summary.md` if present
- debug overlay or contact sheet only when a claim looks questionable

## Scoring Scale

Use the same `1-5` scale for all five dimensions.

| Score | Meaning |
| --- | --- |
| `1` | Poor: clearly wrong or not useful |
| `2` | Weak: recurring issues, limited usefulness |
| `3` | Mixed: partly correct/useful, but needs revision |
| `4` | Good: mostly correct/useful, minor issues only |
| `5` | Strong: clear, grounded, and directly useful |

## Dimensions

### 1. Correctness

Question: Do the reported observations broadly match what is visible in the clip?

Score high when:
- the report describes the dominant visible behavior correctly
- major strengths and issues are visually defensible
- the report does not overclaim from weak evidence

Score low when:
- the report misreads the clip
- it labels the wrong dominant issue
- it confuses uncertainty with certainty

Examples of failure modes:
- calls a note-reading segment an eye-contact problem without acknowledging low face visibility
- flags excessive animation when gestures look controlled
- claims positive affect with too little frontal-face evidence

### 2. Actionability

Question: Does the report tell the teacher what to do next in a practical way?

Score high when:
- actions are specific and testable in the next lecture
- advice is phrased as an instructional adjustment, not a generic judgment
- the teacher can understand what to keep, change, or inspect

Score low when:
- feedback is only metric restatement
- advice is vague, generic, or moralizing
- the teacher would not know what to try next

### 3. Timestamp Usefulness

Question: Are timestamps specific enough to help the teacher inspect the relevant moments?

Score high when:
- actions and strengths cite concrete moments or short windows
- timestamps align with the described behavior
- the teacher can jump to the cited segment and verify it quickly

Score low when:
- timestamps are missing
- timestamps are too broad to be useful
- cited moments do not match the recommendation

### 4. Tone

Question: Is the feedback respectful, coach-like, and suitable for teacher reflection?

Score high when:
- wording is direct but not harsh
- the report avoids labeling the teacher as good/bad
- strengths and watch-items are balanced appropriately

Score low when:
- tone is overly negative, robotic, or patronizing
- the report sounds like a score dump
- wording is too absolute for the available evidence

### 5. Confidence Handling

Question: Does the report communicate uncertainty appropriately when evidence quality is weak?

Score high when:
- low face/hand visibility is reflected in the wording
- uncertain claims are softened or marked for review
- the report distinguishes observed behavior from inference

Score low when:
- uncertain cues are reported as facts
- low-coverage clips still get confident affect/eye-contact claims
- the report ignores evidence quality warnings

## Pass / Fail Rule

Mark a clip `pass` only if all of the following are true:
- `correctness >= 4`
- `actionability >= 4`
- `timestamp_usefulness >= 4`
- `tone >= 3`
- `confidence_handling >= 4`

Otherwise mark it `fail`.

If a clip is borderline, prefer `fail` and explain the main blocker in notes. The goal of the goldset is tuning pressure, not generosity.

## Recommended Review Workflow

1. Read the teacher-facing coaching report first.
2. Check whether the top actions match the clip at a glance.
3. Verify cited timestamps against the clip or debug assets.
4. Score the five dimensions.
5. Record pass/fail.
6. Add one short note for the main strength and one short note for the main failure mode.

Target time per clip: `3-5 minutes`.

## Evidence Tags for Notes

Use short evidence tags in notes where possible so recurring patterns are easy to summarize later.

Suggested tags:
- `note_reading`
- `low_face_visibility`
- `overstated_affect`
- `eye_contact_overclaim`
- `gesture_penalty_too_harsh`
- `good_timestamp_grounding`
- `actionable_next_step`
- `too_generic`
- `tone_too_harsh`
- `uncertainty_handled_well`
- `manual_review_needed`

## Goldset Output Expectation

After all `12` clips are reviewed, summarize:
- top recurring failure modes
- strongest report patterns to preserve
- categories most in need of threshold tuning
- categories most in need of prompt/coaching rewrite
