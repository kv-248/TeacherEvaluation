# TeacherEvaluation

This repository contains a research-backed nonverbal-cue evaluation pipeline for teacher lecture videos. The integrated code uses existing pretrained components only, with no training or finetuning.

## Included

- `nonverbal_eval/`
  - core landmark-based evaluation package
- `run_experiment.py`
  - short clip evaluation and debug artifact generation
- `run_segment_batch.py`
  - multi-segment comparison runner
- `run_long_experiment.py`
  - extended context-window inference runner
  - now also supports teacher-facing coaching brief generation
- `docs/`
  - report source, PDF, figure generator, PDF renderer, and generated figures
  - frontend QA notes for the Streamlit coaching-report UI
- `artifacts/`
  - selected debug runs, logs, summaries, plots, and exported media
- `samples/`
  - sample lecture video used in the experiments

## Main report

- Markdown: `docs/nonverbal_eval_research_report.md`
- PDF: `docs/nonverbal_eval_research_report.pdf`

The report includes:

- tracked metrics and how they are computed
- literature traceability for each metric
- experiment results on the sample lecture video
- the 1-minute context-window run at `12 fps`
- debug and automation-boundary discussion

The long-run runner can now emit a separate coaching artifact set:

- `teacher_coaching_report.json`
- `teacher_coaching_report.md`
- `teacher_coaching_report.pdf`
- `coaching_evidence.json`
- `coaching_moments/`

## Key artifacts included

- debug session with overlay video:
  - `artifacts/nonverbal_eval_debug3/run_20260315T193444Z/`
- batch comparison across short lecture segments:
  - `artifacts/nonverbal_eval_batch/batch_20260315T191630Z/`
- extended context-window run:
  - `artifacts/nonverbal_eval_long/run_20260315T202856Z/`
- sample video:
  - `samples/Lecture_1_cut_1m_to_5m.mp4`

## Docker (Recommended)

The easiest way to run the pipeline is via Docker Compose. All dependencies (including OpenCV's system packages and WeasyPrint for PDF generation) are handled automatically.

1. Ensure your Gemini API key is in your environment:
   ```bash
   export GEMINI_API_KEY=your_rotated_key_here
   ```
2. Start the interactive Streamlit UI (available at http://localhost:8501):
   ```bash
   docker compose up streamlit
   ```
3. Or run a headless evaluation batch across the included `clips/`:
   ```bash
   docker compose run evaluator --clip-ids crashcourse_moon_phases,harvard_mba_case_classroom
   ```

## Manual Run

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Example commands:

```bash
python run_experiment.py --video samples/Lecture_1_cut_1m_to_5m.mp4
python run_segment_batch.py --video samples/Lecture_1_cut_1m_to_5m.mp4
python run_long_experiment.py --video samples/Lecture_1_cut_1m_to_5m.mp4 --start-sec 92.5 --duration-sec 60 --analysis-fps 12
```

Default Gemini-backed semantic review and coaching:

```bash
export GEMINI_API_KEY=your_rotated_key_here
python run_long_experiment.py \
  --video samples/Lecture_1_cut_1m_to_5m.mp4 \
  --start-sec 92.5 \
  --duration-sec 60 \
  --analysis-fps 12 \
  --enable-semantic \
  --semantic-model gemini-2.5-flash \
  --coach-model gemini-2.5-flash
```

This is the recommended path for this repo. It avoids local heavy-model downloads and uses the Gemini API for both frame-level semantic review and final coaching synthesis.

Legacy local-transformer support still exists in code, but it is no longer the default and it is not required for normal use. If you ever need that older path for experiments, install:

```bash
pip install -r requirements_optional_semantic.txt
```

Gemini coaching output is validated against the `feedback_first_v1` report shape and falls back to the deterministic template brief if the response cannot be parsed cleanly.

Fast smoke test with no semantic model call:

```bash
python run_long_experiment.py \
  --video samples/Lecture_1_cut_1m_to_5m.mp4 \
  --start-sec 115 \
  --duration-sec 20 \
  --analysis-fps 12 \
  --enable-coaching \
  --disable-qwen \
  --coach-fallback-template-only
```

Streamlit frontend with a static coaching-report QA fixture and a small Playwright smoke test:

```bash
export TEACHER_EVALUATION_QA_REPORT_JSON=/workspace/TeacherEvaluation/frontend_tests/teacher_coaching_report.fixture.json
streamlit run streamlit_app.py
python frontend_tests/streamlit_smoke.py --app-url http://127.0.0.1:8501
```

To use Gemini in the Streamlit frontend without editing code:

```bash
export GEMINI_API_KEY=your_rotated_key_here
export TEACHER_EVALUATION_SEMANTIC_MODEL=gemini-2.5-flash
export TEACHER_EVALUATION_COACH_MODEL=gemini-2.5-flash
streamlit run streamlit_app.py
```

Then enable semantic review in the sidebar and turn off template-only coaching if you want the final coaching brief to use Gemini too.


To regenerate the report figures and PDF:

```bash
python docs/generate_report_figures.py
python docs/render_report_pdf.py --input docs/nonverbal_eval_research_report.md --output docs/nonverbal_eval_research_report.pdf
```

## Notes

- The current MediaPipe/TFLite path is effectively CPU-bound in this environment. The two available A40 GPUs are not the main acceleration path for the current inference stack.
- The semantic layer is strictly additive. It writes separate semantic artifacts and does not change the existing heuristic score formulas.
- The coaching layer is also strictly additive. It builds a separate teacher-facing brief from structured evidence and does not overwrite `summary_full.*` or `window_summary.*`.
- The default semantic model is `gemini-2.5-flash`.
- The default coaching synthesis model is also `gemini-2.5-flash`. If that call is unavailable or the response is malformed, the runner falls back to a deterministic template-driven coaching brief.
- No local heavy LLM or VLM download is required for the default path. The optional `transformers` and `accelerate` stack is only for legacy local experiments. SAM2 has a stricter torch requirement and is therefore gated behind explicit config/checkpoint arguments and version checks.
- The current runtime expects the legacy MediaPipe `solutions` API, so `requirements.txt` pins `mediapipe==0.10.21` and a compatible OpenCV/Numpy range.
- `.codex/`, workspace session logs, and unrelated local state are intentionally excluded.
