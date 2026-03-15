# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/artifacts/nonverbal_eval_batch/batch_20260315T191630Z/segment_090s/run_20260315T191652Z/clip_5s.mp4`
- Start: `90.00s`
- Duration requested: `5.00s`
- Frames analyzed: `152`
- FPS: `29.97`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `1.000`

## Scores

- Natural movement: `57.6` (moderate)
- Positive affect: `45.2` (limited)
- Enthusiasm: `48.9` (limited)
- Posture stability: `84.2` (strong)
- Confidence/presence: `65.7` (moderate)
- Audience orientation: `83.2` (strong)
- Eye-contact distribution: `68.9` (moderate)
- Alertness: `90.2` (strong)
- Gesture smoothness: `80.1` (strong)
- Stage usage: `21.1`
- Heuristic nonverbal score: `67.8` (moderate)

## Risks

- Static behavior risk: `9.8` (low)
- Excessive animation risk: `10.9` (low)
- Tension/hostility risk: `8.2` (low)
- Rigidity risk: `6.8` (low)
- Closed-posture risk: `60.0` (moderate)

## Raw Metrics

- Gesture extent mean: `1.390`
- Arm span mean: `0.735`
- Gesture motion mean: `0.0346`
- Gesture motion peak: `0.1547`
- Gesture motion std: `0.0287`
- Open palm ratio: `0.697`
- Pointing ratio: `0.007`
- Fist ratio: `0.112`
- Smile proxy mean: `0.350`
- Smile proxy std: `0.0189`
- Mouth open mean: `0.1946`
- Mouth open std: `0.1812`
- Eye open mean: `0.3589`
- Brow-eye mean: `0.1735`
- Signed yaw std: `0.3068`
- Stage range: `0.095`
- LDLJ raw: `14.406`
- SAL raw: `-2.413`

## Eye-Contact Proxy

- Sector balance score: `63.0`
- Room scan score: `46.9`
- Sector distribution: `left=0, center=79, right=73`
- Gaze transitions: `7`
- Gaze transition rate/sec: `1.389`

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
