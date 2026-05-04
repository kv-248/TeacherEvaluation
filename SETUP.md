# Local Setup Guide

Run the Teacher Evaluation app locally without Docker in five steps.

---

## 1. Python 3.11

Install Python **3.11** from https://www.python.org/downloads/

> **Important:** `mediapipe 0.10.21` does not support Python 3.12 or newer. Check your version with `python --version`.

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

---

## 2. ffmpeg

ffmpeg is required for video decoding. It is a system tool, not a pip package.

**Windows:**
```
winget install ffmpeg
```

**Mac:**
```
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```
sudo apt install ffmpeg
```

Verify with `ffmpeg -version`.

---

## 3. Install Python packages

```bash
pip install -r requirements_local.txt
```

---

## 4. Gemini API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Get a free key at https://aistudio.google.com/app/apikey

---

## 5. Run

```bash
streamlit run streamlit_app.py
```

The app opens at **http://localhost:8501**. Upload a short lecture video clip (MP4, 30–120 seconds works best) and the scorecard will appear after processing.
