#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

OPEN_BROWSER="${OPEN_BROWSER:-1}"

log() {
  echo ""
  echo "==> $1"
}

run_docker() {
  MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" "$@"
}

log "Stopping any existing Streamlit service"
run_docker docker compose stop streamlit >/dev/null 2>&1 || true
run_docker docker compose rm -sf streamlit >/dev/null 2>&1 || true

log "Building the Streamlit image"
run_docker docker compose build streamlit

log "Starting the Streamlit service"
set +e
start_output="$(run_docker docker compose up -d --force-recreate streamlit 2>&1)"
start_code=$?
set -e
echo "$start_output"

if [[ $start_code -ne 0 ]]; then
  if grep -qi "port is already allocated" <<<"$start_output"; then
    echo ""
    echo "Port 8501 is still in use by another process or container."
    echo "Current Docker listeners on 8501:"
    run_docker docker ps --format 'table {{.Names}}\t{{.Ports}}' | grep '8501->' || true
    echo ""
    echo "Free the port, then rerun this script."
  fi
  exit "$start_code"
fi

echo ""
echo "Streamlit UI is starting."
echo "Open: http://localhost:8501"
echo "If you want live logs, run: docker compose logs -f streamlit"

if [[ "$OPEN_BROWSER" == "1" ]]; then
  cmd.exe /c start "" "http://localhost:8501" >/dev/null 2>&1 || true
fi
