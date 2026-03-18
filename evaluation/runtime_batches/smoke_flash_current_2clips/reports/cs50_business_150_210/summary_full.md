# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/cs50_business_150_210/run_20260318T003242Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `0.992`
- Face coverage: `0.764`
- Hand coverage: `0.808`

## Scores

- Natural movement: `15.8` (limited)
- Positive affect: `35.7` (limited)
- Enthusiasm: `45.5` (limited)
- Posture stability: `71.0` (moderate)
- Confidence/presence: `68.5` (moderate)
- Audience orientation: `45.9` (limited)
- Eye-contact distribution: `68.2` (moderate)
- Alertness: `75.1` (strong)
- Gesture smoothness: `45.0` (limited)
- Stage usage: `100.0`
- Heuristic nonverbal score: `46.6` (limited)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `80.0` (high)
- Tension/hostility risk: `33.4` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `33.2` (low)

## Raw Metrics

- Gesture extent mean: `2.901`
- Arm span mean: `1.333`
- Gesture motion mean: `0.3363`
- Gesture motion peak: `8.8210`
- Gesture motion std: `0.7157`
- Open palm ratio: `0.611`
- Pointing ratio: `0.021`
- Fist ratio: `0.144`
- Smile proxy mean: `0.284`
- Smile proxy std: `0.0525`
- Mouth open mean: `0.2679`
- Mouth open std: `0.2827`
- Eye open mean: `0.4351`
- Brow-eye mean: `0.2094`
- Signed yaw std: `0.8644`
- Stage range: `0.412`
- LDLJ raw: `22.068`
- SAL raw: `-14.505`

## Eye-Contact Proxy

- Sector balance score: `91.5`
- Room scan score: `77.3`
- Sector distribution: `left=261, center=82, right=207`
- Gaze transitions: `51`
- Gaze transition rate/sec: `0.851`

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

- Face coverage dropped below 95%; audience orientation and facial scores are less stable.
- Hand coverage dropped below 85%; gesture classification is less stable.

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
