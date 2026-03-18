# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_cs230_240_300/run_20260318T011500Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.750`
- Hand coverage: `0.802`

## Scores

- Natural movement: `16.3` (limited)
- Positive affect: `34.9` (limited)
- Enthusiasm: `45.9` (limited)
- Posture stability: `61.8` (moderate)
- Confidence/presence: `74.5` (moderate)
- Audience orientation: `72.3` (moderate)
- Eye-contact distribution: `75.4` (strong)
- Alertness: `43.1` (limited)
- Gesture smoothness: `46.5` (limited)
- Stage usage: `96.8`
- Heuristic nonverbal score: `47.0` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `31.5` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `3.1` (low)

## Raw Metrics

- Gesture extent mean: `2.567`
- Arm span mean: `1.868`
- Gesture motion mean: `0.1054`
- Gesture motion peak: `1.7206`
- Gesture motion std: `0.1567`
- Open palm ratio: `0.560`
- Pointing ratio: `0.054`
- Fist ratio: `0.187`
- Smile proxy mean: `0.322`
- Smile proxy std: `0.0276`
- Mouth open mean: `0.0519`
- Mouth open std: `0.0749`
- Eye open mean: `0.2281`
- Brow-eye mean: `0.2556`
- Signed yaw std: `0.5246`
- Stage range: `0.292`
- LDLJ raw: `20.507`
- SAL raw: `-5.870`

## Eye-Contact Proxy

- Sector balance score: `75.7`
- Room scan score: `82.1`
- Sector distribution: `left=89, center=78, right=374`
- Gaze transitions: `46`
- Gaze transition rate/sec: `0.767`

## Feedback

### Strengths
- Body openness and stance suggest confident delivery rather than closed-off presentation.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
- Alertness cues are weaker than ideal; review eyelid openness and room-facing orientation.

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
