#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: arm_periodic_push.sh [options]

Arm a detached scheduler that runs push_checkpoint.sh every N seconds.

Options:
  --repo-root PATH       Repo root. Default: script parent directory
  --interval-sec N       Push interval in seconds. Default: 900
  --state-root PATH      Directory for scheduler state. Default: /tmp/checkpoint_push
  --run-immediately      Run one checkpoint push before the first sleep
  -h, --help             Show this help text.
EOF
}

REPO_ROOT=""
INTERVAL_SEC=900
STATE_ROOT="/tmp/checkpoint_push"
RUN_IMMEDIATELY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --interval-sec)
      INTERVAL_SEC="${2:-}"
      shift 2
      ;;
    --state-root)
      STATE_ROOT="${2:-}"
      shift 2
      ;;
    --run-immediately)
      RUN_IMMEDIATELY=true
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUSH_SCRIPT="${SCRIPT_DIR}/push_checkpoint.sh"
if [[ ! -x "$PUSH_SCRIPT" ]]; then
  chmod +x "$PUSH_SCRIPT"
fi

if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

mkdir -p "$STATE_ROOT"
SCHEDULER_LOG="${STATE_ROOT}/periodic_push.log"
SCHEDULER_PID_FILE="${STATE_ROOT}/periodic_push.pid"

RUN_NOW_FLAG=""
if [[ "$RUN_IMMEDIATELY" == "true" ]]; then
  RUN_NOW_FLAG="yes"
fi

nohup bash -lc '
set -euo pipefail
repo_root="$1"
state_root="$2"
interval_sec="$3"
push_script="$4"
run_now_flag="${5:-}"
log_file="${state_root}/periodic_push.log"
if [[ -n "$run_now_flag" ]]; then
  "$push_script" --repo-root "$repo_root" --state-root "$state_root" >>"$log_file" 2>&1 || true
fi
while true; do
  sleep "$interval_sec"
  "$push_script" --repo-root "$repo_root" --state-root "$state_root" >>"$log_file" 2>&1 || true
done
' _ "$REPO_ROOT" "$STATE_ROOT" "$INTERVAL_SEC" "$PUSH_SCRIPT" "$RUN_NOW_FLAG" \
  >/dev/null 2>&1 &
echo "$!" > "$SCHEDULER_PID_FILE"

printf 'repo_root=%s\ninterval_sec=%s\nscheduler_pid=%s\nlog_file=%s\n' \
  "$REPO_ROOT" \
  "$INTERVAL_SEC" \
  "$(cat "$SCHEDULER_PID_FILE")" \
  "$SCHEDULER_LOG"
ps -fp "$(cat "$SCHEDULER_PID_FILE")"
