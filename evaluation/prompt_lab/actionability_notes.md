# Actionability Notes

## What This Candidate Optimizes

This prompt candidate keeps the current JSON contract but pushes the model toward concrete, testable coaching advice instead of broad summary language.

## Evidence Used

- The coaching smoke reports are currently falling back to templates, which produces stable but repetitive phrasing like "open the stance between points" and "soften the visible facial tone."
- `summary_full.md` for the long nonverbal example shows a useful mix of strong and weak signals: high excessive-animation risk, moderate closed-posture risk, limited audience orientation, limited eye-contact distribution, and low face coverage.
- `semantic_summary.md` adds a second source of grounding, but it also shows source disagreement on audience orientation. That makes explicit confidence handling important.
- `coaching_prompts.toml` already has a solid schema and a reasonable base tone, but it does not force the model to turn evidence into a next-lecture experiment with a visible cue and success check.

## Main Gaps Addressed

- Generic advice is replaced with behavior-change language.
- Priority actions are required to read as experiments, not diagnoses.
- The prompt now tells the model to choose the best-supported coaching lever when evidence is mixed.
- Confidence handling is made stricter when face or hand coverage is weak.
- Strengths are framed as repeatable behaviors worth preserving, not just praise.

## Why This Should Improve Actionability

- A teacher can act on "after each board check, return shoulders to the room and sweep left-center-right once" more easily than on "improve eye contact."
- A report that says "movement spikes are larger than needed" becomes more useful when it also names the cue, the adjustment, and the observable success criterion.
- When face coverage is weak, the model should not over-interpret facial tone; the prompt now steers it toward posture, room orientation, and movement instead.

## Risks To Watch

- Over-constraining actionability can make the report sound repetitive if the evidence only supports one main lever.
- If the model follows the experiment framing too literally, it may become verbose, so the executive summary remains capped and the field guidance is still concise.
- Low-confidence windows still need restraint; the prompt should prevent the model from inventing a "balanced" report when the clip only supports one solid finding.

## Expected Outcome

- More specific `what_to_try_next` language.
- Better alignment between the visible cue, the metric evidence, and the suggested adjustment.
- Fewer empty or generic strengths.
- Better handling of mixed evidence and visibility limits without losing grounding.
