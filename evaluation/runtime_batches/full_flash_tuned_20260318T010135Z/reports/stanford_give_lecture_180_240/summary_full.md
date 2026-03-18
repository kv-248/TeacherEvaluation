# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_give_lecture_180_240/run_20260318T011624Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.047`

## Scores

- Natural movement: `24.1` (limited)
- Positive affect: `20.0` (limited)
- Enthusiasm: `45.1` (limited)
- Posture stability: `81.4` (strong)
- Confidence/presence: `87.2` (strong)
- Audience orientation: `85.1` (strong)
- Eye-contact distribution: `90.3` (strong)
- Alertness: `90.0` (strong)
- Gesture smoothness: `68.8` (moderate)
- Stage usage: `84.6`
- Heuristic nonverbal score: `60.9` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `73.9` (high)
- Tension/hostility risk: `20.7` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `0.0` (low)

## Raw Metrics

- Gesture extent mean: `1.928`
- Arm span mean: `1.504`
- Gesture motion mean: `0.0519`
- Gesture motion peak: `0.5763`
- Gesture motion std: `0.0682`
- Open palm ratio: `0.043`
- Pointing ratio: `0.003`
- Fist ratio: `0.000`
- Smile proxy mean: `0.313`
- Smile proxy std: `0.0305`
- Mouth open mean: `0.2258`
- Mouth open std: `0.1364`
- Eye open mean: `0.3397`
- Brow-eye mean: `0.1464`
- Signed yaw std: `0.4834`
- Stage range: `0.260`
- LDLJ raw: `21.741`
- SAL raw: `-3.921`

## Eye-Contact Proxy

- Sector balance score: `99.0`
- Room scan score: `86.8`
- Sector distribution: `left=219, center=212, right=290`
- Gaze transitions: `41`
- Gaze transition rate/sec: `0.683`

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

- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
