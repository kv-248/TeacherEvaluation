# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_newtonian_240_300/run_20260318T012824Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.865`
- Hand coverage: `0.910`

## Scores

- Natural movement: `23.2` (limited)
- Positive affect: `23.6` (limited)
- Enthusiasm: `40.4` (limited)
- Posture stability: `63.9` (moderate)
- Confidence/presence: `78.0` (strong)
- Audience orientation: `80.7` (strong)
- Eye-contact distribution: `80.7` (strong)
- Alertness: `83.4` (strong)
- Gesture smoothness: `66.2` (moderate)
- Stage usage: `65.5`
- Heuristic nonverbal score: `54.1` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `55.3` (moderate)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `0.0` (low)

## Raw Metrics

- Gesture extent mean: `2.925`
- Arm span mean: `2.566`
- Gesture motion mean: `0.0531`
- Gesture motion peak: `0.7149`
- Gesture motion std: `0.0807`
- Open palm ratio: `0.326`
- Pointing ratio: `0.026`
- Fist ratio: `0.434`
- Smile proxy mean: `0.282`
- Smile proxy std: `0.0243`
- Mouth open mean: `0.0441`
- Mouth open std: `0.0739`
- Eye open mean: `0.4620`
- Brow-eye mean: `0.1706`
- Signed yaw std: `0.4822`
- Stage range: `0.210`
- LDLJ raw: `20.965`
- SAL raw: `-4.151`

## Eye-Contact Proxy

- Sector balance score: `78.7`
- Room scan score: `84.0`
- Sector distribution: `left=61, center=164, right=399`
- Gaze transitions: `44`
- Gaze transition rate/sec: `0.733`

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
