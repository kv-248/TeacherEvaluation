# Teacher Evaluation: Docker Deployment Guide

Welcome to the automated deployment guide for the Teacher Evaluation pipeline. This repository analyzes teacher lecture videos using computer vision heuristics and Google Gemini's Semantic AI to generate actionable coaching blueprints.

Due to the heavy requirements of OpenCV and PDF generation (WeasyPrint), **running this application via Docker is the officially supported and recommended path.** 

We have provided a zero-configuration containerization setup using `docker compose`.

---

## 1. Initial Setup

### Prerequisites
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
2. A valid [Google Gemini API Key](https://aistudio.google.com/app/apikey) (e.g., `gemini-2.5-flash` access).

### Step 1: Clone the Repository
Download the code to your local machine:
```bash
git clone git@github.com:YOUR_USERNAME/TeacherEvaluation.git
cd TeacherEvaluation
```

### Step 2: Inject Your API Key
The pipeline requires your Gemini API key to synthesize the final coaching reports.

To avoid hardcoding it in the code, export it in your active terminal session:
```bash
# On Mac/Linux:
export GEMINI_API_KEY="AIzaSyYourSecretKeyHere..."

# On Windows PowerShell:
$env:GEMINI_API_KEY="AIzaSyYourSecretKeyHere..."
```
*(Tip: for a stable "build once, run many times" workflow, create a `.env` file in the root of the repository containing `GEMINI_API_KEY=your_key`. The Docker runners now check for this before starting.)*

---

## 2. Using the Interactive UI (Streamlit)

If you want a visual interface to explore existing processed runs or to trigger new evaluations with a single click, use the Web UI.

### Start the Server
Run this command from the root of the repository:
```bash
docker compose up streamlit --build
```

If the image is already built and you have not changed dependencies or Docker-related files, you can reuse it without rebuilding:
```bash
docker compose up -d streamlit
```

### Access It
1. Wait for the terminal to say `You can now view your Streamlit app in your browser.`
2. Open your web browser and navigate to: [http://localhost:8501](http://localhost:8501)
3. From the left sidebar, choose a clip, toggle "Enable Semantic Review", and hit Run!

### Stop the Server
Press `Ctrl+C` in the terminal to cleanly shut down the container.

---

## 3. Using the Headless CLI (Batch Automator)

If you want to evaluate multiple videos automatically in the background (perfect for CI/CD or overnight processing runs), use the headless batch evaluator tool. 

### Run Default Batch (Smoke Test)
To automatically process a default batch of local clips (e.g., `crashcourse_moon_phases`, `studyiq_shah_bano_case`) and output the resulting markdown/PDF coaching reports to a timestamped directory:

```bash
docker compose run evaluator
```

### Run the Sample Long-Form Evaluation Without Rebuilding

Build once:
```bash
docker compose build streamlit
docker compose up -d streamlit
```

Then reuse the same built image for repeated evaluation requests:
```bash
bash runner.sh
```

On Windows PowerShell, use:
```powershell
.\runner.ps1
```

Both runners write host-visible outputs under:
`TeacherEvaluation/local_data/docker_test_outputs/`

### Check Gemini Auth Before a Long Run

If you want to confirm that the container not only sees a key but can actually call Gemini, run:

```bash
docker compose run --rm --no-deps --entrypoint python streamlit tools/check_gemini_auth.py
```

This distinguishes:
- key missing
- key present but rejected by the Gemini API
- key valid, but the requested model is unavailable for that key/project

### Run Custom Batch
To process specific target clips from your `clips/` folder, you can override the arguments passed to the python script:

```bash
docker compose run evaluator python evaluation/run_local_clips_gemini_batch.py \
  --clip-ids pd_classes_body_language_demo,harvard_mba_case_classroom \
  --output-dir evaluation/runtime_batches/my_custom_run
```

### Where to Find Your Reports
Once a batch run finishes, it generates a full directory of metrics, debugging plots, annotated keyframe thumbnails, and the final synthetic AI coaching report.
You can find these on your local machine at:
`TeacherEvaluation/evaluation/runtime_batches/`

---

## 4. Advanced: Injecting Custom Clips
The repository comes pre-loaded with over 50 lecture clips inside the `clips/` directory. 

To analyze your own custom video:
1. Create a subfolder inside `clips/` named playfully lowercase with underscores (e.g., `clips/my_math_lecture_1/`).
2. Place your video file inside that new subfolder and **name it exactly `clip.mp4`**.
3. Re-run the batch CLI tool targeting your exact folder name!
```bash
docker compose run evaluator python evaluation/run_local_clips_gemini_batch.py --clip-ids my_math_lecture_1
```
