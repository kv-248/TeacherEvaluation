# Runtime Flash Actionability Notes

## Main findings

1. The current report repeats the same high-level coaching language across runs without enough clip-specific articulation.
   - Evidence: [run_20260318T000201Z](/workspace/artifacts/nonverbal_eval_long/run_20260318T000201Z/teacher_coaching_report.md) and [run_20260317T235240Z](/workspace/artifacts/nonverbal_eval_long/run_20260317T235240Z/teacher_coaching_report.md) are nearly identical at the action level.
   - Impact: the teacher gets plausible advice, but not enough sense of what is uniquely happening in this clip.
   - Recommendation: require the coaching prompt to explain the *interaction between cues* in each action, not just name the issue. Example pattern: `Because the clip is audience-facing and otherwise strong, the main opportunity is to reduce oversized emphasis gestures rather than change room engagement.`

2. The report still behaves like a `Top 3 only` brief, even though the target product is `Top 3 + full inventory`.
   - Evidence: the reviewed reports include `Top 3 Actions`, `Strengths`, `Moment-by-Moment Evidence`, `Keep Doing`, and `Watch For`, but no explicit `All Additional Observations` section.
   - Impact: smaller but still important issues are either omitted or buried in moment cards, so the teacher cannot distinguish major actions from secondary refinements.
   - Recommendation: add a mandatory `All Additional Observations` block after `Top 3 Actions`. Prompt it as a flat timestamped inventory of lower-priority findings with one-line implications.

3. Strengths are present, but they are not framed strongly enough when the clip is mostly competent.
   - Evidence: the current reports correctly surface `Alert room presence`, `Open-palm explanatory delivery`, and `Distributed room engagement`, but the executive summary still leads with corrections.
   - Impact: a teacher reading the report gets a criticism-first experience, even when the clip mostly shows stable room-facing behavior.
   - Recommendation: change the summary prompt so that when overall engagement is strong and reliability is high, the first sentence must name the strongest stable behavior before any correction.

4. The semantic layer is helping, but the report underuses it.
   - Evidence: [semantic_summary.md](/workspace/artifacts/nonverbal_eval_long/run_20260318T000201Z/semantic_extensions/semantic_summary.md) shows `audience_focus_ratio=1.00` and recurring `open_palm_explaining`, yet the actions do not fully leverage that framing.
   - Impact: the teacher hears generic posture/gesture advice instead of more useful contextual advice such as “keep the audience-facing explanation style, but tighten the size of emphasis gestures.”
   - Recommendation: add a prompt rule that every priority action must mention whether the semantic layer supports, complicates, or weakens the base-metric reading.

5. The `Watch For` section is useful, but it is too detached from the main report logic.
   - Evidence: current `Watch For` items are good short checks, but they are not clearly tied to why they were demoted out of the top actions.
   - Impact: the teacher cannot tell whether these are minor issues, low-confidence issues, or just future reminders.
   - Recommendation: split this into:
     - `Additional Observations` for evidence-backed but lower-priority issues
     - `Low-Confidence Watchlist` for weak or uncertain issues only

## Prompt/report changes to make next

1. Make the executive summary structure deterministic:
   - sentence 1: strongest visible teaching strength
   - sentence 2: main coaching opportunity
   - sentence 3: why that opportunity matters in this specific clip

2. Require each `Top 3 Action` to include one clip-specific contrast:
   - what is already working
   - what should change
   - why the change is a refinement, not a wholesale correction

3. Add a required `All Additional Observations` array to the coaching output schema.
   - each item should contain:
   - `title`
   - `timestamps`
   - `short implication`
   - `confidence`

4. Add a prompt rule that strengths must be explicit when no major intervention is needed.
   - if the evidence is mostly strong, the model should say `this is primarily a refinement report` rather than producing criticism-first language.

5. Tighten the semantic-to-coaching bridge.
   - when semantic output is strongly audience-facing and explanatory, default posture/gesture language should be framed as refinement of delivery, not as a broad communication problem.

## Report-logic changes worth allowing

1. Add a `report posture` mode:
   - `correction_first`
   - `refinement_first`
   - `strengths_first`
   - derive it from overall score, reliability, and severity of detected issues.

2. Promote strengths higher when:
   - audience orientation is strong
   - semantic audience focus is high
   - no high-severity risk dominates the window set

3. Prevent moment cards from being the only place where secondary observations live.
   - moment cards should support the report, not replace the missing inventory section.

## Priority order

1. Add `All Additional Observations` plus `Low-Confidence Watchlist` separation.
2. Rewrite the executive-summary prompt to be strength-first on mostly good clips.
3. Force each top action to reference how semantic evidence changes the interpretation.
4. Add refinement-first language when the clip is strong overall and only needs tuning.
