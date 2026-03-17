# Streamlit Frontend

This app is the minimal teacher-facing frontend for the pipeline.

## Scope

- Upload one lecture video up to 5 minutes.
- Run the shared `nonverbal_eval.app_service.run_teacher_evaluation(...)` entrypoint.
- Render the teacher-facing coaching brief.
- Provide downloads for the generated `JSON`, `Markdown`, and `PDF`.

The app intentionally does not expose:

- dataset validation controls
- batch tooling
- debug overlays
- admin-only evaluation artifacts

## Run

Install the frontend dependency set:

```bash
pip install -r requirements_frontend.txt
```

Start the app from the repo root:

```bash
streamlit run streamlit_app.py
```

## Notes

- Uploaded videos and run outputs are written under `local_data/streamlit/`.
- The frontend uses `12 fps` analysis by default.
- Qwen semantic review is optional from the sidebar.
- SAM2 stays disabled in this frontend.
- The shared service path is the source of truth; the frontend should not shell out to the CLI.
