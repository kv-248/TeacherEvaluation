# Feedback Quality Backlog

Source set reviewed: `run_20260317T213602Z`, `run_20260317T214522Z`, `run_20260317T214817Z`.

## Priority 1: Replace generic coaching with clip-specific insight

- Problem: The reports often restate a label instead of telling the teacher what actually happened and why it matters.
- Evidence: `open the stance between points`, `soften the visible facial tone`, `preserve this delivery pattern`.
- Fix: Require each action to name one observable behavior, one teaching reason, and one next-lecture experiment in plain language.

## Priority 2: Strengths need to be concrete or absent

- Problem: Strengths are abstract titles that do not tell the teacher what to repeat.
- Evidence: `Upright confident presence`, `Alert room presence`, plus report 3 with an empty strengths list.
- Fix: Only surface a strength when it names a repeatable behavior with a cited moment; otherwise say there was no clear stable strength worth calling out.

## Priority 3: Add a real no-issue / maintenance mode

- Problem: Even the most stable-looking report still forces a correction, which makes the feedback feel manufactured.
- Evidence: report 3 has no strengths but still invents a top issue; reports 1 and 2 also reduce the clip to one minor posture fix.
- Fix: Allow the report to say `no major coaching issue` and shift to maintain/watch language when severity is low.

## Priority 4: Remove metric and system leakage from teacher-facing copy

- Problem: The report exposes internal scaffolding that does not help a teacher improve.
- Evidence: `overall=64.1`, `Targeted Qwen interpretation was not run for this window.`
- Fix: Keep raw metrics and pipeline notes in debug fields only; teacher-facing text should stay behavioral and instructional.

## Priority 5: Make confidence handling evidence-aware

- Problem: The only uncertainty note is a generic short-duration caveat, even when the clip is thin on support for affect or room-read claims.
- Evidence: `Short duration limits how confidently the report can generalize beyond this segment.`
- Fix: Mention the specific evidence limit, such as face visibility, brief window length, or ambiguous pose, and downgrade the claim accordingly.
