# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_last_lecture_180_240/run_20260318T011901Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.897`
- Face coverage: `0.436`
- Hand coverage: `0.781`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `33.5` (limited)
- Enthusiasm: `45.3` (limited)
- Posture stability: `77.3` (strong)
- Confidence/presence: `80.4` (strong)
- Audience orientation: `68.8` (moderate)
- Eye-contact distribution: `75.0` (moderate)
- Alertness: `83.8` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `97.1`
- Heuristic nonverbal score: `53.9` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `70.1` (high)
- Tension/hostility risk: `17.9` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `7.1` (low)

## Raw Metrics

- Gesture extent mean: `1.822`
- Arm span mean: `1.790`
- Gesture motion mean: `0.1779`
- Gesture motion peak: `6.3528`
- Gesture motion std: `0.3200`
- Open palm ratio: `0.316`
- Pointing ratio: `0.022`
- Fist ratio: `0.430`
- Smile proxy mean: `0.334`
- Smile proxy std: `0.0540`
- Mouth open mean: `0.1772`
- Mouth open std: `0.1772`
- Eye open mean: `0.3463`
- Brow-eye mean: `0.1584`
- Signed yaw std: `0.4682`
- Stage range: `0.293`
- LDLJ raw: `20.962`
- SAL raw: `-8.277`

## Eye-Contact Proxy

- Sector balance score: `76.8`
- Room scan score: `85.9`
- Sector distribution: `left=30, center=77, right=207`
- Gaze transitions: `42`
- Gaze transition rate/sec: `0.700`

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

- Pose coverage dropped below 95%; posture and gesture scores are less stable.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
