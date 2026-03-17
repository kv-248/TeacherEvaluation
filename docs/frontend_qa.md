# Frontend QA

This repo has a minimal Streamlit QA path for the coaching report schema.

## What It Covers

- `no_material_intervention_needed`
- `strength_inventory`
- `additional_observation_inventory`
- `low_confidence_watchlist`
- the existing JSON and Markdown downloads

## Install

Install the normal frontend dependencies and the Playwright smoke-test dependency:

```bash
pip install -r requirements_frontend.txt
pip install -r requirements_frontend_qa.txt
python -m playwright install chromium
```

## QA Fixture Mode

The Streamlit app can render a static coaching report fixture without running the evaluation pipeline.

Set these environment variables before starting the app:

```bash
export TEACHER_EVALUATION_QA_REPORT_JSON=/workspace/TeacherEvaluation/frontend_tests/teacher_coaching_report.fixture.json
```

Optional:

```bash
export TEACHER_EVALUATION_QA_REPORT_PDF=/path/to/teacher_coaching_report.pdf
```

Then start Streamlit from the repo root:

```bash
streamlit run streamlit_app.py
```

## Smoke Test

With the app open in QA fixture mode, run:

```bash
python frontend_tests/streamlit_smoke.py --app-url http://127.0.0.1:8501
```

Add `--headed` if you want to see the browser, and `--screenshot output/playwright/streamlit_smoke.png` if you want a capture.

## Notes

- The smoke test is intentionally small and only checks that the report sections render and the download buttons are present.
- For a real run, clear `TEACHER_EVALUATION_QA_REPORT_JSON` and use the normal upload flow.
