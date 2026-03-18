# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_linear_eq_180_240/run_20260318T005356Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.03s`
- Frames analyzed: `721`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.687`
- Face coverage: `0.133`
- Hand coverage: `0.412`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `20.0` (limited)
- Enthusiasm: `37.7` (limited)
- Posture stability: `43.4` (limited)
- Confidence/presence: `48.8` (limited)
- Audience orientation: `14.3` (limited)
- Eye-contact distribution: `42.4` (limited)
- Alertness: `57.3` (moderate)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `29.3` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `34.1` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `40.0` (moderate)

## Raw Metrics

- Gesture extent mean: `6.601`
- Arm span mean: `2.152`
- Gesture motion mean: `0.7810`
- Gesture motion peak: `14.6843`
- Gesture motion std: `1.5136`
- Open palm ratio: `0.079`
- Pointing ratio: `0.105`
- Fist ratio: `0.133`
- Smile proxy mean: `0.306`
- Smile proxy std: `0.0447`
- Mouth open mean: `0.1086`
- Mouth open std: `0.2334`
- Eye open mean: `0.3669`
- Brow-eye mean: `0.1508`
- Signed yaw std: `0.4107`
- Stage range: `0.619`
- LDLJ raw: `22.025`
- SAL raw: `-11.278`

## Eye-Contact Proxy

- Sector balance score: `62.6`
- Room scan score: `70.2`
- Sector distribution: `left=6, center=17, right=73`
- Gaze transitions: `16`
- Gaze transition rate/sec: `0.267`

## Feedback

### Strengths
- The clip is technically trackable, but no single nonverbal strength clearly dominates in this short window.

### Watch Items
- Movement may occasionally become more animated than needed for the teaching point.
- Body posture trends somewhat closed; monitor slouching or arm positions that reduce openness.
- Gaze distribution appears uneven; check whether the lecture favors one audience sector.

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
