# Batch feedback-quality assessment — 2026-04-17

Assessment of coaching-report feedback quality across five YouTube-curated
lecture clips, run on the Workstream-1/2/3 pipeline with `gemini-2.5-pro`
as the semantic and coaching model.

## Test corpus

All clips are 60-second cuts from the curated dataset at
[datasets/lecture_eval_youtube_curated/clips/](../datasets/lecture_eval_youtube_curated/clips/).
Runs stored under [local_data/docker_test_outputs/batch_eval/](../local_data/docker_test_outputs/batch_eval/).

| # | Clip | Institution | Subject style | Overall score |
|---|---|---|---|---|
| 1 | `mit_ocw_how_to_speak_300_360` | MIT OCW | Board-facing demonstration | 53.3 |
| 2 | `stanford_cs230_240_300` | Stanford | Animated AI lecture | 51.1 |
| 3 | `yale_quantum_240_300` | Yale | Blackboard math/physics | 45.4 |
| 4 | `cs50_business_150_210` | Harvard CS50 | Slide-driven business talk | 49.9 |
| 5 | `mit_ocw_pigeonhole_240_300` | MIT OCW | Math discussion | 55.9 |

All runs completed end-to-end: semantic `status: completed`, PDF rendered,
keyframes + jump-to-timestamp links produced.

## Summary rating

| Layer | Rating | Note |
|---|---|---|
| Semantic per-frame review (Pro) | **9 / 10** | Discriminating, style-aware, no hallucinations observed |
| Scorecard + badges | **9 / 10** | Consistent across all 5 clips |
| At-a-Glance narrative | **8 / 10** | Pro writes fluent plain-English summaries |
| Top Actions (Why / What we saw / Try next) | **7 / 10** | Structurally correct; copy occasionally boilerplate |
| Strengths | **5 / 10** | Templatised evidence strings, copy-paste "Review at" windows |
| Watch Items | **3 / 10** | Severe duplication — overlaps with Strengths and self-duplicates |
| Moment-by-Moment Evidence | **8 / 10** | Metric + semantic + link integration is the strongest section |
| Technical appendix | **4 / 10** | Still dumps raw JSON blobs |
| Markdown rendering | **6 / 10** | Scorecard embeds raw HTML intended for PDF only |

**Overall feedback quality across the 5 batch runs: 6 / 10** — noticeably
below the 8/10 scored on the `Lecture_1_cut_1m_to_5m` reference run. The
regression is isolated to the coaching-synthesis layer (see root cause below).

## What the semantic layer does well

The Pro per-frame annotations are the strongest signal in the system and
correctly discriminate between teaching styles:

- **Yale Quantum** — 7/8 frames labelled `teacher_focus: board` and 6/8 labelled
  `body_action: writing_board`. The teacher was in fact writing equations on
  a blackboard. `posture_signal: closed_or_slouched` fired on 2/8 frames —
  consistent with hunching over the board.
- **MIT "How to Speak"** (Patrick Winston) — 5/8 frames `teacher_focus: board`,
  3/8 `body_action: walking`. Winston famously paced and wrote simultaneously;
  the annotations capture that.
- **MIT Pigeonhole** — 6/8 `teacher_focus: audience`, 6/8 `posture_signal:
  upright_open`. This was a math-discussion clip where the instructor stood
  open-postured and explained. Correctly characterised.
- **Stanford CS230** — 6/8 `teacher_focus: audience`, 4/8 `body_action:
  open_palm_explaining`. Matches the animated AI-lecture style.
- **CS50 Business** — split 3/8 `screen`, 3/8 `audience`. Correctly captures
  the alternation between slide-glance and audience delivery.

