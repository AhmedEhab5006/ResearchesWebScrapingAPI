# Multi-stage build for optimized Django + Celery application
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt && \
    pip install --user --no-cache-dir gunicorn==23.0.0

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 django && \
    mkdir -p /app/staticfiles && \
    mkdir -p /app/media && \
    mkdir -p /app/logs && \
    chown -R django:django /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=django:django /root/.local /home/django/.local

# Copy application code
COPY --chown=django:django . .

# Copy entrypoint script
COPY --chown=django:django docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set PATH to include user site-packages
ENV PATH=/home/django/.local/bin:$PATH

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check for web server
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /home/django/.local/bin/python -c "import urllib.request; urllib.request.urlopen('http://172.1.50.98:8000/').read()" || exit 1

# Use entrypoint script to manage both Celery and Gunicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]