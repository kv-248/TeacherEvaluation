# Runtime Flash Precision Notes

## Ranked findings

### 1. `aligned` is too permissive when semantic and base audience signals differ materially

Evidence:
- In `/workspace/artifacts/nonverbal_eval_long/run_20260318T000201Z/semantic_extensions/semantic_summary.md`, base audience ratio is `0.71` and Gemini semantic audience ratio is `1.00`, yet the agreement label is still `aligned`.
- A gap of `0.29` is too large to present as simple agreement. It reads more like `same direction, stronger semantic claim`.

Recommendation:
- Tighten the agreement label thresholds.
- Reserve `aligned` for small differences only.
- Add an intermediate label such as `semantic_stronger_than_base` or `partial_alignment` for gaps above roughly `0.15-0.20`.
- If the semantic layer is materially stronger than the base proxy, surface that as a reliability note instead of treating it as clean corroboration.

### 2. Hybrid coaching reports are still too confident about posture and facial-tone corrections

Evidence:
- `/workspace/artifacts/nonverbal_eval_long/run_20260318T000201Z/teacher_coaching_report.md` is `llm_api_hybrid`, but its top actions still use `Confidence: high` for `Open the stance between points` and `Soften the visible facial tone`.
- The paired semantic summary does not support those claims directly; it only shows `audience_focus_ratio=1.00`, `static_stance_ratio=0.25`, and no warm/tense affect signal.
- In the moment cards, the Qwen interpretation text says `open-palm explanatory gestures recur; stance is often static`, which is weaker and different from `closed posture` or `tense facial tone`.

Recommendation:
- In `llm_api_hybrid` mode, downshift confidence by one band for corrective actions unless they are supported by both:
  - repeated heuristic evidence across windows, and
  - matching semantic evidence.
- Do not allow a hybrid report to emit `high` confidence for affect or posture corrections when the semantic layer does not explicitly support them.

### 3. `static stance` is being over-read as `closed posture`

Evidence:
- The semantic outputs repeatedly mention `stance is often static`, not closed, guarded, or withdrawn.
- The coaching report still escalates this into `closed posture` in multiple windows.
- That creates a false-positive pathway where low movement or neutral stance becomes a personality-coded posture correction.

Recommendation:
- Separate these concepts in report logic:
  - `static stance`
  - `closed posture`
  - `rigidity`
- Require either semantic confirmation of guarded/closed posture or stronger landmark-based posture evidence before using `closed posture` language.
- If the evidence only supports stillness, phrase it as `more static than needed` rather than `closed`.

### 4. Facial-tone coaching is too eager under neutral-only semantic evidence

Evidence:
- The semantic summaries for the 60-second sample show `warm=0.00` and `tense=0.00`.
- The coaching report still promotes `Soften the visible facial tone` as a top-3 action with `high` confidence.
- That is an unsupported jump from neutral/uncertain affect evidence to a definite facial-tone correction.

Recommendation:
- Affect corrections should require at least one of:
  - explicit semantic `tense` evidence,
  - sustained low-face-quality-aware facial metric evidence across more than one window,
  - or repeated reviewer-confirmed patterns from manual audit.
- If none of those hold, move facial-tone language to `Watch For` instead of `Top 3 Actions`.

### 5. Agreement failure cases need stronger suppression rules

Evidence:
- In `/workspace/artifacts/nonverbal_eval_long/run_20260315T220440Z/semantic_extensions/semantic_summary.md`, the agreement label is `review` with a large audience disagreement (`0.32` vs `0.00`).
- Current report-generation behavior still risks turning weak semantic interpretation into teacher-facing language if hybrid fallback or template logic picks up nearby evidence tags too aggressively.

Recommendation:
- When semantic agreement is `review` or `not_available`, do not let semantic-derived phrasing strengthen a corrective claim.
- In those cases, semantic output should be advisory only and should not promote any action title or confidence band.

## Prompt / threshold / report-logic changes to prioritize

1. Tighten semantic agreement thresholds and labels before changing prose.
2. Add hybrid-mode confidence suppression for posture and affect corrections.
3. Add a hard distinction between `static`, `closed`, and `rigid` in the coaching action-selection logic.
4. Require semantic corroboration or repeated-window evidence before promoting affect corrections into the top action list.
5. Downgrade semantic influence to `watch` mode when agreement is `review` or when semantic output is missing.

## Precision-first default

If the system must choose between under-coaching and over-coaching, it should under-coach on posture/affect claims and keep those items in `Watch For` unless corroboration is explicit.
