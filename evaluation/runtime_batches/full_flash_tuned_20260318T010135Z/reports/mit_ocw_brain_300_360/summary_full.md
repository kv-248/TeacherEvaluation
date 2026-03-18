# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_brain_300_360/run_20260318T010424Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `59.99s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.000`

## Scores

- Natural movement: `36.3` (limited)
- Positive affect: `31.4` (limited)
- Enthusiasm: `34.3` (limited)
- Posture stability: `89.3` (strong)
- Confidence/presence: `89.4` (strong)
- Audience orientation: `80.7` (strong)
- Eye-contact distribution: `79.1` (strong)
- Alertness: `91.0` (strong)
- Gesture smoothness: `64.3` (moderate)
- Stage usage: `0.0`
- Heuristic nonverbal score: `59.6` (moderate)

## Risks

- Static behavior risk: `68.6` (high)
- Excessive animation risk: `25.7` (low)
- Tension/hostility risk: `7.5` (low)
- Rigidity risk: `30.9` (low)
- Closed-posture risk: `0.0` (low)

## Raw Metrics

- Gesture extent mean: `2.983`
- Arm span mean: `1.695`
- Gesture motion mean: `0.0088`
- Gesture motion peak: `0.0580`
- Gesture motion std: `0.0096`
- Open palm ratio: `0.000`
- Pointing ratio: `0.000`
- Fist ratio: `0.000`
- Smile proxy mean: `0.345`
- Smile proxy std: `0.0268`
- Mouth open mean: `0.1737`
- Mouth open std: `0.1443`
- Eye open mean: `0.4282`
- Brow-eye mean: `0.1923`
- Signed yaw std: `0.7089`
- Stage range: `0.011`
- LDLJ raw: `22.965`
- SAL raw: `-4.316`

## Eye-Contact Proxy

- Sector balance score: `84.7`
- Room scan score: `66.0`
- Sector distribution: `left=300, center=65, right=355`
- Gaze transitions: `63`
- Gaze transition rate/sec: `1.051`

## Feedback

### Strengths
- Posture is upright and stable, supporting a confident classroom presence.
- Body openness and stance suggest confident delivery rather than closed-off presentation.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may be too limited in places; check for stretches of static delivery.

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
