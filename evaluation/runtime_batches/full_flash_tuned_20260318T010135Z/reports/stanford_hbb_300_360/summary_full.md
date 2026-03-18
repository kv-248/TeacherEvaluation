# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/stanford_hbb_300_360/run_20260318T011753Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `59.99s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.807`
- Hand coverage: `0.006`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `21.6` (limited)
- Enthusiasm: `39.6` (limited)
- Posture stability: `65.4` (moderate)
- Confidence/presence: `62.1` (moderate)
- Audience orientation: `25.8` (limited)
- Eye-contact distribution: `52.8` (limited)
- Alertness: `67.3` (moderate)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `38.0` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `16.1` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `40.0` (moderate)

## Raw Metrics

- Gesture extent mean: `4.784`
- Arm span mean: `2.246`
- Gesture motion mean: `0.9242`
- Gesture motion peak: `17.1676`
- Gesture motion std: `1.9835`
- Open palm ratio: `0.001`
- Pointing ratio: `0.001`
- Fist ratio: `0.001`
- Smile proxy mean: `0.323`
- Smile proxy std: `0.0466`
- Mouth open mean: `0.2211`
- Mouth open std: `0.2509`
- Eye open mean: `0.5866`
- Brow-eye mean: `0.2627`
- Signed yaw std: `1.0893`
- Stage range: `0.659`
- LDLJ raw: `22.225`
- SAL raw: `-10.871`

## Eye-Contact Proxy

- Sector balance score: `63.5`
- Room scan score: `94.7`
- Sector distribution: `left=426, center=25, right=130`
- Gaze transitions: `25`
- Gaze transition rate/sec: `0.417`

## Feedback

### Strengths
- The instructor appears alert and attentive to the room.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
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
