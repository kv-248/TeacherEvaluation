# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local/mit_ocw_intro_120_180/run_20260318T005251Z/full_segment_reference.mp4`
- Start: `0.00s`
- Duration requested: `60.00s`
- Frames analyzed: `720`
- FPS: `12.00`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `0.988`
- Hand coverage: `1.000`

## Scores

- Natural movement: `33.6` (limited)
- Positive affect: `64.4` (moderate)
- Enthusiasm: `62.0` (moderate)
- Posture stability: `78.9` (strong)
- Confidence/presence: `63.1` (moderate)
- Audience orientation: `75.9` (strong)
- Eye-contact distribution: `82.9` (strong)
- Alertness: `86.5` (strong)
- Gesture smoothness: `71.7` (moderate)
- Stage usage: `100.0`
- Heuristic nonverbal score: `63.4` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `66.1` (high)
- Tension/hostility risk: `11.5` (low)
- Rigidity risk: `0.0` (low)
- Closed-posture risk: `52.7` (moderate)

## Raw Metrics

- Gesture extent mean: `1.712`
- Arm span mean: `0.793`
- Gesture motion mean: `0.0432`
- Gesture motion peak: `0.3439`
- Gesture motion std: `0.0462`
- Open palm ratio: `0.972`
- Pointing ratio: `0.001`
- Fist ratio: `0.036`
- Smile proxy mean: `0.374`
- Smile proxy std: `0.0251`
- Mouth open mean: `0.1032`
- Mouth open std: `0.1064`
- Eye open mean: `0.4387`
- Brow-eye mean: `0.1654`
- Signed yaw std: `0.7610`
- Stage range: `0.360`
- LDLJ raw: `21.835`
- SAL raw: `-3.674`

## Eye-Contact Proxy

- Sector balance score: `90.2`
- Room scan score: `85.8`
- Sector distribution: `left=149, center=164, right=398`
- Gaze transitions: `42`
- Gaze transition rate/sec: `0.701`

## Feedback

### Strengths
- Facial affect reads as reasonably welcoming and approachable.
- Posture is upright and stable, supporting a confident classroom presence.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
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

- None

## Notes

- These scores are heuristic nonverbal proxies based on pretrained landmark detectors.
- They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.
- Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.
