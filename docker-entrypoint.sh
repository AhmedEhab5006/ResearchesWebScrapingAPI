#!/bin/bash
set -e

# Function to cleanup processes on exit
cleanup() {
    echo "Caught signal, shutting down gracefully..."
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null || true
        wait $CELERY_PID 2>/dev/null || true
    fi
    exit 0
}

# Trap SIGTERM and SIGINT for graceful shutdown
trap cleanup SIGTERM SIGINT

echo "=========================================="
echo "Django + Celery Application Startup"
echo "=========================================="

# Only run migrations and collectstatic on startup
if [ "$1" = "start" ] || [ -z "$1" ]; then
    echo ""
    echo "Step 1: Running Django migrations..."
    python manage.py migrate --noinput || echo "Migration failed, continuing anyway..."
    
    echo ""
    echo "Step 2: Collecting static files..."
    python manage.py collectstatic --noinput --clear || echo "Collectstatic failed, continuing anyway..."
    
    echo ""
    echo "Step 3: Starting Celery worker in background..."
    celery -A ResearchesWebScrapingAPI worker \
        -l ${CELERY_LOG_LEVEL:-info} \
        -P solo \
        --concurrency=1 \
        --logfile=/app/logs/celery.log \
        &
    CELERY_PID=$!
    echo "Celery worker started with PID: $CELERY_PID"
    
    echo ""
    echo "Step 4: Starting Gunicorn web server..."
    echo "=========================================="
    echo ""
    
    # Start Gunicorn in foreground
    exec gunicorn \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --worker-class sync \
        --worker-tmp-dir /dev/shm \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --timeout ${GUNICORN_TIMEOUT:-60} \
        --access-logfile - \
        --error-logfile - \
        ResearchesWebScrapingAPI.wsgi:application
fi

# Handle other commands
exec "$@"
