# Subagent Workflow

This repository uses repo-local Codex subagents under `.codex/agents/`. The top-level Codex session acts as conductor and delegates narrow, parallel tasks to specialist agents.

## Agents

| Agent | Primary responsibility | Expected tracked outputs |
| --- | --- | --- |
| `validation_curator` | Curate the 50-clip validation set from the source CSV | `evaluation/validation_manifest.csv`, selection notes |
| `batch_eval_engineer` | Build dataset acquisition, extraction, and batch-run tooling | `tools/prepare_validation_dataset.py`, `tools/run_validation_batch.py`, tooling docs |
| `coaching_tuner` | Improve prompts, thresholds, and teacher-facing report quality | `configs/*.toml`, tuning notes, updates to `nonverbal_eval/` |
| `teacher_report_qa` | Define and apply the hybrid goldset rubric | `evaluation/goldset_rubric.md`, `evaluation/goldset_labels.csv`, findings template |
| `frontend_builder` | Build the minimal Streamlit upload-and-report app | `streamlit_app.py`, shared app-facing service, frontend notes |

## Waves

### Wave 0

- Add repo-local agent configs.
- Adjust ignore rules so `.codex/agents/**` is tracked.
- Add config skeletons and this runbook.
- Commit and push when stable.

### Wave 1

Run in parallel:

- `validation_curator`
- `teacher_report_qa`
- `frontend_builder`

Acceptance:

- validation manifest exists and is internally consistent
- goldset rubric and label template exist
- Streamlit shell exists with mocked or placeholder report rendering

Commit and push after all three are ready.

### Wave 2

Run in parallel:

- `batch_eval_engineer`
- `coaching_tuner`
- `frontend_builder` integration updates

Acceptance:

- acquisition and extraction tooling runs reproducibly
- baseline goldset outputs exist
- frontend can call the shared service path in a smoke-test flow

Commit and push after the wave is coherent end to end.

### Wave 3

Run in parallel:

- `teacher_report_qa` review pass
- `coaching_tuner` tuning pass
- `batch_eval_engineer` broader 50-clip run

Acceptance:

- revised goldset results show clear improvement or meet the target quality threshold
- tuned prompts and thresholds are versioned and documented

Commit and push after the improved configuration is stable.

### Wave 4

Conductor-led integration:

- final validation summary
- final frontend verification
- final docs update

Acceptance:

- upload-to-report flow works
- coaching report remains grounded and timestamp-linked
- current raw technical outputs still exist

Commit and push after the demo-ready state is verified.

## Push Cadence

- Each wave ends with a local commit and an immediate push to `origin/main`.
- If remote auth fails, keep the local commit boundary intact and resume the push later.

## Guardrails

- Raw downloaded videos and extracted clips stay local-only and git-ignored.
- No training or finetuning.
- Keep the teacher-facing report grounded to evidence and timestamps.
- Preserve `summary_full.*` and `window_summary.*` while improving the coaching layer.
