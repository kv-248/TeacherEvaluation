# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_deconstruction_180_240/run_20260318T012158Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.951`
- Hand coverage: `0.976`

## Scores

- Natural movement: `26.1` (limited)
- Positive affect: `41.6` (limited)
- Enthusiasm: `52.0` (limited)
- Posture stability: `74.6` (moderate)
- Confidence/presence: `77.1` (strong)
- Audience orientation: `61.9` (moderate)
- Eye-contact distribution: `74.3` (moderate)
- Alertness: `80.9` (strong)
- Gesture smoothness: `74.6` (moderate)
- Stage usage: `100.0`
- Heuristic nonverbal score: `57.3` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `65.9` (high)
- Tension/hostility risk: `25.9` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `15.0` (low)

## Raw Metrics

- Gesture extent mean: `1.704`
- Arm span mean: `1.427`
- Gesture motion mean: `0.1127`
- Gesture motion peak: `1.4766`
- Gesture motion std: `0.1380`
- Open palm ratio: `0.802`
- Pointing ratio: `0.019`
- Fist ratio: `0.279`
- Smile proxy mean: `0.323`
- Smile proxy std: `0.0386`
- Mouth open mean: `0.1215`
- Mouth open std: `0.1606`
- Eye open mean: `0.4192`
- Brow-eye mean: `0.1847`
- Signed yaw std: `0.7936`
- Stage range: `0.499`
- LDLJ raw: `21.009`
- SAL raw: `-3.417`

## Eye-Contact Proxy

- Sector balance score: `84.8`
- Room scan score: `84.0`
- Sector distribution: `left=344, center=63, right=279`
- Gaze transitions: `44`
- Gaze transition rate/sec: `0.733`

## Feedback

### Strengths
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
