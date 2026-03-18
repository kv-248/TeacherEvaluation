# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_power_elec_240_300/run_20260318T011234Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.983`
- Hand coverage: `0.646`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `27.4` (limited)
- Enthusiasm: `45.3` (limited)
- Posture stability: `74.0` (moderate)
- Confidence/presence: `70.4` (moderate)
- Audience orientation: `72.2` (moderate)
- Eye-contact distribution: `80.9` (strong)
- Alertness: `83.9` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `51.9` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `33.6` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `3.2` (low)

## Raw Metrics

- Gesture extent mean: `2.231`
- Arm span mean: `1.113`
- Gesture motion mean: `0.1362`
- Gesture motion peak: `2.8090`
- Gesture motion std: `0.2230`
- Open palm ratio: `0.342`
- Pointing ratio: `0.044`
- Fist ratio: `0.246`
- Smile proxy mean: `0.318`
- Smile proxy std: `0.0284`
- Mouth open mean: `0.0789`
- Mouth open std: `0.1277`
- Eye open mean: `0.4463`
- Brow-eye mean: `0.1526`
- Signed yaw std: `0.8707`
- Stage range: `0.341`
- LDLJ raw: `21.587`
- SAL raw: `-7.226`

## Eye-Contact Proxy

- Sector balance score: `95.7`
- Room scan score: `74.5`
- Sector distribution: `left=339, center=166, right=203`
- Gaze transitions: `54`
- Gaze transition rate/sec: `0.901`

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

- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
