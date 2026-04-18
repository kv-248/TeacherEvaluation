#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE="$SCRIPT_DIR/.env"
if [[ ! -f "$ENV_FILE" ]] || ! grep -Eq '^[[:space:]]*GEMINI_API_KEY[[:space:]]*=[[:space:]]*[^[:space:]#]+' "$ENV_FILE"; then
  echo "Gemini API key not found in $ENV_FILE." >&2
  echo "Docker runs now use .env as the single source of truth. Add GEMINI_API_KEY=... to TeacherEvaluation/.env." >&2
  exit 1
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
