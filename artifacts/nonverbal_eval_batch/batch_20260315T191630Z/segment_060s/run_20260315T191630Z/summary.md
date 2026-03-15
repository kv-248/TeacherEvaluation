# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/artifacts/nonverbal_eval_batch/batch_20260315T191630Z/segment_060s/run_20260315T191630Z/clip_5s.mp4`
- Start: `60.00s`
- Duration requested: `5.00s`
- Frames analyzed: `152`
- FPS: `29.97`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.993`

## Scores

- Natural movement: `65.5` (moderate)
- Positive affect: `42.7` (limited)
- Enthusiasm: `55.1` (moderate)
- Posture stability: `90.4` (strong)
- Confidence/presence: `62.8` (moderate)
- Audience orientation: `73.8` (moderate)
- Eye-contact distribution: `79.6` (strong)
- Alertness: `89.3` (strong)
- Gesture smoothness: `77.1` (strong)
- Stage usage: `31.3`
- Heuristic nonverbal score: `69.6` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `21.7` (low)
- Tension/hostility risk: `12.8` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `61.3` (moderate)

## Raw Metrics

- Gesture extent mean: `1.505`
- Arm span mean: `0.487`
- Gesture motion mean: `0.0244`
- Gesture motion peak: `0.1858`
- Gesture motion std: `0.0266`
- Open palm ratio: `0.664`
- Pointing ratio: `0.013`
- Fist ratio: `0.224`
- Smile proxy mean: `0.331`
- Smile proxy std: `0.0300`
- Mouth open mean: `0.2051`
- Mouth open std: `0.1547`
- Eye open mean: `0.3909`
- Brow-eye mean: `0.1720`
- Signed yaw std: `0.6434`
- Stage range: `0.121`
- LDLJ raw: `13.926`
- SAL raw: `-2.521`

## Eye-Contact Proxy

- Sector balance score: `86.5`
- Room scan score: `80.6`
- Sector distribution: `left=80, center=17, right=55`
- Gaze transitions: `4`
- Gaze transition rate/sec: `0.794`

## Feedback

### Strengths
- Posture is upright and stable, supporting a confident classroom presence.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Body posture trends somewhat closed; monitor slouching or arm positions that reduce openness.

## Manual Review

- Grooming/professional appearance: `manual_review_required`
- Reason: A landmark-only pipeline is not a validated or fair way to score grooming or professional appearance.
- Speech-gesture synchronization is intentionally out of scope in this version.
- Professional grooming/appearance requires manual review.

## Warnings

- None

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
