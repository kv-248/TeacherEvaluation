# Conductor Backlog

## Parallelization Backlog

- Keep the repo-local config set for four-way conductor fan-out so the dataset review, prompt debate, feedback-quality review, and frontend QA lanes can stay independent.
- Keep `prompt_advocate_precision` and `prompt_advocate_actionability` separate until `prompt_arbiter` has a chance to reconcile the tradeoff.
- Keep `feedback_quality_critic` and `feedback_completeness_reviewer` separate so severity and coverage do not get blended into one pass.
- Add a clear lane-handoff note for the conductor so recurring issues land in one backlog instead of being rediscovered in later waves.
- Re-run frontend QA as a dedicated smoke lane after any app-service or Streamlit change, rather than folding it into report tuning.

## Feedback-Quality Backlog

- Remove generic coaching phrases from teacher-facing copy. The current review round flagged lines like `open the stance between points`, `Upright confident presence`, and `Preserve this delivery pattern` as too abstract.
- Add a real no-issue or maintenance-only mode so stable clips do not force a correction.
- Require concrete strengths and concrete actions in the same report. Empty or abstract strengths are still showing up.
- Suppress metric leakage and internal system notes from teacher-facing prose, including raw score fragments and debug references.
- Tighten uncertainty language when face, hand, or affect evidence is weak so confidence claims match actual visibility.
