# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_linguistics_180_240/run_20260318T012631Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.997`
- Face coverage: `0.904`
- Hand coverage: `0.989`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `41.1` (limited)
- Enthusiasm: `47.2` (limited)
- Posture stability: `74.6` (moderate)
- Confidence/presence: `77.0` (strong)
- Audience orientation: `61.5` (moderate)
- Eye-contact distribution: `70.8` (moderate)
- Alertness: `80.8` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `52.1` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `72.8` (high)
- Tension/hostility risk: `25.6` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `15.5` (low)

## Raw Metrics

- Gesture extent mean: `1.881`
- Arm span mean: `1.815`
- Gesture motion mean: `0.2052`
- Gesture motion peak: `9.4963`
- Gesture motion std: `0.5741`
- Open palm ratio: `0.838`
- Pointing ratio: `0.087`
- Fist ratio: `0.147`
- Smile proxy mean: `0.322`
- Smile proxy std: `0.0425`
- Mouth open mean: `0.1199`
- Mouth open std: `0.1834`
- Eye open mean: `0.4058`
- Brow-eye mean: `0.1898`
- Signed yaw std: `0.7659`
- Stage range: `0.521`
- LDLJ raw: `21.500`
- SAL raw: `-14.323`

## Eye-Contact Proxy

- Sector balance score: `85.5`
- Room scan score: `66.1`
- Sector distribution: `left=247, center=66, right=339`
- Gaze transitions: `63`
- Gaze transition rate/sec: `1.050`

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

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
