# Clip Review Rubric

Use this rubric to decide whether a clip should stay in the validation set or be replaced by a stronger local clip.

## Goal

The set should favor clips that are useful for teacher-facing nonverbal evaluation: visible speaker, clear instructional intent, lecture pacing, board/screen orientation, gesture and posture cues, and enough movement to calibrate the downstream reviewer.

## Scoring Dimensions

Score each dimension from `1` to `5`.

### 1. Teacher Visibility

- `5`: speaker is clearly visible for most of the clip.
- `4`: speaker visibility is strong with only minor occlusion or camera drift.
- `3`: mixed visibility; some usable speaker footage but frequent reductions.
- `2`: weak visibility; speaker is often off-screen or tiny.
- `1`: essentially unusable for observing the teacher.

### 2. Lecture Fit

- `5`: directly instructional, classroom-like, or lecture-like.
- `4`: clearly educational, even if it is setup or demo oriented.
- `3`: adjacent to teaching, but not a direct teaching clip.
- `2`: mostly meta-talk, setup, or generic advice.
- `1`: not meaningfully related to teacher evaluation.

### 3. Nonverbal Usefulness

- `5`: strong evidence for gesture, posture, eye-line, and classroom orientation.
- `4`: good nonverbal signal with minor limitations.
- `3`: usable, but the signal is narrower or repetitive.
- `2`: little motion variety or too much screen/slide dominance.
- `1`: no useful nonverbal signal.

### 4. Distinctiveness

- `5`: adds a clearly different teaching pattern or classroom style.
- `4`: useful but only lightly overlaps with other selected clips.
- `3`: somewhat redundant.
- `2`: highly redundant with a better existing clip.
- `1`: duplicate value; should be replaced.

### 5. Technical Usability

- `5`: stable enough to review without distraction.
- `4`: minor issues only.
- `3`: acceptable, but some extraction or framing risk.
- `2`: distracting technical issues.
- `1`: not worth keeping.

## Decision Rule

- `keep` when Teacher Visibility, Lecture Fit, and Nonverbal Usefulness are all `4` or `5`, and the clip is not redundant.
- `replace` when the clip is educationally adjacent but weak on visibility, lecture fit, or nonverbal usefulness, and a better local clip exists.
- `drop` only when the clip is not useful enough to retain and no stronger replacement is needed for the active set.

## Confidence Guide

- `high`: the title, channel, and batch summary all point in the same direction.
- `medium`: the clip is likely useful, but some framing or content uncertainty remains.
- `low`: the decision depends on a weak title signal or the clip is borderline.

## Review Bias

Prefer clips that show:

- a clearly visible lecturer or teacher
- direct teaching or lecture delivery
- whiteboard, board, or screen coordination
- movement that reveals posture, gestures, and audience orientation
- enough contrast across teaching styles to avoid overfitting to one format

Prefer replacement for clips that are mostly:

- setup tutorials
- tool demos
- teacher interview prep
- generic presentation coaching
- broad public-speaking clips with weak teacher specificity
