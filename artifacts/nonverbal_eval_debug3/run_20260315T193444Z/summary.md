# Nonverbal Cue Experiment

## Clip

- Source clip: `/workspace/artifacts/nonverbal_eval_debug3/run_20260315T193444Z/clip_5s.mp4`
- Start: `120.00s`
- Duration requested: `5.00s`
- Frames analyzed: `152`
- FPS: `29.97`

## Quality Control

- Pose coverage: `1.000`
- Face coverage: `1.000`
- Hand coverage: `0.993`

## Scores

- Natural movement: `72.1` (moderate)
- Positive affect: `45.4` (limited)
- Enthusiasm: `62.0` (moderate)
- Posture stability: `81.6` (strong)
- Confidence/presence: `81.5` (strong)
- Audience orientation: `65.9` (moderate)
- Eye-contact distribution: `71.8` (moderate)
- Alertness: `84.3` (strong)
- Gesture smoothness: `74.5` (moderate)
- Stage usage: `55.3`
- Heuristic nonverbal score: `71.1` (moderate)

## Risks

- Static behavior risk: `0.0` (low)
- Excessive animation risk: `0.0` (low)
- Tension/hostility risk: `9.2` (low)
- Rigidity risk: `6.1` (low)
- Closed-posture risk: `10.4` (low)

## Raw Metrics

- Gesture extent mean: `1.271`
- Arm span mean: `1.936`
- Gesture motion mean: `0.0246`
- Gesture motion peak: `0.1293`
- Gesture motion std: `0.0237`
- Open palm ratio: `0.954`
- Pointing ratio: `0.000`
- Fist ratio: `0.053`
- Smile proxy mean: `0.347`
- Smile proxy std: `0.0192`
- Mouth open mean: `0.2104`
- Mouth open std: `0.1631`
- Eye open mean: `0.3856`
- Brow-eye mean: `0.1617`
- Signed yaw std: `0.7249`
- Stage range: `0.184`
- LDLJ raw: `13.164`
- SAL raw: `-2.499`

## Eye-Contact Proxy

- Sector balance score: `68.2`
- Room scan score: `91.4`
- Sector distribution: `left=57, center=3, right=92`
- Gaze transitions: `2`
- Gaze transition rate/sec: `0.397`

## Feedback

### Strengths
- Gesture movement looks natural rather than statue-like or mechanical.
- Posture is upright and stable, supporting a confident classroom presence.
- Body openness and stance suggest confident delivery rather than closed-off presentation.
- Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.
- The instructor appears alert and attentive to the room.

### Watch Items
- No major risk flags in this short clip; validate on longer spans before drawing conclusions.

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
