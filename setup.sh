#!/usr/bin/env bash
# setup.sh — one-shot local setup for Teacher Evaluation
# Works on macOS and Linux. Run once to create the venv and install deps,
# then the app starts automatically.
#
# Usage:
#   bash setup.sh          # setup + run
#   bash setup.sh --only-setup   # setup only, do not start the app

set -euo pipefail

VENV_DIR=".venv"
REQUIREMENTS="requirements_local.txt"
APP="streamlit_app.py"
ENV_FILE=".env"
ONLY_SETUP=false

for arg in "$@"; do
  [[ "$arg" == "--only-setup" ]] && ONLY_SETUP=true
done

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'
info()  { echo -e "${GREEN}[setup]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn] ${NC} $*"; }
abort() { echo -e "${RED}[error]${NC} $*"; exit 1; }

install_python311() {
  local PY_VER="3.11.9"
  local OS
  OS=$(uname -s 2>/dev/null)

  case "$OS" in
    Darwin)
      if command -v brew &>/dev/null 2>&1; then
        info "Installing Python $PY_VER via Homebrew..."
        brew install python@3.11
        PYTHON=$(brew --prefix python@3.11)/bin/python3.11
      else
        info "Downloading Python $PY_VER for macOS (~40 MB)..."
        curl -fL "https://www.python.org/ftp/python/${PY_VER}/python-${PY_VER}-macos11.pkg" \
          -o /tmp/python311.pkg
        sudo installer -pkg /tmp/python311.pkg -target /
        rm -f /tmp/python311.pkg
        PYTHON=$(command -v python3.11 2>/dev/null || echo "")
      fi
      ;;
    Linux)
      if command -v apt-get &>/dev/null 2>&1; then
        info "Installing Python $PY_VER via apt..."
        if command -v add-apt-repository &>/dev/null 2>&1; then
          sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
        fi
        sudo apt-get update -qq
        sudo apt-get install -y python3.11 python3.11-venv python3.11-distutils
        PYTHON=$(command -v python3.11 2>/dev/null || echo "")
      elif command -v dnf &>/dev/null 2>&1; then
        info "Installing Python $PY_VER via dnf..."
        sudo dnf install -y python3.11
        PYTHON=$(command -v python3.11 2>/dev/null || echo "")
      else
        abort "Cannot auto-install Python 3.11 on this system. Install it from https://www.python.org/downloads/"
      fi
      ;;
    MINGW*|CYGWIN*|MSYS*)
      if command -v winget &>/dev/null 2>&1; then
        info "Installing Python $PY_VER via winget..."
        winget install --id Python.Python.3.11 --silent \
          --accept-package-agreements --accept-source-agreements
        PYTHON="py -3.11"
      else
        info "Downloading Python $PY_VER installer for Windows (~25 MB)..."
        local EXE="/tmp/python311_installer.exe"
        curl -fL "https://www.python.org/ftp/python/${PY_VER}/python-${PY_VER}-amd64.exe" \
          -o "$EXE"
        "$EXE" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
        rm -f "$EXE"
        PYTHON="py -3.11"
      fi
      ;;
    *)
      abort "Unsupported OS '$OS'. Install Python 3.11 manually: https://www.python.org/downloads/"
      ;;
  esac

  [[ -z "$PYTHON" ]] && abort "Python 3.11 install failed. Install it manually: https://www.python.org/downloads/"
  VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "")
  [[ -z "$VERSION" ]] && abort "Python 3.11 not usable after install. Try again or install manually."
  info "Python $VERSION ready."
}

# ── 1. Python version check ───────────────────────────────────────────────────
info "Checking Python version..."
PYTHON=""
for candidate in python3.11 python3 python; do
  if command -v "$candidate" &>/dev/null; then
    VERSION=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    if [[ "$MAJOR" -eq 3 && "$MINOR" -eq 11 ]]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

# Windows py launcher: try py -3.11 (works even when python3.11 isn't on PATH)
if [[ -z "$PYTHON" ]] && command -v py &>/dev/null 2>&1; then
  if py -3.11 -c "import sys" &>/dev/null 2>&1; then
    PYTHON="py -3.11"
    VERSION="3.11"
    info "Found Python 3.11 via Windows py launcher (py -3.11)"
  fi
fi

if [[ -z "$PYTHON" ]]; then
  warn "Python 3.11 not found — auto-installing..."
  install_python311
else
  info "Found Python $VERSION at $PYTHON"
fi

# ── 2. ffmpeg check ───────────────────────────────────────────────────────────
info "Checking ffmpeg..."
if command -v ffmpeg &>/dev/null; then
  info "ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
  warn "ffmpeg not found on PATH."
  echo ""
  echo "  Install it before processing videos:"
  echo "    macOS:        brew install ffmpeg"
  echo "    Ubuntu/Debian: sudo apt install ffmpeg"
  echo ""
  echo "  Continuing setup — the app will start but video processing will fail without ffmpeg."
  echo ""
fi

# ── 3. Create virtual environment ─────────────────────────────────────────────
if [[ -d "$VENV_DIR" ]]; then
  info "Virtual environment already exists at $VENV_DIR — skipping creation."
else
  info "Creating virtual environment at $VENV_DIR..."
  $PYTHON -m venv "$VENV_DIR"
  info "Virtual environment created."
fi

# Detect venv layout (bin/ on Mac/Linux, Scripts/ on Windows)
if [[ -f "$VENV_DIR/bin/pip" ]]; then
  VENV_PYTHON="$VENV_DIR/bin/python"
  VENV_PIP="$VENV_DIR/bin/pip"
  VENV_STREAMLIT="$VENV_DIR/bin/streamlit"
else
  VENV_PYTHON="$VENV_DIR/Scripts/python"
  VENV_PIP="$VENV_DIR/Scripts/pip"
  VENV_STREAMLIT="$VENV_DIR/Scripts/streamlit"
fi

# ── 4. Install requirements ───────────────────────────────────────────────────
if [[ ! -f "$REQUIREMENTS" ]]; then
  abort "$REQUIREMENTS not found. Are you in the project root directory?"
fi

info "Installing packages from $REQUIREMENTS..."
"$VENV_PIP" install --upgrade pip --quiet
"$VENV_PIP" install -r "$REQUIREMENTS"
info "Packages installed."

# ── 5. Check .env / GEMINI_API_KEY ────────────────────────────────────────────
info "Checking API key..."
KEY_OK=false

if [[ -f "$ENV_FILE" ]]; then
  KEY=$(grep -E "^GEMINI_API_KEY=" "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]"')
  if [[ -n "$KEY" && "$KEY" != "your_key_here" ]]; then
    KEY_OK=true
    info "GEMINI_API_KEY found in $ENV_FILE."
  fi
fi

if [[ "$KEY_OK" == false ]]; then
  warn "GEMINI_API_KEY is not set."
  echo ""
  echo "  Create a .env file in this directory with:"
  echo "    GEMINI_API_KEY=your_key_here"
  echo ""
  echo "  Get a free key at: https://aistudio.google.com/app/apikey"
  echo ""
  echo "  The app will start but report generation will fail without a valid key."
  echo ""
fi

# ── 6. Run ────────────────────────────────────────────────────────────────────
if [[ "$ONLY_SETUP" == true ]]; then
  info "Setup complete. To start the app run:"
  echo "  $VENV_STREAMLIT run $APP"
  exit 0
fi

info "Starting Streamlit app..."
echo ""
echo "  App will open at http://localhost:8501"
echo "  Press Ctrl+C to stop."
echo ""
exec "$VENV_STREAMLIT" run "$APP"
