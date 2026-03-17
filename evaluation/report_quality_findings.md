# Goldset Review Findings

## Review Round

- Round ID: `2026-03-17-teacher-report-quality`
- Reviewer: `feedback_quality_critic`
- Date: `2026-03-17`
- Model / prompt config under review: `template_fallback` outputs from `run_20260317T213602Z`, `run_20260317T214522Z`, `run_20260317T214817Z`
- Threshold config under review: not provided in the inspected artifacts
- Clips reviewed: `3`
- Pass count: `0`
- Fail count: `3`

## Snapshot

| Dimension | Avg score | Main issue if below target |
| --- | --- | --- |
| Correctness | `3.0` | The visible behaviors are plausible, but the insight stays too generic to feel meaningfully grounded. |
| Actionability | `2.0` | Actions are vague and often read like renamed labels rather than instructions a teacher can test. |
| Timestamp usefulness | `3.0` | The windows are concrete, but the cited behavior is too broad to inspect quickly. |
| Tone | `4.0` | Respectful and coach-like, without obvious judgment language. |
| Confidence handling | `2.0` | Uncertainty is handled with boilerplate, not with evidence-specific caution. |

Targets for rapid iteration:
- correctness: `>= 3.5`
- actionability: `>= 4.0`
- timestamp usefulness: `>= 4.0`
- tone: `>= 3.5`
- confidence handling: `>= 4.0`

## Recurring Failure Modes

| Failure mode | Clips affected | What it looked like | Likely source | Suggested owner |
| --- | --- | --- | --- | --- |
| Generic coaching instead of clip-specific insight | `3` | `open the stance between points`, `soften the visible facial tone`, `preserve this delivery pattern` | coaching prompt / report rendering | `coaching_tuner` |
| Strengths are abstract or missing | `3` | `Upright confident presence`, `Alert room presence`, and report 3 has an empty strengths list | coaching prompt / report rendering | `coaching_tuner` |
| Forced issue selection instead of a real no-issue mode | `3` | Every report ends with a correction even when the clip reads mostly stable | threshold / coaching prompt | `coaching_tuner` |
| Metric and system leakage into teacher-facing copy | `3` | `overall=64.1`, `Targeted Qwen interpretation was not run for this window.` | report rendering | `coaching_tuner` |

## Strong Patterns To Preserve

| Pattern | Clips affected | Why it worked |
| --- | --- | --- |
| Tight, scannable report structure with summary, strengths, actions, and evidence moments | `3` | Makes the output easy to scan and jump through, even when the content needs revision. |
| Direct, nonjudgmental tone | `3` | The feedback stays coach-like and does not shame the teacher. |

## Clip-Level Notes

### Passes worth preserving

- None in this round.

### Fails requiring tuning

- `run_20260317T213602Z`:
  main blocker: generic action and weak strengths.
  evidence: `Open the stance between points`; `Upright confident presence`; `Alert room presence`.
  recommended change: replace abstract titles with one concrete repeatable behavior and one teacher test for the next class.
- `run_20260317T214522Z`:
  main blocker: same generic template behavior as the first report.
  evidence: `open the stance between points`; `overall=64.1`; `Preserve this delivery pattern`.
  recommended change: suppress metric-led phrasing in teacher copy and require a specific coaching move tied to the cited window.
- `run_20260317T214817Z`:
  main blocker: no strengths, but still a forced correction.
  evidence: empty `top_strengths`; `soften the visible facial tone`; `Keep using the moments that already look most stable and room-facing.`
  recommended change: allow a real maintenance/no-issue mode and only surface a fix when the evidence clearly warrants one.

## Tuning Recommendations for coaching_tuner

### Threshold adjustments

- Proposed change: allow a no-issue or maintenance-only output when the clip is mostly stable and the candidate fixes are low-severity.
  reason: report 3 should not be forced into a single correction when the evidence is thin.
  clips: `run_20260317T214817Z`
- Proposed change: raise the bar for top-action selection unless the report can cite a concrete, visible behavior and a teacher-relevant consequence.
  reason: the current actions are too generic to be useful.
  clips: all 3

### VLM prompt adjustments

- Proposed change: ask for one clip-specific observation, one why-it-matters sentence, and one next-lecture experiment.
  reason: the current outputs stay at the level of labels instead of instruction.
  clips: all 3
- Proposed change: require evidence-aware confidence language when face, hands, or expression are not clearly visible.
  reason: the uncertainty note is generic and does not track the actual evidence limits.
  clips: all 3

### Coaching prompt / report adjustments

- Proposed change: move raw metric strings and pipeline notes out of teacher-facing prose.
  reason: `overall=...` and `Qwen interpretation was not run` are debug details, not coaching.
  clips: all 3
- Proposed change: make strengths concrete or omit them; if there is no stable strength, say that plainly.
  reason: abstract strengths do not help the teacher preserve anything useful.
  clips: all 3

## Release Recommendation

- Status: `hold`
- Reason: the reports are readable but too generic to be teacher-useful, and they still force a correction even when the clip looks mostly stable.
- Minimum changes required before next goldset rerun:
  - remove metric/system leakage from teacher-facing text
  - add a real no-issue / maintenance mode
  - make strengths and actions concrete enough that a teacher could test them next lesson
