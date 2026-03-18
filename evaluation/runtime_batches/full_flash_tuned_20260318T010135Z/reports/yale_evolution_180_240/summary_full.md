# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_evolution_180_240/run_20260318T012325Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.961`
- Face coverage: `0.562`
- Hand coverage: `0.603`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `25.8` (limited)
- Enthusiasm: `43.2` (limited)
- Posture stability: `67.2` (moderate)
- Confidence/presence: `71.0` (moderate)
- Audience orientation: `64.3` (moderate)
- Eye-contact distribution: `69.4` (moderate)
- Alertness: `79.4` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `47.9` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.2` (high)
- Tension/hostility risk: `46.4` (moderate)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `12.3` (low)

## Raw Metrics

- Gesture extent mean: `2.578`
- Arm span mean: `1.296`
- Gesture motion mean: `0.1626`
- Gesture motion peak: `5.0401`
- Gesture motion std: `0.3934`
- Open palm ratio: `0.290`
- Pointing ratio: `0.024`
- Fist ratio: `0.125`
- Smile proxy mean: `0.288`
- Smile proxy std: `0.0359`
- Mouth open mean: `0.0743`
- Mouth open std: `0.1093`
- Eye open mean: `0.4351`
- Brow-eye mean: `0.1592`
- Signed yaw std: `0.5083`
- Stage range: `0.437`
- LDLJ raw: `21.249`
- SAL raw: `-8.526`

## Eye-Contact Proxy

- Sector balance score: `76.7`
- Room scan score: `68.0`
- Sector distribution: `left=74, center=55, right=276`
- Gaze transitions: `61`
- Gaze transition rate/sec: `1.017`

## Feedback

### Strengths
- Body openness and stance suggest confident delivery rather than closed-off presentation.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
- Facial affect looks somewhat tense; verify that expressions do not read as harsh or closed.

## Manual Review

- Grooming/professional appearance: `manual_review_required`
- Reason: A landmark-only pipeline is not a validated or fair way to score grooming or professional appearance.
- Speech-gesture synchronization is intentionally out of scope in this version.
- Professional grooming/appearance requires manual review.

## Warnings

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
