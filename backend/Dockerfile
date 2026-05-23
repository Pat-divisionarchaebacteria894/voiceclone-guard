FROM python:3.11-slim

# System deps for librosa / soundfile / matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/models

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
