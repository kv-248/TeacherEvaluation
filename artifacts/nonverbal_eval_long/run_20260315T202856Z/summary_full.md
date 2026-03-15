# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/artifacts/nonverbal_eval_long/run_20260315T202856Z/full_segment_reference.mp4`
- Start: `92.50s`
- Duration requested: `60.00s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.990`
- Hand coverage: `0.975`

## Scores

- Natural movement: `24.3` (limited)
- Positive affect: `49.8` (limited)
- Enthusiasm: `52.3` (limited)
- Posture stability: `79.4` (strong)
- Confidence/presence: `65.7` (moderate)
- Audience orientation: `70.9` (moderate)
- Eye-contact distribution: `79.9` (strong)
- Alertness: `85.1` (strong)
- Gesture smoothness: `56.8` (moderate)
- Stage usage: `90.9`
- Heuristic nonverbal score: `58.4` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `61.0` (moderate)
- Tension/hostility risk: `7.0` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `36.9` (moderate)

## Raw Metrics

- Gesture extent mean: `1.568`
- Arm span mean: `0.912`
- Gesture motion mean: `0.0625`
- Gesture motion peak: `1.0954`
- Gesture motion std: `0.0886`
- Open palm ratio: `0.803`
- Pointing ratio: `0.006`
- Fist ratio: `0.119`
- Smile proxy mean: `0.344`
- Smile proxy std: `0.0256`
- Mouth open mean: `0.1928`
- Mouth open std: `0.1698`
- Eye open mean: `0.3853`
- Brow-eye mean: `0.1753`
- Signed yaw std: `0.6090`
- Stage range: `0.276`
- LDLJ raw: `21.219`
- SAL raw: `-4.969`

## Eye-Contact Proxy

- Sector balance score: `90.2`
- Room scan score: `82.1`
- Sector distribution: `left=323, center=94, right=297`
- Gaze transitions: `46`
- Gaze transition rate/sec: `0.767`

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
