# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_quantum_240_300/run_20260318T013148Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.252`
- Hand coverage: `0.466`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `20.0` (limited)
- Enthusiasm: `41.2` (limited)
- Posture stability: `60.5` (moderate)
- Confidence/presence: `65.1` (moderate)
- Audience orientation: `43.0` (limited)
- Eye-contact distribution: `65.8` (moderate)
- Alertness: `71.0` (moderate)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `41.6` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `39.0` (moderate)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `36.6` (moderate)

## Raw Metrics

- Gesture extent mean: `4.195`
- Arm span mean: `2.982`
- Gesture motion mean: `0.7200`
- Gesture motion peak: `28.7942`
- Gesture motion std: `1.6769`
- Open palm ratio: `0.055`
- Pointing ratio: `0.028`
- Fist ratio: `0.362`
- Smile proxy mean: `0.314`
- Smile proxy std: `0.0351`
- Mouth open mean: `0.0688`
- Mouth open std: `0.1598`
- Eye open mean: `0.4788`
- Brow-eye mean: `0.2038`
- Signed yaw std: `0.5748`
- Stage range: `0.440`
- LDLJ raw: `21.566`
- SAL raw: `-14.680`

## Eye-Contact Proxy

- Sector balance score: `82.5`
- Room scan score: `87.8`
- Sector distribution: `left=32, center=34, right=116`
- Gaze transitions: `40`
- Gaze transition rate/sec: `0.667`

## Feedback

### Strengths
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
- Facial affect looks somewhat tense; verify that expressions do not read as harsh or closed.
- Body posture trends somewhat closed; monitor slouching or arm positions that reduce openness.

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
