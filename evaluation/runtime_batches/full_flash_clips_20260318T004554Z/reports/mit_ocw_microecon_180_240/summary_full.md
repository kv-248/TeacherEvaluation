# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_microecon_180_240/run_20260318T005454Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.901`
- Face coverage: `0.592`
- Hand coverage: `0.761`

## Scores

- Natural movement: `18.5` (limited)
- Positive affect: `26.6` (limited)
- Enthusiasm: `44.3` (limited)
- Posture stability: `62.5` (moderate)
- Confidence/presence: `69.3` (moderate)
- Audience orientation: `54.0` (limited)
- Eye-contact distribution: `68.3` (moderate)
- Alertness: `75.0` (moderate)
- Gesture smoothness: `52.8` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `46.4` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `30.1` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `24.0` (low)

## Raw Metrics

- Gesture extent mean: `3.043`
- Arm span mean: `1.876`
- Gesture motion mean: `0.2953`
- Gesture motion peak: `6.2602`
- Gesture motion std: `0.4868`
- Open palm ratio: `0.315`
- Pointing ratio: `0.019`
- Fist ratio: `0.317`
- Smile proxy mean: `0.296`
- Smile proxy std: `0.0469`
- Mouth open mean: `0.1853`
- Mouth open std: `0.2230`
- Eye open mean: `0.4563`
- Brow-eye mean: `0.1959`
- Signed yaw std: `0.8211`
- Stage range: `0.599`
- LDLJ raw: `21.196`
- SAL raw: `-5.316`

## Eye-Contact Proxy

- Sector balance score: `84.3`
- Room scan score: `72.6`
- Sector distribution: `left=233, center=42, right=151`
- Gaze transitions: `56`
- Gaze transition rate/sec: `0.935`

## Feedback

### Strengths
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
