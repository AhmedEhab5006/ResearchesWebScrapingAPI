# Docker Setup Guide for Django + Celery Application

## Overview

This Docker setup provides a production-ready configuration for running a Django application with integrated Celery workers. Both the Django web server (Gunicorn) and Celery worker run in a single container for optimal resource efficiency.

## Architecture

```
┌─────────────────────────────────────────┐
│         Web Container (web)             │
├─────────────────────────────────────────┤
│  Gunicorn (Port 8000)                   │
│  Celery Worker (Solo Process)           │
└─────────────────────────────────────────┘
         ↓                    ↓
    ┌────────────┐      ┌─────────────┐
    │ PostgreSQL │      │    Redis    │
    │  Database  │      │   Broker    │
    └────────────┘      └─────────────┘
```

## Files

- **Dockerfile**: Multi-stage optimized build
  - Stage 1 (Builder): Compiles dependencies
  - Stage 2 (Runtime): Minimal runtime image with only necessary packages
  
- **docker-entrypoint.sh**: Startup script that:
  - Runs Django migrations
  - Collects static files
  - Starts Celery worker in background (solo process, single concurrency)
  - Starts Gunicorn as foreground process
  - Handles graceful shutdown of both processes
  
- **docker-compose.yml**: Orchestrates all services
  - PostgreSQL database
  - Redis message broker
  - Django + Celery web service
  - Optional Celery Beat for scheduled tasks
  
- **.dockerignore**: Excludes unnecessary files from build context
- **.env.example**: Template for environment variables

## Quick Start

### 1. Prepare Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Build and Start Services

```bash
# Build image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
```

### 3. Run Management Commands

```bash
# Within running container
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# One-off command
docker-compose run --rm web python manage.py custom_command
```

## Configuration

### Environment Variables (see .env.example)

**Django Settings:**
- `DEBUG`: Set to False in production
- `SECRET_KEY`: Change to a secure value
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains

**Database:**
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL user
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: Database hostname (use 'db' in Docker Compose)
- `DB_PORT`: Database port

**Redis (Cache & Celery Broker):**
- `REDIS_URL`: Redis connection string (use 'redis://redis:6379/0')

**Celery:**
- `CELERY_LOG_LEVEL`: Logging level (debug, info, warning)

**Gunicorn:**
- `GUNICORN_WORKERS`: Number of worker processes (default: 4)
- `GUNICORN_TIMEOUT`: Worker timeout in seconds (default: 60)

## Key Features

### 1. Multi-Stage Build
- **Builder stage**: Installs build dependencies and compiles Python packages
- **Runtime stage**: Minimal image with only runtime dependencies
- **Result**: Smaller image size (~1.2GB vs ~2GB+)

### 2. Security
- Non-root user (`django`) runs the application
- Proper file permissions and ownership
- Secrets managed via environment variables

### 3. Process Management
- Celery worker runs in background with solo pool and 1 concurrency
- Graceful shutdown handling via signal traps
- Both processes terminate cleanly on container stop

### 4. Static Files & Migrations
- Static files automatically collected on startup
- Migrations automatically run on startup
- Safe error handling if initial setup fails

### 5. Production Ready
- Gunicorn as WSGI server with configurable workers
- Health checks enabled
- Proper logging setup
- Volume management for persistent data

## Development vs Production

### Development (with live reload)

```bash
# Edit docker-compose.yml to uncomment the development command
command: bash -c "python manage.py runserver 0.0.0.0:8000 & celery -A ResearchesWebScrapingAPI worker -l info -P solo --concurrency=1"
```

### Production (current setup)

- Uses Gunicorn with multiple workers
- Single Celery worker with solo pool
- Graceful shutdown handling
- Health checks

## Troubleshooting

### Container won't start
```bash
# View startup logs
docker-compose logs web

# Run interactively for debugging
docker-compose run --rm web bash
```

### Database connection errors
```bash
# Verify database is running and healthy
docker-compose ps

# Check database logs
docker-compose logs db
```

### Celery worker not processing tasks
```bash
# Check Celery logs
docker-compose exec web tail -f /app/logs/celery.log

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

### Static files not serving
```bash
# Manually trigger collection
docker-compose exec web python manage.py collectstatic --clear --noinput
```

## Performance Tuning

### Worker Processes
Adjust `GUNICORN_WORKERS` based on CPU cores:
```
GUNICORN_WORKERS = 2 * CPU_CORES + 1
```

### Celery Concurrency
Currently set to 1 (solo process). For higher throughput:
- Modify entrypoint script to use prefork pool
- Adjust `--concurrency` parameter

### Memory Limits
Add to docker-compose.yml services section:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## Scaling

### Multiple Celery Workers
Create separate service in docker-compose.yml:
```yaml
celery-worker-2:
  build: .
  command: celery -A ResearchesWebScrapingAPI worker -l info -n worker-2
  depends_on:
    - db
    - redis
```

### Multiple Web Instances
Use Docker Swarm or Kubernetes with load balancer (nginx, HAProxy)

## SSL/HTTPS

For production, use reverse proxy (nginx) in front of Gunicorn:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://web:8000;
    }
}
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/
```

### Container Stats
```bash
docker stats
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web

# Follow logs
docker-compose logs -f web

# Last 50 lines
docker-compose logs --tail=50 web
```

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## References

- [Django Deployment with Gunicorn](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/gunicorn/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
