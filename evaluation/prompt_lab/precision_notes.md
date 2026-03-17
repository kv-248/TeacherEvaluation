# Precision Notes

This prompt candidate is designed to reduce false-positive coaching claims by requiring stronger evidence before it upgrades a proxy signal into a recommendation.

## Observed failure modes

- Short clips were still producing confident posture or affect actions. In the 20-second and 5-second lecture runs, the reports promoted a single action even though the visible frames were mostly upright and settled and the report had no targeted Qwen corroboration.
- Low-coverage clips invite unstable face, eye-contact, and gesture claims. The goldset examples with face coverage below `0.55` and hand coverage below `0.40` were especially vulnerable to overconfident interpretation.
- High motion-risk scores can dominate the narrative even when the visual evidence is only mildly animated. The prompt needs to treat motion risk as a prompt for caution, not as proof of a coaching problem.

## Design choices

- Require at least two aligned cues, or one cue that is visibly obvious across the clip, before emitting a priority action.
- Treat short duration and medium reliability as explicit uncertainty gates, not as background metadata.
- Keep neutral affect out of the problem list unless there is direct visual support.
- Avoid turning brief hand position changes or one cropped window into a closed-posture claim.
- Prefer `watch_for` and `confidence_notes` when coverage is low or cue separation is ambiguous.

## Evidence base used

- `/workspace/tmp/test_coaching_smoke/run_20260317T213602Z/teacher_coaching_report.json`
- `/workspace/tmp/test_wave2_config/run_20260317T214522Z/teacher_coaching_report.json`
- `/workspace/tmp/test_post_protobuf_fix/run_20260317T214817Z/teacher_coaching_report.json`
- `/workspace/TeacherEvaluation/evaluation/local_data/batches/goldset_seed_batch/batch_results.csv`
- `/workspace/TeacherEvaluation/evaluation/local_data/batches/local_seed_batch/batch_results.csv`
- `/workspace/TeacherEvaluation/evaluation/local_data/runs_goldset_seed/clip_004/run_20260317T215943Z/summary_full.md`
- `/workspace/TeacherEvaluation/evaluation/local_data/runs_goldset_seed/clip_005/run_20260317T220007Z/summary_full.md`
- `/workspace/TeacherEvaluation/evaluation/local_data/runs_local/cs50_business_150_210/run_20260317T215132Z/summary_full.md`
- `/workspace/TeacherEvaluation/evaluation/local_data/runs_local/mit_ocw_how_to_speak_300_360/run_20260317T215520Z/summary_full.md`
- `/workspace/TeacherEvaluation/evaluation/local_data/runs_local/mit_ocw_aero_300_360/run_20260317T215251Z/summary_full.md`

## Intended effect

- Reduce posture and affect false positives.
- Preserve the useful parts of the current report structure.
- Keep the report actionable, but only when the evidence is strong enough to justify a recommendation.
