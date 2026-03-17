# Goldset Review Findings Template v2

## Review Round

- Round ID:
- Reviewer:
- Date:
- Model / prompt config under review:
- Threshold config under review:
- Clips reviewed:
- Pass count:
- Fail count:

## Snapshot

| Dimension | Avg score | Main issue if below target |
| --- | --- | --- |
| Completeness |  |  |
| Non-genericness |  |  |
| Confidence calibration |  |  |
| Strength handling |  |  |

Targets for rapid iteration:
- completeness: `>= 4.0`
- non-genericness: `>= 4.0`
- confidence calibration: `>= 4.0`
- strength handling: `>= 4.0`

## Recurring Failure Modes

List only patterns seen in at least `2` clips.

| Failure mode | Clips affected | What it looked like | Likely source | Suggested owner |
| --- | --- | --- | --- | --- |
|  |  |  | threshold / VLM prompt / coaching prompt / report rendering | coaching_tuner |
|  |  |  | threshold / VLM prompt / coaching prompt / report rendering | coaching_tuner |
|  |  |  | threshold / VLM prompt / coaching prompt / report rendering | coaching_tuner |

## Strong Patterns To Preserve

| Pattern | Clips affected | Why it worked |
| --- | --- | --- |
|  |  |  |
|  |  |  |

## Clip-Level Notes

### Passes worth preserving

- `clip_id`:
  reason:
- `clip_id`:
  reason:

### Fails requiring tuning

- `clip_id`:
  main blocker:
  evidence:
  recommended change:
- `clip_id`:
  main blocker:
  evidence:
  recommended change:

## Tuning Recommendations for coaching_tuner

### Threshold adjustments

- Proposed change:
  reason:
  clips:
- Proposed change:
  reason:
  clips:

### VLM prompt adjustments

- Proposed change:
  reason:
  clips:
- Proposed change:
  reason:
  clips:

### Coaching prompt / report adjustments

- Proposed change:
  reason:
  clips:
- Proposed change:
  reason:
  clips:

## Release Recommendation

- Status: `hold` / `advance`
- Reason:
- Minimum changes required before next goldset rerun:
  - 
  - 
