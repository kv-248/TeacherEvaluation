# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_how_to_speak_300_360/run_20260318T005125Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `59.99s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.994`
- Face coverage: `0.554`
- Hand coverage: `0.383`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `22.2` (limited)
- Enthusiasm: `44.0` (limited)
- Posture stability: `66.6` (moderate)
- Confidence/presence: `74.7` (moderate)
- Audience orientation: `65.9` (moderate)
- Eye-contact distribution: `81.1` (strong)
- Alertness: `79.7` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `49.6` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `31.8` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `10.4` (low)

## Raw Metrics

- Gesture extent mean: `3.468`
- Arm span mean: `2.292`
- Gesture motion mean: `0.1799`
- Gesture motion peak: `4.3000`
- Gesture motion std: `0.3673`
- Open palm ratio: `0.172`
- Pointing ratio: `0.011`
- Fist ratio: `0.278`
- Smile proxy mean: `0.306`
- Smile proxy std: `0.0280`
- Mouth open mean: `0.1320`
- Mouth open std: `0.1151`
- Eye open mean: `0.3489`
- Brow-eye mean: `0.1451`
- Signed yaw std: `0.5364`
- Stage range: `0.495`
- LDLJ raw: `21.670`
- SAL raw: `-10.858`

## Eye-Contact Proxy

- Sector balance score: `97.9`
- Room scan score: `85.8`
- Sector distribution: `left=154, center=94, right=151`
- Gaze transitions: `42`
- Gaze transition rate/sec: `0.701`

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
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
