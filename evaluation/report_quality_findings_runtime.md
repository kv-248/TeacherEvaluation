# Runtime Report Quality Findings

Primary evidence reviewed:

- `/workspace/artifacts/nonverbal_eval_long/run_20260318T000201Z/teacher_coaching_report.md`
- `/workspace/artifacts/nonverbal_eval_long/run_20260317T235240Z/teacher_coaching_report.md`
- `/workspace/tmp/final_wave_smoke/run_20260317T223333Z/teacher_coaching_report.md`
- `/workspace/artifacts/nonverbal_eval_long/run_20260315T220440Z/summary_full.md`

## Ranked Defects

1. The report still over-promotes posture and facial-tone corrections as high-confidence actions.
   In the 60 s hybrid reports, `Open the stance between points` and `Soften the visible facial tone` are presented as strong interventions even though the supporting evidence is mostly heuristic and only moderately specific. The low-face-coverage clip summary at `run_20260315T220440Z` shows exactly why this is risky: face-based conclusions become unstable quickly, yet the teacher-facing layer still tends to package them as confident coaching.

2. The semantic layer is not changing the teacher-facing advice enough.
   The Gemini/Qwen interpretation says the teacher is audience-facing and uses open-palm explanatory gestures, but the main coaching actions remain almost identical to the fallback template. The semantic layer is helping the strengths section slightly, but it is not yet materially suppressing weak corrections or generating more clip-specific advice.

3. The top actions are too generic and too stable across runs.
   The two 60 s reports are nearly identical in structure and wording. That is a sign that the coaching layer is still dominated by template logic rather than by the actual clip evidence. A teacher reading repeated reports like this will learn the house style, not the specific behavior to change.

4. The report still compresses repeated evidence into broad advice instead of a usable next-step experiment.
   `Tighten the peak size of gestures` is directionally plausible, but it is phrased as a general reminder rather than a concrete experiment tied to the moments where the signal appears. The current output tells the teacher what was wrong, but not how to rehearse or test a better behavior in the next lecture.

5. The no-intervention path is better than before, but still not strict enough.
   The 5 s smoke report correctly avoids full corrective actions, yet it still surfaces a facial-tone watch item from a very short clip. That means the suppression policy is improved but not yet conservative enough for short or low-confidence spans.

6. Strengths are useful, but they are not yet organized as a maintenance plan.
   The strengths section already captures room engagement and open-palm delivery, but it reads like praise rather than a reusable coaching plan. When a clip is good, the report should lean harder into what to preserve intentionally, not only what to fix.

7. Hybrid mode is operationally useful but not transparent enough.
   `llm_api_hybrid` is better than dropping back to a full template, but the teacher-facing report does not explain which sections came from the model and which were preserved from deterministic fallback logic. That makes calibration harder during review and tuning.

## Immediate Backlog

- Add hard promotion gates for posture and facial actions.
  Require multi-window support plus quality-control thresholds before these can appear in `Top 3 Actions`. Otherwise demote them to `Watch For` or low-confidence inventory.

- Make semantic evidence able to suppress weak corrections.
  If the semantic layer strongly supports `audience-facing`, `open-palm explaining`, or another positive cue, it should block unrelated high-confidence corrections unless there is strong counter-evidence.

- Convert corrective actions into rehearsal-style next steps.
  Replace generic phrasing with one behavior, one cue, and one next-lecture experiment. The teacher should be able to try the recommendation immediately.

- Increase report variance based on real clip evidence.
  The coaching brief should not default to the same three interventions across moderate clips. Add stronger tie-breaking and suppression logic so different evidence patterns actually produce different advice.

- Tighten short-clip and low-face-coverage demotion rules.
  For very short clips or clips with unstable face evidence, default to strengths plus watch items rather than corrective actions.

- Surface strengths as a maintenance plan.
  When a clip is strong or mixed-positive, rewrite the strengths section so it reads as `keep doing these three things deliberately`, not just `these looked good`.

- Expose hybrid provenance for manual reviewers.
  Add a small provenance note in the technical appendix or reliability section indicating whether actions/strengths came from deterministic fallback, semantic support, or model-authored synthesis.
