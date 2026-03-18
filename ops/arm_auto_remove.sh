#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: arm_auto_remove.sh --pod-id POD_ID [options]

Arm two detached auto-removal watchdogs for a Runpod pod.

Options:
  --pod-id POD_ID             Literal Runpod pod id. Required.
  --env-file PATH             Env file with RUNPOD_API_KEY. Default: /workspace/.env
  --primary-delay-sec N       Primary watchdog delay in seconds. Default: 10800
  --secondary-delay-sec N     Secondary watchdog delay in seconds. Default: 11400
  --retries N                 Removal retries per watchdog. Default: 60
  --retry-delay-sec N         Seconds between retries. Default: 60
  --state-root PATH           Directory for pid/log/schedule files. Default: /tmp/runpod_auto_remove
  -h, --help                  Show this help text.

This script performs a preflight check before arming the watchdogs.
EOF
}

timestamp_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

POD_ID=""
ENV_FILE="/workspace/.env"
PRIMARY_DELAY_SEC=10800
SECONDARY_DELAY_SEC=11400
RETRIES=60
RETRY_DELAY_SEC=60
STATE_ROOT="/tmp/runpod_auto_remove"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pod-id)
      POD_ID="${2:-}"
      shift 2
      ;;
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --primary-delay-sec)
      PRIMARY_DELAY_SEC="${2:-}"
      shift 2
      ;;
    --secondary-delay-sec)
      SECONDARY_DELAY_SEC="${2:-}"
      shift 2
      ;;
    --retries)
      RETRIES="${2:-}"
      shift 2
      ;;
    --retry-delay-sec)
      RETRY_DELAY_SEC="${2:-}"
      shift 2
      ;;
    --state-root)
      STATE_ROOT="${2:-}"
      shift 2
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

if [[ -z "$POD_ID" ]]; then
  printf -- '--pod-id is required.\n\n' >&2
  usage >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOVE_SCRIPT="${SCRIPT_DIR}/auto_remove_pod.sh"
if [[ ! -x "$REMOVE_SCRIPT" ]]; then
  chmod +x "$REMOVE_SCRIPT"
fi

RUN_STATE_DIR="${STATE_ROOT}/${POD_ID}"
mkdir -p "$RUN_STATE_DIR"

PRIMARY_LOG="${RUN_STATE_DIR}/primary.log"
SECONDARY_LOG="${RUN_STATE_DIR}/secondary.log"
PRIMARY_PID_FILE="${RUN_STATE_DIR}/primary.pid"
SECONDARY_PID_FILE="${RUN_STATE_DIR}/secondary.pid"
SCHEDULE_FILE="${RUN_STATE_DIR}/schedule.txt"

"$REMOVE_SCRIPT" \
  --pod-id "$POD_ID" \
  --env-file "$ENV_FILE" \
  --log-file "${RUN_STATE_DIR}/preflight.log" \
  --preflight

PRIMARY_TARGET="$(date -u -d "+${PRIMARY_DELAY_SEC} seconds" '+%Y-%m-%d %H:%M:%S UTC')"
SECONDARY_TARGET="$(date -u -d "+${SECONDARY_DELAY_SEC} seconds" '+%Y-%m-%d %H:%M:%S UTC')"

setsid bash -lc \
  '"$0" --pod-id "$1" --env-file "$2" --start-after-sec "$3" --retries "$4" --retry-delay-sec "$5" --log-file "$6"' \
  "$REMOVE_SCRIPT" \
  "$POD_ID" \
  "$ENV_FILE" \
  "$PRIMARY_DELAY_SEC" \
  "$RETRIES" \
  "$RETRY_DELAY_SEC" \
  "$PRIMARY_LOG" \
  >/dev/null 2>&1 < /dev/null &
echo "$!" > "$PRIMARY_PID_FILE"

setsid bash -lc \
  '"$0" --pod-id "$1" --env-file "$2" --start-after-sec "$3" --retries "$4" --retry-delay-sec "$5" --log-file "$6"' \
  "$REMOVE_SCRIPT" \
  "$POD_ID" \
  "$ENV_FILE" \
  "$SECONDARY_DELAY_SEC" \
  "$RETRIES" \
  "$RETRY_DELAY_SEC" \
  "$SECONDARY_LOG" \
  >/dev/null 2>&1 < /dev/null &
echo "$!" > "$SECONDARY_PID_FILE"

sleep 2
ps -p "$(cat "$PRIMARY_PID_FILE")" >/dev/null 2>&1 || {
  printf 'Primary auto-remove watchdog failed to stay alive.\n' >&2
  exit 1
}
ps -p "$(cat "$SECONDARY_PID_FILE")" >/dev/null 2>&1 || {
  printf 'Secondary auto-remove watchdog failed to stay alive.\n' >&2
  exit 1
}

printf 'armed_at=%s\npod_id=%s\nprimary_target=%s\nsecondary_target=%s\nprimary_pid=%s\nsecondary_pid=%s\n' \
  "$(timestamp_utc)" \
  "$POD_ID" \
  "$PRIMARY_TARGET" \
  "$SECONDARY_TARGET" \
  "$(cat "$PRIMARY_PID_FILE")" \
  "$(cat "$SECONDARY_PID_FILE")" > "$SCHEDULE_FILE"

cat "$SCHEDULE_FILE"
ps -fp "$(cat "$PRIMARY_PID_FILE")" "$(cat "$SECONDARY_PID_FILE")"
