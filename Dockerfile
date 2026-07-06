FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for faster model loading
ENV HF_HUB_TIMEOUT=600 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HF_HOME=/app/.cache/huggingface \
    PYTHONUNBUFFERED=1

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY static/ static/
COPY data/ data/

# Create cache directory
RUN mkdir -p .cache/huggingface

# Expose port (Spaces uses 7860, others use 8000)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/api/health')"

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