None of the 40 frame annotations contained invented detail or
off-schema outputs. Rationales were grounded in visible evidence
("teacher is mid-stride, walking across the stage. His head is turned towards
the audience.").

## What the coaching layer does well

Across all 5 reports:

1. **Scorecard is consistent and scannable** — Overall score + 5 sub-scores
   with green/amber/red bands render identically, and the bands correctly
   track the underlying metrics.
2. **At-a-Glance narratives are fluent** — e.g. Yale Quantum: *"Your stage
   usage and expressive range are effective. The main opportunities for growth
   are in moderating the size of your gestures to match the importance of
   your points and in turning back to face the audience more quickly after
   writing on the board."* This is coach-quality prose, not metric readout.
3. **Moment-by-Moment Evidence is the strongest section**. Each moment
   combines: (a) tag list ("low face visibility / uneven room scan / low
   audience orientation"), (b) metric row ("Overall 39.4; room scan 46.9;
   presence 59.3; natural movement 23.8"), (c) semantic interpretation
   paraphrase, (d) coaching implication, (e) timestamp jump-link,
   (f) embedded keyframe thumbnail. This is the section teachers are
   most likely to actually use.
4. **Top-Action heading is correct** across all counts: "Top Action" (1),
   "Top 2 Actions" (2), "Top 3 Actions" (3). The previously-reported heading
   bug is gone.
5. **Confidence labels are uniform** (`low` / `medium` / `high`) — no more
   "QC confidence" variant mixed in.

## What is clearly degraded — and why

### Core regression: all 5 runs fell back to `llm_api_hybrid`

The `Report Provenance` footer on every one of the 5 batch runs reads:

```
Source mode: `llm_api_hybrid`
```

compared to the clean `llm_api` footer on the earlier `Lecture_1` reference
run. The `events.jsonl` on every batch run contains:

```json
{"event": "coaching_llm_partial_output",
 "payload": {"reason": "Schema-valid Gemini output did not satisfy
             feedback_first_v2 validation; merged onto deterministic fallback.",
             "model": "gemini-2.5-pro"}}
```

This is the deferred follow-up flagged in the implementation plan. Pro is
returning schema-valid JSON, but the local `feedback_first_v2` post-validator
is rejecting it and merging the template fallback. The result is a
mixed report: **At-a-Glance + Top Actions come from Pro, but Strengths and
Watch Items come from the template.**

### Symptoms of the fallback in the rendered reports

1. **Copy-paste "Review at" windows.** Every Strength across every clip
   lists the *same* 4 windows (00:00-00:15, 00:15-00:30, 00:30-00:45,
   00:45-01:00). That is the template echoing the input window set, not
   selecting evidence windows.
2. **Templatised evidence strings.** Evidence lines concatenate the same
   skeleton per window: `"00:00-00:15 used a room sweep that reached more
   than one sector over time. 00:15-00:30 used a room sweep that reached
   more than one sector over time."` This repeats verbatim across clips
   and wastes the teacher's attention.
3. **Watch Items duplicate Strengths.** On 3 of 5 clips, the same heading
   appears in *both* Strengths and Watch Items (e.g. `mit_how_to_speak`:
   `Purposeful room coverage` and `Purposeful pause control` appear in
   both sections; `yale_quantum`: `Distributed room engagement` appears in
   both). This is a template bug, not an LLM bug.
4. **Watch Items self-duplicate.** Same heading appears twice within Watch
   Items (e.g. `mit_how_to_speak` has `Break the static stage anchor` and
   `Turn back toward the audience sooner` each listed twice; `yale_quantum`
   has three headings duplicated). The second copy is usually the generic
   "The signal is visible, but it is not yet sustained enough to justify
   real corrective feedback." version.
5. **"Why watch" = "What we saw".** In every Watch Item, the two fields
   contain identical text — the template isn't distinguishing the forward-
   looking prompt from the observation.
6. **Confidence collapsed to `medium` / `low`.** The reference run had
   mostly `high`; these 5 runs have no `high` Confidence anywhere except
   on two Moment-by-Moment entries. This is the fallback being
   conservative, not a genuine lower-quality observation.

### Non-fallback issues still present

These would remain even with a clean LLM path:

1. **Scorecard HTML in markdown.** `<div class="scorecard">...</div>`
   renders correctly in the WeasyPrint PDF but ugly in raw markdown
   viewers. A markdown-native fallback with text traffic-light badges
   should render alongside.
2. **Technical Appendix JSON dumps.** Lines 130-132 of each report dump
   raw `movement_presence`, `facial_expressiveness`, and `gaze_dynamics`
   JSON in code-spans. These belong in `summary_full.md` only, or should
   be converted into readable tables.
3. **Sweep rate calibration.** All 5 clips reported 34-52 sweeps/min.
   McIntyre et al. (2017) expert-teacher baselines are 3-8/min. The
   current metric is picking up micro-saccades, not purposeful room scans.
   Not a report-quality issue per se, but a metric-interpretation issue
   that leaks into the copy ("Balanced gaze sweep" fires on every clip).
4. **Jump-to-timestamp link path.** Links use absolute container paths
   like `/outputs/batch_eval/.../full_segment_reference.mp4#t=45` that
   only resolve inside Docker. For external viewing, these should be
   relative paths.

## Per-clip findings

### MIT How to Speak — 53.3 / 100

*Winston's classic board-heavy delivery.* Semantic layer correctly flags
board-focus (5/8 frames) and walking motion (3/8). Coaching picks
"Tighten gesture size" as the single Top Action, which is reasonable.
Watch Items section is the most affected by the duplication bug — 5 of
6 entries repeat content from elsewhere in the report.

### Stanford CS230 — 51.1 / 100

*Animated AI lecture.* Correctly picks up open-palm explanation (4/8) and
over-animation signal (severity 79). Top Actions are solid and specific.
"Balanced gaze sweep" is a false strength — driven by the mis-calibrated
sweep-rate metric.

### Yale Quantum — 45.4 / 100

*Math on a blackboard.* Lowest overall score, and appropriately so: teacher
focus is dominantly board (7/8), audience orientation is low, and posture
slouches when writing. The `Turn back toward the audience sooner` action
is legitimately useful feedback for this specific teaching style. This is
the clip where the pipeline gives the most *actionable* feedback.

### CS50 Business — 49.9 / 100

*Slide-driven business talk.* Semantic layer correctly flags screen/audience
split (3/3). Three Top Actions surface here — gesture size, open stance,
turn back to audience — all consistent with a slide-presenter standing next
to a screen. Copy quality is typical of the hybrid fallback.

### MIT Pigeonhole — 55.9 / 100

*Math discussion, confident stance.* Highest overall score. Correctly picks
"Break the static stage anchor" as Action 1 (severity 89) — the teacher
genuinely stays in one zone. Semantic layer shows 6/8 audience focus and
6/8 upright_open, matching observed confidence.

## Recommendations

Prioritised, with the `feedback_first_v2` validator fix as the highest-impact
single change:

1. **[High — unblocks Watch Items / Strengths quality]** Relax or reshape the
   `feedback_first_v2` post-validator so Pro's schema-valid output flows
   through without merging the deterministic template. All 6 symptoms of
   degraded feedback listed above collapse when this is fixed.
2. **[Medium]** Enforce Watch-Items de-duplication at the merge step: any
   heading that already appears in Strengths or in earlier Watch-Items
   entries should not render again.
3. **[Medium]** Add a markdown-native scorecard fallback alongside the HTML
   `<div>` block, so raw-markdown viewers see a clean table.
4. **[Medium]** Remove JSON blobs from the Technical Appendix; either
   table-ify (movement zone dwell, pause stats) or relocate to
   `summary_full.md`.
5. **[Low — data-quality]** Recalibrate `sweep_rate_per_min` so it reflects
   purposeful left-center-right scans, not micro-saccades. Target the
   3-8/min expert-teacher band from McIntyre et al. (2017). Until fixed,
   "Balanced gaze sweep" will surface as a strength on essentially every
   clip.
6. **[Low]** Switch jump-to-timestamp links to relative paths so the
   rendered markdown is portable outside the Docker container.

## Bottom line for the thesis defence

**What the pipeline demonstrably does:** a Pro-grade vision model produces
per-frame semantic annotations that correctly discriminate between teaching
styles across 5 lecturers from 4 institutions, no hallucinations, 100% of
frames on-schema. Metric layer, scorecard, and moment-by-moment evidence
integration all work end-to-end. The top-of-report summary prose is fluent
and coaching-grade.

**What still needs work:** the coaching-synthesis post-validator is the
single largest remaining quality blocker. Fixing it is a local code change
— no additional LLM work, no new data, no architectural shift — and would
bring the 5 batch reports from 6/10 to approximately 8/10 (matching the
`Lecture_1` reference run's quality).
