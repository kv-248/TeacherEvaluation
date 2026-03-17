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

## Run

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

Optional semantic layer with Qwen and SAM2 as additive outputs only:

```bash
pip install -r requirements_optional_semantic.txt
python run_long_experiment.py \
  --video samples/Lecture_1_cut_1m_to_5m.mp4 \
  --start-sec 92.5 \
  --duration-sec 60 \
  --analysis-fps 12 \
  --enable-semantic \
  --qwen-model Qwen/Qwen2.5-VL-7B-Instruct \
  --qwen-device cuda:0 \
  --disable-sam2
```

For a larger Qwen checkpoint that can shard across both A40s, pass a model id such as `Qwen/Qwen2.5-VL-32B-Instruct` with `--qwen-device-map auto`.

Teacher-facing coaching brief with targeted Qwen review and a local synthesis model:

```bash
python run_long_experiment.py \
  --video samples/Lecture_1_cut_1m_to_5m.mp4 \
  --start-sec 92.5 \
  --duration-sec 60 \
  --analysis-fps 12 \
  --enable-coaching
```

Fast smoke test without downloading local Qwen weights:

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

If you want SAM2 outputs as well, pass a local config and checkpoint:

```bash
python run_long_experiment.py \
  --video samples/Lecture_1_cut_1m_to_5m.mp4 \
  --start-sec 92.5 \
  --duration-sec 60 \
  --analysis-fps 12 \
  --enable-semantic \
  --sam2-model-cfg <sam2_config.yaml> \
  --sam2-checkpoint <sam2_checkpoint.pt>
```

To regenerate the report figures and PDF:

```bash
python docs/generate_report_figures.py
python docs/render_report_pdf.py --input docs/nonverbal_eval_research_report.md --output docs/nonverbal_eval_research_report.pdf
```

## Notes

- The current MediaPipe/TFLite path is effectively CPU-bound in this environment. The two available A40 GPUs are not the main acceleration path for the current inference stack.
- The semantic layer is strictly additive. It writes separate semantic artifacts and does not change the existing heuristic score formulas.
- The coaching layer is also strictly additive. It builds a separate teacher-facing brief from structured evidence and does not overwrite `summary_full.*` or `window_summary.*`.
- The default semantic model is now `Qwen/Qwen2.5-VL-7B-Instruct`, which is a stronger drop-in upgrade over the earlier `3B` path for this repo's frame-level semantic review tasks.
- The default coaching synthesis model is `Qwen/Qwen2.5-3B-Instruct`. If that model is unavailable, the runner falls back to a deterministic template-driven coaching brief.
- Qwen can run with the optional `transformers` and `accelerate` dependencies. SAM2 has a stricter torch requirement and is therefore gated behind explicit config/checkpoint arguments and version checks.
- The current runtime expects the legacy MediaPipe `solutions` API, so `requirements.txt` pins `mediapipe==0.10.21` and a compatible OpenCV/Numpy range.
- `.codex/`, workspace session logs, and unrelated local state are intentionally excluded.
