# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/yale_finance_240_300/run_20260318T012454Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.404`

## Scores

- Natural movement: `22.4` (limited)
- Positive affect: `24.9` (limited)
- Enthusiasm: `39.5` (limited)
- Posture stability: `65.8` (moderate)
- Confidence/presence: `62.5` (moderate)
- Audience orientation: `80.3` (strong)
- Eye-contact distribution: `71.0` (moderate)
- Alertness: `61.6` (moderate)
- Gesture smoothness: `63.9` (moderate)
- Stage usage: `68.5`
- Heuristic nonverbal score: `49.4` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `72.9` (high)
- Tension/hostility risk: `31.3` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `31.9` (low)

## Raw Metrics

- Gesture extent mean: `1.901`
- Arm span mean: `0.914`
- Gesture motion mean: `0.0851`
- Gesture motion peak: `0.7879`
- Gesture motion std: `0.1042`
- Open palm ratio: `0.356`
- Pointing ratio: `0.004`
- Fist ratio: `0.031`
- Smile proxy mean: `0.323`
- Smile proxy std: `0.0232`
- Mouth open mean: `0.0601`
- Mouth open std: `0.0931`
- Eye open mean: `0.2688`
- Brow-eye mean: `0.2079`
- Signed yaw std: `0.3903`
- Stage range: `0.218`
- LDLJ raw: `21.953`
- SAL raw: `-4.354`

## Eye-Contact Proxy

- Sector balance score: `54.9`
- Room scan score: `78.3`
- Sector distribution: `left=55, center=78, right=588`
- Gaze transitions: `19`
- Gaze transition rate/sec: `0.317`

## Feedback

### Strengths
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.

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
