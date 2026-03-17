# Prompt Arbitration Notes

## Decision

The winning direction is not either candidate unchanged. The correct merge is:

- use the actionability-first candidate as the base prompt
- import the precision-first candidate's evidence gates, coverage guardrails, and no-forced-correction stance
- pair the prompt merge with a small threshold package so the worker stops manufacturing weak posture, motion, and affect corrections

## Why actionability stays in front

The current reports are already readable, but the review findings show the main teacher-facing failure is that the action is too generic to use. The actionability candidate fixes the right part of the problem:

- it turns actions into next-lecture experiments instead of relabeled metrics
- it makes strengths name repeatable behavior instead of abstract praise
- it handles disagreement between semantic review and metrics explicitly

Those are the changes most likely to move actionability from the current failing level toward the target.

## Why precision still decides issue selection

The baseline artifacts also show that the system is still too willing to invent a top issue:

- the 20-second reports still surfaced a closed-posture correction even though the clip read mostly upright and stable
- the 5-second report still surfaced a facial-tone correction from a moderate low-affect proxy alone
- low-coverage goldset cases remain unsafe for strong affect, gaze, gesture, and posture claims

That means the actionability candidate cannot ship alone. Its cue-to-action bias is useful only after a stronger evidence bar is met. The precision candidate contributes the missing guardrails:

- no priority action from a single weak proxy, transient frame, or short clip
- no neutral-affect problem by default
- no closed-posture story from brief occlusion or one cropped window
- `watch_for` or confidence language when the evidence is mild or coverage is weak

## Key tradeoff

If precision wins completely, the report becomes safer but not clearly more useful to a teacher. If actionability wins completely, the wording improves but the report still overcommits to weak corrections. The merged decision keeps the stronger coaching language while making issue selection meaningfully harder.

That tradeoff is the right one for the teacher-feedback goal: a teacher benefits more from one well-supported experiment or a maintenance verdict than from a polished but weak correction.

## Rejected Pieces

- Reject the precision candidate as a standalone base prompt. It does not do enough to force clip-specific, testable next steps.
- Reject the actionability candidate's affect-first bias as written. It would keep overproducing facial-tone coaching from moderate proxy scores.
- Reject any implementation that still forces at least one correction on short or mostly stable clips.

## Threshold Companion Changes

The prompt merge should ship with threshold changes, not by prompt alone:

- add a short-clip action gate at `30.0s`
- require at least `2` supporting windows for a priority action unless a single-window signal is clearly strong
- require minimum coverage before affect, eye-contact, gesture, or posture actions are allowed
- raise the affect and excessive-animation trigger thresholds so moderate proxy noise stops dominating the teacher-facing report

These changes matter because the reviewed failures were not just wording problems. They were selection problems.

## Worker Note

Maintenance mode must be real. The worker should allow empty `priority_actions` when no issue clears the bar, rather than treating that output as invalid. Without that change, the system will keep reintroducing forced corrections even if the prompt is improved.
