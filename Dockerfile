# Dockerfile for CPU-only deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose the API port (Render defaults to 10000)
EXPOSE 10000

# Set environment variables for the model
ENV MODEL_ID="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
ENV HF_HOME="/app/.cache"
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Command to run the application
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
