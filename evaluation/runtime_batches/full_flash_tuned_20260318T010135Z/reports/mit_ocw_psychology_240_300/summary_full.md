# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_psychology_240_300/run_20260318T011358Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.803`
- Face coverage: `0.800`
- Hand coverage: `0.007`

## Scores

- Natural movement: `53.9` (limited)
- Positive affect: `21.6` (limited)
- Enthusiasm: `41.7` (limited)
- Posture stability: `98.2` (strong)
- Confidence/presence: `95.7` (strong)
- Audience orientation: `88.5` (strong)
- Eye-contact distribution: `85.0` (strong)
- Alertness: `71.0` (moderate)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `10.2`
- Heuristic nonverbal score: `61.5` (moderate)

## Risks

- Static behavior risk: `20.8` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `12.8` (low)
- Rigidity risk: `7.4` (low)
- Closed-posture risk: `0.0` (low)

## Raw Metrics

- Gesture extent mean: `2.569`
- Arm span mean: `1.400`
- Gesture motion mean: `0.0173`
- Gesture motion peak: `0.9591`
- Gesture motion std: `0.0658`
- Open palm ratio: `0.000`
- Pointing ratio: `0.003`
- Fist ratio: `0.007`
- Smile proxy mean: `0.340`
- Smile proxy std: `0.0186`
- Mouth open mean: `0.1855`
- Mouth open std: `0.1347`
- Eye open mean: `0.2612`
- Brow-eye mean: `0.2495`
- Signed yaw std: `0.2801`
- Stage range: `0.066`
- LDLJ raw: `21.410`
- SAL raw: `-29.146`

## Eye-Contact Proxy

- Sector balance score: `76.5`
- Room scan score: `91.9`
- Sector distribution: `left=25, center=264, right=288`
- Gaze transitions: `24`
- Gaze transition rate/sec: `0.400`

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

- Pose coverage dropped below 95%; posture and gesture scores are less stable.
- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
