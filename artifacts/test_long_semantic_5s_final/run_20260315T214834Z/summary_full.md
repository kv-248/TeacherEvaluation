# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/artifacts/test_long_semantic_5s_final/run_20260315T214834Z/full_segment_reference.mp4`
- Start: `120.00s`
- Duration requested: `5.00s`
- Frames analyzed: `61`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.984`

## Scores

- Natural movement: `37.2` (limited)
- Positive affect: `42.9` (limited)
- Enthusiasm: `47.5` (limited)
- Posture stability: `81.2` (strong)
- Confidence/presence: `81.2` (strong)
- Audience orientation: `65.4` (moderate)
- Eye-contact distribution: `73.0` (moderate)
- Alertness: `84.0` (strong)
- Gesture smoothness: `66.0` (moderate)
- Stage usage: `54.5`
- Heuristic nonverbal score: `61.3` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `39.3` (moderate)
- Tension/hostility risk: `11.7` (low)
- Rigidity risk: `7.1` (low)
- Closed-posture risk: `11.0` (low)

## Raw Metrics

- Gesture extent mean: `1.277`
- Arm span mean: `1.954`
- Gesture motion mean: `0.0523`
- Gesture motion peak: `0.2400`
- Gesture motion std: `0.0519`
- Open palm ratio: `0.934`
- Pointing ratio: `0.000`
- Fist ratio: `0.033`
- Smile proxy mean: `0.343`
- Smile proxy std: `0.0187`
- Mouth open mean: `0.2043`
- Mouth open std: `0.1518`
- Eye open mean: `0.3813`
- Brow-eye mean: `0.1613`
- Signed yaw std: `0.7306`
- Stage range: `0.182`
- LDLJ raw: `12.539`
- SAL raw: `-3.038`

## Eye-Contact Proxy

- Sector balance score: `72.0`
- Room scan score: `91.9`
- Sector distribution: `left=23, center=2, right=36`
- Gaze transitions: `2`
- Gaze transition rate/sec: `0.400`

## Feedback

### Strengths
- Posture is upright and stable, supporting a confident classroom presence.
- Body openness and stance suggest confident delivery rather than closed-off presentation.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.

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
