#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: auto_remove_pod.sh --pod-id POD_ID [options]

Remove a Runpod pod after an optional delay, with retries.

Options:
  --pod-id POD_ID            Literal Runpod pod id to remove. Required.
  --env-file PATH            Env file that defines RUNPOD_API_KEY. Default: /workspace/.env
  --start-after-sec N        Sleep N seconds before attempting removal. Default: 0
  --retries N                Number of remove attempts. Default: 60
  --retry-delay-sec N        Seconds between remove attempts. Default: 60
  --log-file PATH            Log file path. Default: /tmp/runpod_auto_remove_POD_ID.log
  --preflight                Authenticate and verify `runpodctl get pod`, but do not remove.
  -h, --help                 Show this help text.

Examples:
  auto_remove_pod.sh --pod-id 123abc --preflight
  auto_remove_pod.sh --pod-id 123abc --start-after-sec 10800 --retries 60
EOF
}

timestamp_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

log_line() {
  local message="$1"
  printf '[%s] %s\n' "$(timestamp_utc)" "$message" | tee -a "$LOG_FILE"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  }
}

POD_ID=""
ENV_FILE="/workspace/.env"
START_AFTER_SEC=0
RETRIES=60
RETRY_DELAY_SEC=60
LOG_FILE=""
PREFLIGHT=false

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
    --start-after-sec)
      START_AFTER_SEC="${2:-}"
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
    --log-file)
      LOG_FILE="${2:-}"
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

if [[ -z "$POD_ID" ]]; then
  printf -- '--pod-id is required.\n\n' >&2
  usage >&2
  exit 1
fi

if [[ -z "$LOG_FILE" ]]; then
  LOG_FILE="/tmp/runpod_auto_remove_${POD_ID}.log"
fi

require_cmd runpodctl

if [[ ! -f "$ENV_FILE" ]]; then
  printf 'Env file not found: %s\n' "$ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ -z "${RUNPOD_API_KEY:-}" ]]; then
  printf 'RUNPOD_API_KEY missing after sourcing %s\n' "$ENV_FILE" >&2
  exit 1
fi

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log_line "configuring runpodctl for pod ${POD_ID}"
runpodctl config --apiKey "$RUNPOD_API_KEY" >/dev/null 2>&1

log_line "verifying pod visibility via runpodctl get pod ${POD_ID}"
runpodctl get pod "$POD_ID" >/dev/null

if [[ "$PREFLIGHT" == "true" ]]; then
  log_line "preflight completed successfully; no removal attempted"
  exit 0
fi

if (( START_AFTER_SEC > 0 )); then
  log_line "sleeping ${START_AFTER_SEC}s before removal attempts"
  sleep "$START_AFTER_SEC"
fi

attempt=1
while (( attempt <= RETRIES )); do
  log_line "remove attempt ${attempt}/${RETRIES} for pod ${POD_ID}"
  if runpodctl remove pod "$POD_ID"; then
    log_line "remove command succeeded for pod ${POD_ID}"
    exit 0
  fi
  if (( attempt < RETRIES )); then
    log_line "remove attempt ${attempt} failed; sleeping ${RETRY_DELAY_SEC}s before retry"
    sleep "$RETRY_DELAY_SEC"
  fi
  attempt=$((attempt + 1))
done

log_line "all ${RETRIES} remove attempts failed for pod ${POD_ID}"
exit 1
