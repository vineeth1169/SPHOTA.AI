# Docker Setup & Deployment Guide

## Overview

Sphota Engine is now fully containerized with Docker and Docker Compose for seamless deployment. The setup includes:

- **FastAPI Microservice** on Python 3.10 with Uvicorn
- **MySQL 8.0 Database** with persistent volumes
- **Pre-downloaded AI Model** (all-MiniLM-L6-v2) for zero-wait startup
- **Multi-stage Docker build** for optimized image size
- **Health checks** for both services

## Quick Start (One Command)

```bash
# Clone the repository
git clone https://github.com/vineeth1169/SPHOTA.AI.git
cd SPHOTA.AI

# Copy environment file
cp .env.example .env

# Start both services
docker-compose up
```

That's it! The API will be available at `http://localhost:8000` within 60 seconds.

## Detailed Setup

### Prerequisites

- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Disk Space**: ~3GB (includes cached models)

### Installation

#### macOS & Linux
```bash
# Install Docker Desktop (includes Compose)
# Visit: https://www.docker.com/products/docker-desktop
```

#### Windows (PowerShell)
```bash
# Using Chocolatey
choco install docker-desktop
```

### Starting the Engine

#### Development Mode (with auto-reload)
```bash
docker-compose up
```

#### Production Mode (multi-worker)
Uncomment this line in `docker-compose.yml`:
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Then restart:
```bash
docker-compose up --build
```

### Environment Configuration

Edit `.env` file to customize:

```env
# Database credentials
DB_USER=sphota_user
DB_PASSWORD=your_secure_password
DB_NAME=sphota_db

# API settings
LOG_LEVEL=info
API_PORT=8000

# Model
SBERT_MODEL=all-MiniLM-L6-v2
```

## Architecture

### Dockerfile Strategy

**Stage 1: Builder**
- Installs build dependencies
- Downloads Python packages
- **Pre-caches the 300MB AI model** using `SentenceTransformers`
- Result: Model is baked into image, no runtime download

**Stage 2: Runtime**
- Slim Python 3.10 base (only 150MB)
- Copies virtual environment from builder
- Only includes runtime dependencies (mysql-client)
- Final image: ~600MB (including model)

### docker-compose.yml Structure

```
┌─────────────────────────────────────────┐
│      Docker Compose Network             │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  sphota_api (FastAPI)            │   │
│  │  - Port: 8000                    │   │
│  │  - Volume: ./app (dev)           │   │
│  │  - Depends on: sphota_db         │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  sphota_db (MySQL 8.0)           │   │
│  │  - Port: 3306                    │   │
│  │  - Volume: sphota_db_volume      │   │
│  │  - Health Check: ENABLED         │   │
│  └──────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Volumes

**sphota_db_volume**
- Persists MySQL data across container restarts
- Located: `/var/lib/docker/volumes/sphota_db_volume/_data`
- Data survives: container stop, rebuild, restart

**huggingface_cache**
- Caches HuggingFace models
- Prevents re-downloading on container updates

### Networking

Both services communicate via the `sphota_network` bridge:

```
API → sphota_db:3306 (internal Docker DNS)
```

No localhost/127.0.0.1 needed - Docker handles service discovery.

## API Endpoints

Once running:

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T19:45:00Z"
}
```

### Resolve Intent
```bash
curl -X POST http://localhost:8000/resolve-intent \
  -H "Content-Type: application/json" \
  -d '{
    "command_text": "Go to the bank",
    "context": {
      "ctx_location": "Nature/Wilderness"
    }
  }'
```

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Access

### From Host Machine
```bash
mysql -h localhost -u sphota_user -p -D sphota_db
```

Enter password: `sphota_secure_password` (or your custom value)

### Inside Container
```bash
docker exec -it sphota_db mysql -u sphota_user -p -D sphota_db
```

## Useful Commands

### View Logs
```bash
# API logs
docker-compose logs sphota_api -f

# Database logs
docker-compose logs sphota_db -f

# All logs
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Full Reset (Delete Data)
```bash
docker-compose down -v
# This removes volumes, data is lost
```

### Rebuild Image
```bash
docker-compose build --no-cache
docker-compose up
```

### Scale API Instances
```bash
docker-compose up --scale sphota_api=3 sphota_db=1
```

### Inspect Container
```bash
# Get shell access
docker exec -it sphota_api bash

# Check environment variables
docker exec sphota_api env | grep DB_
```

## Performance Optimization

### Model Caching Benefits

The pre-downloaded model in the Docker image provides:

- **First Run**: 50 seconds (no model download)
- **vs Traditional**: 5+ minutes (downloading 300MB model)
- **Faster Iterations**: Each rebuild reuses model cache

### Build Time Optimization

```bash
# First build: ~5 minutes (downloads model)
docker-compose build

# Subsequent rebuilds: ~1 minute (cached layers)
docker-compose build
```

### Database Optimization

MySQL configuration in `docker-compose.yml`:

```
- max_connections=1000
- character-set=utf8mb4
- collation=utf8mb4_unicode_ci
```

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill process (macOS/Linux)
kill -9 <PID>

# Or use different port in .env
API_PORT=8001
```

### Database Connection Failed
```bash
# Check database is running
docker-compose logs sphota_db

# Verify health
docker-compose ps

# Restart database
docker-compose restart sphota_db
```

### Out of Memory
```bash
# Increase Docker memory allocation in Docker Desktop settings
# Settings > Resources > Memory (increase to 4GB+)

# Or reduce model size
SBERT_MODEL=all-MiniLM-L6-v2  # Lightweight option
```

### Image Build Failed
```bash
# Clear build cache and rebuild
docker-compose build --no-cache --progress=plain

# Check for specific error in output
```

## Production Deployment

### Pre-Production Checklist

- [ ] Set strong passwords in `.env`
- [ ] Disable `--reload` in Dockerfile
- [ ] Use `--workers 4` for Uvicorn
- [ ] Set `LOG_LEVEL=warning`
- [ ] Enable HTTPS/TLS at load balancer
- [ ] Configure MySQL backups
- [ ] Set resource limits in `docker-compose.yml`

### Resource Limits

Add to `sphota_api` in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### Kubernetes Deployment

Extract images for K8s:

```bash
# Build and tag images
docker-compose build
docker tag sphota-api:latest registry.example.com/sphota-api:v1.0.0
docker tag mysql:8.0 registry.example.com/sphota-db:v1.0.0

# Push to registry
docker push registry.example.com/sphota-api:v1.0.0
docker push registry.example.com/sphota-db:v1.0.0
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: docker/setup-buildx-action@v1
      - run: docker-compose build
      - run: docker-compose up -d
      - run: curl http://localhost:8000/health
```

## Support & Issues

For issues or questions:

1. Check logs: `docker-compose logs`
2. Review `.env` configuration
3. Ensure Docker & Compose are up-to-date
4. File issue: https://github.com/vineeth1169/SPHOTA.AI/issues

---

**Status:** ✅ Production-Ready | **Version:** 1.0.0 | **Last Updated:** Jan 17, 2026
