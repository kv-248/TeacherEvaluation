# Hybrid Goldset Review Rubric v2

## Purpose

This rubric is for rapid manual review of `12` goldset clips with a completeness-first lens. Use it to judge whether the teacher-facing report faithfully represents the visible strengths and issues, without generic filler or overconfident inference.

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

Use the same `1-5` scale for all four dimensions.

| Score | Meaning |
| --- | --- |
| `1` | Poor: clearly incomplete, generic, or misleading |
| `2` | Weak: recurring gaps or shallow representation |
| `3` | Mixed: partly complete, but with noticeable omissions or flattening |
| `4` | Good: mostly complete and specific, with only minor issues |
| `5` | Strong: complete, specific, calibrated, and teacher-useful |

## Dimensions

### 1. Completeness

Question: Does the report cover the meaningful visible strengths and issues that a teacher would need to know?

Score high when:
- all salient visible strengths are represented if they are clearly present
- all salient visible issues are represented if they are clearly present
- the report does not force a correction when `maintenance mode` or `no major issue` is the more honest summary
- distinct observations stay distinct instead of being collapsed into one generic bucket

Score low when:
- visible strengths are omitted
- visible issues are omitted
- the report invents a priority action just to have one
- the report flattens multiple cues into a single vague label

Examples of failure modes:
- empty strengths list despite a visibly stable clip
- one minor fix used as the whole story
- no-issue clip still forced into a correction

### 2. Non-genericness

Question: Are the represented items specific enough to feel like they came from the clip rather than a template?

Score high when:
- each item names an observable cue, not just a trait label
- the wording could not be swapped into any clip without sounding wrong
- the report distinguishes what was seen from the interpretation of what it means
- internal metrics or system notes are kept out of teacher-facing prose

Score low when:
- titles are abstract or label-like
- wording is reusable across almost any clip
- metric strings or pipeline notes leak into the report
- the feedback reads like a paraphrase of the summary rather than a clip reading

Examples of failure modes:
- `Upright confident presence`
- `Alert room presence`
- `overall=64.1`
- `Targeted Qwen interpretation was not run for this window.`

### 3. Confidence Calibration

Question: Does the report match confidence to the actual evidence quality?

Score high when:
- uncertainty is tied to the specific limitation that is visible in the clip
- weakly supported claims are softened or omitted
- observed behavior is separated from inference
- the report does not claim more certainty than the evidence supports

Score low when:
- affect, eye-contact, or room-engagement claims are too certain for the available evidence
- only boilerplate short-duration language is used
- the report treats a partial cue as a fully established conclusion

Examples of failure modes:
- generic short-duration caveat with no evidence-specific explanation
- confident interpretation from ambiguous or partially visible behavior

### 4. Strength Handling

Question: Does the report represent strengths honestly and usefully?

Score high when:
- strengths are concrete, repeatable, and evidence-backed
- strengths are preserved when they are part of the main story
- if no clear strength exists, the report says so instead of inventing one
- strength language is not just a positive-sounding restatement of the summary

Score low when:
- strengths are empty, abstract, or duplicated
- the report misses a clear stable strength
- the report invents positive framing without a visible basis

Examples of failure modes:
- empty `top_strengths` list with no explanation
- strengths that are just labels instead of repeatable behaviors

## Pass / Fail Rule

Mark a clip `pass` only if all of the following are true:
- `completeness >= 4`
- `non_genericness >= 4`
- `confidence_calibration >= 4`
- `strength_handling >= 4`

Otherwise mark it `fail`.

If a clip is borderline, prefer `fail` and explain the main blocker in notes. The goal of the goldset is tuning pressure, not generosity.

## Recommended Review Workflow

1. Read the teacher-facing coaching report first.
2. Check whether the report includes every salient visible strength and issue.
3. Verify whether the items are concrete rather than label-like.
4. Check whether uncertainty is matched to the actual evidence limits.
5. Score the four dimensions.
6. Record pass/fail.
7. Add one short note for the main completeness gap and one short note for the strongest preserved pattern.

Target time per clip: `3-5 minutes`.

## Evidence Tags for Notes

Use short evidence tags in notes where possible so recurring patterns are easy to summarize later.

Suggested tags:
- `missing_strength`
- `missing_issue`
- `forced_issue`
- `maintenance_mode_needed`
- `generic_label`
- `abstract_strength`
- `evidence_specific_caution`
- `boilerplate_confidence`
- `debug_leakage`
- `balanced_coverage`
- `concrete_strength`
- `no_issue_mode`

## Goldset Output Expectation

After all `12` clips are reviewed, summarize:
- which visible strengths were consistently represented well
- which visible issues were consistently omitted or flattened
- where generic phrasing still replaced clip-specific reading
- where confidence was well calibrated versus overclaimed
- which report patterns best preserve completeness without inventing a problem

