# Subagent Workflow

This repository uses repo-local Codex subagents under `.codex/agents/`. The top-level Codex session acts as conductor and keeps the work conductor-first: the conductor assigns lanes, specialist agents run in parallel where possible, and the conductor arbitrates only after lane outputs are ready.

## Operating Model

- The repo-local config is set up for up to eight parallel agent threads with depth limited to one handoff level.
- Keep one lane focused on dataset review, one on prompt debate, one on feedback-quality review, and one on frontend QA.
- Use the conductor to reconcile conflicts, not to duplicate specialist work.
- Prompt changes must be justified by actual report outputs, manual visual inspection, or explicit reviewer notes. Do not accept prompt edits based only on model preference.

## Agents

| Lane | Agents | Primary responsibility | Expected tracked outputs |
| --- | --- | --- | --- |
| Dataset review | `validation_reviewer`, `validation_curator`, `batch_eval_engineer` | Review the active manifest, prune weak clips, and materialize the reviewed set | Reviewed manifest, clip-review decisions, replacement notes, and local materialization logs |
| Prompt debate | `prompt_advocate_precision`, `prompt_advocate_actionability`, `prompt_arbiter` | Debate prompt wording, then resolve the debate into one recommendation | Prompt review notes, prompt config updates, and decision notes |
| Feedback-quality review | `feedback_quality_critic`, `feedback_completeness_reviewer` | Review report correctness, actionability, tone, confidence handling, and coverage gaps | `evaluation/report_quality_findings.md`, rubric updates, and backlog items |
| Frontend QA | `frontend_builder`, `frontend_qa` | Keep the upload-to-report path working and validate downloads | Frontend QA notes, smoke coverage, and doc updates |

## Execution Lanes

### Dataset Review

- Keep `evaluation/validation_manifest.csv` as the untouched source manifest.
- Treat `evaluation/reviewed_validation_manifest.csv` as the active tuning and batch-validation manifest.
- Use `/workspace/clips` as the only replacement pool for dropped validation items in this phase.
- Record keep/drop/replace decisions in `evaluation/clip_review_decisions.csv`.

### Prompt Debate

- Run `prompt_advocate_precision` and `prompt_advocate_actionability` in parallel.
- Hand both outputs to `prompt_arbiter` only after each advocate has recorded a concrete recommendation.
- Preserve the tension between precision and usefulness instead of averaging the two concerns away.
- Use report outputs, sampled debug artifacts, and manual clip inspection as the basis for prompt changes.
- Do not let either advocate write live configs directly; only the coaching tuner applies the winning merge.

### Feedback-Quality Review

- Run `feedback_quality_critic` and `feedback_completeness_reviewer` in parallel.
- Use the critic for defect severity and the completeness reviewer for coverage gaps.
- Feed recurring failures back into `evaluation/report_quality_findings.md` and the conductor backlog.
- Optimize for teacher usefulness first: if a clip does not justify corrective feedback, the report should say so explicitly and switch to strengths or watch items.

### Frontend QA

- Check the Streamlit upload-to-report path end to end.
- Verify downloads, stage/status handling, and the app-service integration path.
- Keep the frontend minimal and stable rather than broadening scope.
- Prefer Python Playwright smoke coverage over manual-only frontend checks when browser automation is needed.

## Cadence

1. Conduct the lanes in parallel when they are independent.
2. Use the arbiter or conductor only after the specialist outputs are in hand.
3. Record recurring issues in the backlog before starting the next iteration.
4. Commit at the end of each major wave and attempt an immediate push to `origin/main`.

## Guardrails

- Raw downloaded videos and extracted clips stay local-only and git-ignored.
- No training or finetuning.
- Keep teacher-facing feedback grounded to visible evidence and timestamps.
- Preserve `summary_full.*` and `window_summary.*` while improving the coaching layer.
- The conductor should delegate implementation by default and only take direct code changes for cross-cutting glue or blocked integration.
