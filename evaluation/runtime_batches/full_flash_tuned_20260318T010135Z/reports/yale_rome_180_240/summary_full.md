# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_rome_180_240/run_20260318T013337Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.928`
- Hand coverage: `0.022`

## Scores

- Natural movement: `30.3` (limited)
- Positive affect: `20.0` (limited)
- Enthusiasm: `37.1` (limited)
- Posture stability: `84.5` (strong)
- Confidence/presence: `87.2` (strong)
- Audience orientation: `80.8` (strong)
- Eye-contact distribution: `63.3` (moderate)
- Alertness: `89.6` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `52.7`
- Heuristic nonverbal score: `55.1` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `33.4` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `0.0` (low)

## Raw Metrics

- Gesture extent mean: `2.247`
- Arm span mean: `1.447`
- Gesture motion mean: `0.0384`
- Gesture motion peak: `1.2102`
- Gesture motion std: `0.0899`
- Open palm ratio: `0.017`
- Pointing ratio: `0.000`
- Fist ratio: `0.001`
- Smile proxy mean: `0.318`
- Smile proxy std: `0.0294`
- Mouth open mean: `0.0356`
- Mouth open std: `0.0681`
- Eye open mean: `0.3379`
- Brow-eye mean: `0.1901`
- Signed yaw std: `0.3968`
- Stage range: `0.177`
- LDLJ raw: `21.089`
- SAL raw: `-11.878`

## Eye-Contact Proxy

- Sector balance score: `21.3`
- Room scan score: `97.2`
- Sector distribution: `left=627, center=42, right=0`
- Gaze transitions: `30`
- Gaze transition rate/sec: `0.500`

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

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
