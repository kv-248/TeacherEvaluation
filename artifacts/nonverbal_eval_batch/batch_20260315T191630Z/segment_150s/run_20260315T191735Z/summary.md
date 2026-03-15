# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/artifacts/nonverbal_eval_batch/batch_20260315T191630Z/segment_150s/run_20260315T191735Z/clip_5s.mp4`
- Start: `150.00s`
- Duration requested: `5.00s`
- Frames analyzed: `151`
- FPS: `29.97`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `1.000`

## Scores

- Natural movement: `54.3` (limited)
- Positive affect: `47.8` (limited)
- Enthusiasm: `52.1` (limited)
- Posture stability: `86.4` (strong)
- Confidence/presence: `67.2` (moderate)
- Audience orientation: `79.2` (strong)
- Eye-contact distribution: `78.3` (strong)
- Alertness: `84.6` (strong)
- Gesture smoothness: `63.1` (moderate)
- Stage usage: `33.5`
- Heuristic nonverbal score: `65.4` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `42.6` (moderate)
- Tension/hostility risk: `13.9` (low)
- Rigidity risk: `3.5` (low)
- Closed-posture risk: `53.9` (moderate)

## Raw Metrics

- Gesture extent mean: `1.498`
- Arm span mean: `0.785`
- Gesture motion mean: `0.0296`
- Gesture motion peak: `0.2329`
- Gesture motion std: `0.0394`
- Open palm ratio: `0.642`
- Pointing ratio: `0.046`
- Fist ratio: `0.325`
- Smile proxy mean: `0.356`
- Smile proxy std: `0.0204`
- Mouth open mean: `0.1286`
- Mouth open std: `0.1100`
- Eye open mean: `0.3159`
- Brow-eye mean: `0.1728`
- Signed yaw std: `0.4809`
- Stage range: `0.127`
- LDLJ raw: `13.919`
- SAL raw: `-3.739`

## Eye-Contact Proxy

- Sector balance score: `88.9`
- Room scan score: `57.7`
- Sector distribution: `left=57, center=19, right=75`
- Gaze transitions: `6`
- Gaze transition rate/sec: `1.199`

## Feedback

### Strengths
- Posture is upright and stable, supporting a confident classroom presence.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
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
