# ============================================================
# Weather Dashboard — Production Dockerfile
# Multi-stage build: slim Python 3.11 → Gunicorn on port 5050
# ============================================================

FROM python:3.11-slim AS base

# Metadata
LABEL maintainer="sai-nayan" \
      description="Weather Dashboard — Cloud-Native Flask Application" \
      version="1.0.0"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# --------------- Application Setup ---------------

# Create a non-root application user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set the working directory
WORKDIR /home/appuser/app

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY config.py run.py ./
COPY app/ ./app/
COPY tests/ ./tests/

# Create directories for persistent data and logs
RUN mkdir -p /home/appuser/app/instance /home/appuser/app/logs && \
    chown -R appuser:appuser /home/appuser/app

# Switch to non-root user
USER appuser

# --------------- Runtime Configuration ---------------

# Environment variables
ENV FLASK_ENV=production \
    PORT=5050 \
    SECRET_KEY=change-me-in-production \
    DATABASE_URL=sqlite:////home/appuser/app/instance/weather.db \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=4 \
    GUNICORN_TIMEOUT=120

# Expose the application port
EXPOSE 5050

# Health check — verify the /health endpoint responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5050/health || exit 1

# Start Gunicorn WSGI server (logging to stdout/stderr for Docker log capture)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS} --threads ${GUNICORN_THREADS} --timeout ${GUNICORN_TIMEOUT} --access-logfile - --error-logfile - 'run:app'"]
