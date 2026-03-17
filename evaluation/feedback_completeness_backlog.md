# Feedback Completeness Backlog

Source set reviewed: `run_20260317T213602Z`, `run_20260317T214522Z`, `run_20260317T214817Z`.

## Priority 1: Represent the full visible story, not just one correction

- Problem: The reports usually surface one correction even when the clip also contains visible strengths, and in one case they surface a correction even though the strengths list is empty.
- Evidence: `Upright confident presence`, `Alert room presence`, and the empty `top_strengths` list in report 3.
- Fix: Require the teacher-facing report to include every salient visible strength and issue that would matter to a teacher, or explicitly say there is no clear strength / no major issue worth calling out.

## Priority 2: Stop flattening observations into abstract labels

- Problem: The report names the general category of a behavior, but not the concrete visual cue that made it matter.
- Evidence: `Upright confident presence`, `Alert room presence`, `Open the stance between points`, `Soften the visible facial tone`.
- Fix: Each visible strength or issue should name the actual cue, the window where it was seen, and the practical meaning for the next lesson.

## Priority 3: Add a real maintenance / no-issue mode

- Problem: The current reports still force a fix even when the clip appears mostly stable, which makes the output feel incomplete rather than selective.
- Evidence: report 3 has no strengths but still chooses `Soften the visible facial tone`; reports 1 and 2 reduce a mostly stable clip to a single posture adjustment.
- Fix: Allow the report to say `no major coaching issue` or `maintenance mode` when that is the best summary, and use watch-for language instead of inventing a priority action.

## Priority 4: Calibrate uncertainty to the actual evidence gap

- Problem: The reports use a generic duration caveat, but do not say what specifically limits confidence in the visible reading.
- Evidence: `Short duration limits how confidently the report can generalize beyond this segment.`
- Fix: Tie confidence notes to the real limitation: face visibility, angle, brief window length, conflicting cues, or an observation that is only partially supported.

## Priority 5: Keep teacher-facing copy free of internal scaffolding

- Problem: The report leaks debug-level phrasing that does not help a teacher understand what to repeat or change.
- Evidence: `overall=64.1`, `Targeted Qwen interpretation was not run for this window.`
- Fix: Keep metrics, model notes, and pipeline status out of the teacher-facing narrative so the visible strengths and issues remain clear.

