# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_pigeonhole_240_300/run_20260318T011120Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.968`
- Face coverage: `0.744`
- Hand coverage: `0.932`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `37.4` (limited)
- Enthusiasm: `46.8` (limited)
- Posture stability: `71.6` (moderate)
- Confidence/presence: `77.5` (strong)
- Audience orientation: `67.6` (moderate)
- Eye-contact distribution: `74.6` (moderate)
- Alertness: `81.8` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `51.8` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `84.0` (high)
- Tension/hostility risk: `37.3` (moderate)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `8.5` (low)

## Raw Metrics

- Gesture extent mean: `2.142`
- Arm span mean: `1.586`
- Gesture motion mean: `0.1428`
- Gesture motion peak: `7.9150`
- Gesture motion std: `0.4233`
- Open palm ratio: `0.664`
- Pointing ratio: `0.024`
- Fist ratio: `0.174`
- Smile proxy mean: `0.282`
- Smile proxy std: `0.0362`
- Mouth open mean: `0.1581`
- Mouth open std: `0.1642`
- Eye open mean: `0.4475`
- Brow-eye mean: `0.2016`
- Signed yaw std: `0.5477`
- Stage range: `1.038`
- LDLJ raw: `19.902`
- SAL raw: `-6.140`

## Eye-Contact Proxy

- Sector balance score: `96.6`
- Room scan score: `51.9`
- Sector distribution: `left=140, center=147, right=249`
- Gaze transitions: `78`
- Gaze transition rate/sec: `1.302`

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

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
