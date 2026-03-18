# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_prog_method_240_300/run_20260318T012043Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.908`
- Hand coverage: `0.876`

## Scores

- Natural movement: `21.1` (limited)
- Positive affect: `40.5` (limited)
- Enthusiasm: `47.8` (limited)
- Posture stability: `72.1` (moderate)
- Confidence/presence: `75.2` (strong)
- Audience orientation: `59.3` (moderate)
- Eye-contact distribution: `61.9` (moderate)
- Alertness: `79.4` (strong)
- Gesture smoothness: `60.2` (moderate)
- Stage usage: `100.0`
- Heuristic nonverbal score: `51.9` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `74.1` (high)
- Tension/hostility risk: `32.1` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `18.0` (low)

## Raw Metrics

- Gesture extent mean: `1.934`
- Arm span mean: `1.496`
- Gesture motion mean: `0.1401`
- Gesture motion peak: `3.4383`
- Gesture motion std: `0.2322`
- Open palm ratio: `0.785`
- Pointing ratio: `0.022`
- Fist ratio: `0.040`
- Smile proxy mean: `0.321`
- Smile proxy std: `0.0319`
- Mouth open mean: `0.0443`
- Mouth open std: `0.0581`
- Eye open mean: `0.3629`
- Brow-eye mean: `0.1578`
- Signed yaw std: `0.6462`
- Stage range: `0.466`
- LDLJ raw: `20.751`
- SAL raw: `-4.676`

## Eye-Contact Proxy

- Sector balance score: `55.0`
- Room scan score: `80.2`
- Sector distribution: `left=534, center=59, right=61`
- Gaze transitions: `48`
- Gaze transition rate/sec: `0.801`

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

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
