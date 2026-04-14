# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies (for MoviePy and audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p outputs logs memory/storage

# Expose ports: 8000 (API/Dashboard), 8080 (Flask/Files)
EXPOSE 8000
EXPOSE 8080

# Start the Agency OS (FastAPI server)
CMD ["python", "src/server.py"]
