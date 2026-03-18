# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_power_politics_180_240/run_20260318T013008Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.865`
- Face coverage: `0.843`
- Hand coverage: `0.820`

## Scores

- Natural movement: `19.3` (limited)
- Positive affect: `42.0` (limited)
- Enthusiasm: `49.6` (limited)
- Posture stability: `75.6` (strong)
- Confidence/presence: `64.5` (moderate)
- Audience orientation: `64.3` (moderate)
- Eye-contact distribution: `76.2` (strong)
- Alertness: `82.0` (strong)
- Gesture smoothness: `55.1` (moderate)
- Stage usage: `100.0`
- Heuristic nonverbal score: `52.9` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `13.4` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `32.1` (low)

## Raw Metrics

- Gesture extent mean: `2.167`
- Arm span mean: `0.984`
- Gesture motion mean: `0.0981`
- Gesture motion peak: `2.0717`
- Gesture motion std: `0.1707`
- Open palm ratio: `0.598`
- Pointing ratio: `0.039`
- Fist ratio: `0.139`
- Smile proxy mean: `0.333`
- Smile proxy std: `0.0314`
- Mouth open mean: `0.1682`
- Mouth open std: `0.1615`
- Eye open mean: `0.4042`
- Brow-eye mean: `0.1710`
- Signed yaw std: `0.7187`
- Stage range: `0.456`
- LDLJ raw: `20.515`
- SAL raw: `-5.118`

## Eye-Contact Proxy

- Sector balance score: `86.9`
- Room scan score: `84.0`
- Sector distribution: `left=322, center=71, right=215`
- Gaze transitions: `44`
- Gaze transition rate/sec: `0.733`

## Feedback

### Strengths
- Posture is upright and stable, supporting a confident classroom presence.
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

- Pose coverage dropped below 95%; posture and gesture scores are less stable.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
