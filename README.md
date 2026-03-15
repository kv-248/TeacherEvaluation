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
- `docs/`
  - report source, PDF, figure generator, PDF renderer, and generated figures
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

To regenerate the report figures and PDF:

```bash
python docs/generate_report_figures.py
python docs/render_report_pdf.py --input docs/nonverbal_eval_research_report.md --output docs/nonverbal_eval_research_report.pdf
```

## Notes

- The current MediaPipe/TFLite path is effectively CPU-bound in this environment. The two available A40 GPUs are not the main acceleration path for the current inference stack.
- `.codex/`, workspace session logs, and unrelated local state are intentionally excluded.
