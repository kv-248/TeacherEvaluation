FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV, MediaPipe, and WeasyPrint (PDF generation)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt requirements_eval.txt ./
RUN pip install --no-cache-dir -r requirements_eval.txt

# Copy source code
COPY . .

# Set default command to run Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
