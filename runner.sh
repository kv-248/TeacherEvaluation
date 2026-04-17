#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE="$SCRIPT_DIR/.env"
if [[ -z "${GEMINI_API_KEY:-}" && -z "${GOOGLE_API_KEY:-}" ]]; then
  if [[ ! -f "$ENV_FILE" ]] || ! grep -Eq '^[[:space:]]*GEMINI_API_KEY[[:space:]]*=[[:space:]]*[^[:space:]#]+' "$ENV_FILE"; then
    echo "Gemini API key not found in shell environment or $ENV_FILE." >&2
    echo "Set GEMINI_API_KEY in the shell that runs Docker Compose, or add GEMINI_API_KEY=... to TeacherEvaluation/.env." >&2
    exit 1
  fi
fi

if [[ $# -eq 0 ]]; then
  set -- \
    --video samples/Lecture_1_cut_1m_to_5m.mp4 \
    --output-root /outputs/sample_run \
    --start-sec 92.5 \
    --duration-sec 60 \
    --analysis-fps 12 \
    --enable-semantic \
    --enable-coaching
fi

docker compose run --rm --no-deps --entrypoint python streamlit run_long_experiment.py "$@"
