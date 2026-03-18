#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: push_checkpoint.sh [options]

Stage approved runtime artifacts and code changes, create a timestamped commit
when needed, and push to origin/main.

Options:
  --repo-root PATH       Repo root. Default: current working tree root
  --state-root PATH      Directory for logs/lock files. Default: /tmp/checkpoint_push
  --commit-prefix TEXT   Commit message prefix. Default: runtime checkpoint
  --preflight            Verify git remote/auth and show staged candidate paths only
  -h, --help             Show this help text.
EOF
}

timestamp_compact() {
  date -u '+%Y%m%dT%H%M%SZ'
}

log_line() {
  local message="$1"
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$message" | tee -a "$LOG_FILE"
}

REPO_ROOT=""
STATE_ROOT="/tmp/checkpoint_push"
COMMIT_PREFIX="runtime checkpoint"
PREFLIGHT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --state-root)
      STATE_ROOT="${2:-}"
      shift 2
      ;;
    --commit-prefix)
      COMMIT_PREFIX="${2:-}"
      shift 2
      ;;
    --preflight)
      PREFLIGHT=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
fi

mkdir -p "$STATE_ROOT"
LOG_FILE="${STATE_ROOT}/push_checkpoint.log"
LOCK_DIR="${STATE_ROOT}/lock"
LOCK_PID_FILE="${LOCK_DIR}/pid"

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" >"$LOCK_PID_FILE"
    return 0
  fi

  if [[ -f "$LOCK_PID_FILE" ]]; then
    local lock_pid
    lock_pid="$(cat "$LOCK_PID_FILE" 2>/dev/null || true)"
    if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
      log_line "another checkpoint push is already running; exiting"
      exit 0
    fi
  fi

  rm -rf "$LOCK_DIR"
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" >"$LOCK_PID_FILE"
    log_line "reclaimed stale checkpoint lock"
    return 0
  fi

  log_line "could not acquire checkpoint lock; exiting"
  exit 0
}

release_lock() {
  rm -f "$LOCK_PID_FILE" >/dev/null 2>&1 || true
  rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
}

acquire_lock
trap 'release_lock' EXIT

cd "$REPO_ROOT"

REMOTE_HEAD="$(git ls-remote origin -h refs/heads/main | awk '{print $1}')"
log_line "remote main head: ${REMOTE_HEAD:-unknown}"

stage_runtime_batches() {
  if [[ -d evaluation/runtime_batches ]]; then
    while IFS= read -r -d '' file; do
      git add -- "$file"
    done < <(find evaluation/runtime_batches -type f \( -name '*.md' -o -name '*.json' -o -name '*.csv' -o -name '*.pdf' \) -print0)
  fi
}

stage_code_and_notes() {
  local paths=(
    README.md
    configs
    nonverbal_eval
    docs
    streamlit_app.py
    run_long_experiment.py
    requirements.txt
    requirements_eval.txt
    requirements_optional_semantic.txt
    requirements_frontend.txt
    requirements_frontend_qa.txt
    ops
    evaluation/*.py
    evaluation/*.md
    evaluation/prompt_lab/runtime_flash_*.md
    evaluation/report_quality_findings_runtime.md
  )
  git add -- "${paths[@]}" 2>/dev/null || true
}

stage_runtime_batches
stage_code_and_notes

if [[ "$PREFLIGHT" == "true" ]]; then
  git diff --cached --name-only | sed -n '1,200p'
  exit 0
fi

if git diff --cached --quiet; then
  log_line "no staged changes; nothing to commit"
  exit 0
fi

COMMIT_MSG="${COMMIT_PREFIX} $(timestamp_compact)"
git commit -m "$COMMIT_MSG" >/dev/null
log_line "created commit: ${COMMIT_MSG}"
git push origin main >/dev/null
log_line "pushed commit to origin/main"
