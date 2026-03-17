# Validation Manifest Notes

This manifest is a curated validation set of exactly 50 clips selected from `/workspace/educational_lectures_5_to_10_mins.csv`.

## Inclusion Logic

- Prefer clips with explicit instructional intent: teaching, lecture delivery, whiteboard use, classroom management, demo classes, presentation coaching, and teacher training.
- Keep clips that show a visible speaker or presenter so nonverbal cue calibration is possible.
- Include a mix of delivery styles:
  - whiteboard-heavy online teaching
  - screen-recording and lesson-video workflows
  - lecture and faculty-style clips
  - classroom management and demo-class clips
  - presentation/body-language/public-speaking clips as adjacent benchmarks
- Use `start_hint_sec` as a center-biased extraction hint for later 60s window sampling at 12 fps.
- Mark the 12 strongest teacher-facing clips as `goldset_candidate=true` for manual review and prompt calibration.

## Exclusion Logic

- Avoid music, dance, art-only, gaming, and entertainment clips that do not clearly support teacher-facing nonverbal evaluation.
- Avoid channels beyond the 3-clip cap.
- Avoid near-duplicate selections from the same channel when a better style-diverse option exists.
- Prefer clips where the title and channel make instructional intent clear enough to support a 60s extraction without extensive guessing.

## Manual Review Categories

- Whiteboard teaching and setup-heavy clips
- Lesson-video and screen-recording workflows
- Lecture-effectiveness and teacher-skills advice
- Classroom-management and demo-class clips
- Academic or faculty lecture clips
- Presentation, speech, and body-language benchmarks
- Adjacent non-teacher public-speaking clips used only for calibration

## Extraction Policy

All rows use a center-biased 60s extraction policy at 12 fps. The extraction should start near `start_hint_sec`, with small manual adjustments allowed to keep the speaker, board, and screen in frame when possible.
