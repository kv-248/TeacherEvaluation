# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_aero_300_360/run_20260318T004519Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `59.99s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.981`
- Face coverage: `0.671`
- Hand coverage: `0.389`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `29.0` (limited)
- Enthusiasm: `38.1` (limited)
- Posture stability: `57.7` (moderate)
- Confidence/presence: `65.3` (moderate)
- Audience orientation: `48.0` (limited)
- Eye-contact distribution: `30.3` (limited)
- Alertness: `71.7` (moderate)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `38.3` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `15.8` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `30.9` (low)

## Raw Metrics

- Gesture extent mean: `3.334`
- Arm span mean: `3.031`
- Gesture motion mean: `0.3805`
- Gesture motion peak: `28.3202`
- Gesture motion std: `1.5510`
- Open palm ratio: `0.229`
- Pointing ratio: `0.053`
- Fist ratio: `0.031`
- Smile proxy mean: `0.330`
- Smile proxy std: `0.0427`
- Mouth open mean: `0.1621`
- Mouth open std: `0.2112`
- Eye open mean: `0.5607`
- Brow-eye mean: `0.2440`
- Signed yaw std: `0.4340`
- Stage range: `0.544`
- LDLJ raw: `21.523`
- SAL raw: `-19.056`

## Eye-Contact Proxy

- Sector balance score: `3.4`
- Room scan score: `37.7`
- Sector distribution: `left=0, center=3, right=480`
- Gaze transitions: `4`
- Gaze transition rate/sec: `0.067`

## Feedback

### Strengths
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
- Gaze distribution appears uneven; check whether the lecture favors one audience sector.

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
