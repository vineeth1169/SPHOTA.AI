# Docker Setup & Launch Guide for Hybrid Sphota Engine

## 📦 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)
- ~6GB free disk space (for images, volumes, and ChromaDB cache)
- Port 8000 (API), 3306 (MySQL) available

**Check Installation:**
```bash
docker --version
docker-compose --version
```

---

## 🚀 Quick Start

### Option 1: Windows (PowerShell)

```powershell
# Navigate to project root
cd C:\Users\vinee\Sphota.AI

# Run the startup script
.\start.bat

# To rebuild images
.\start.bat rebuild

# To view logs
.\start.bat logs
```

### Option 2: macOS/Linux (Bash)

```bash
# Navigate to project root
cd ~/path/to/Sphota.AI

# Make script executable
chmod +x start.sh

# Run the startup script
./start.sh

# To rebuild images
./start.sh --rebuild

# To view logs
./start.sh --logs
```

### Option 3: Manual Docker Compose Commands

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sphota_api

# Stop services
docker-compose down
```

---

## 📋 What Gets Set Up

### Services Started

| Service | Port | Purpose |
|---------|------|---------|
| **sphota_api** | 8000 | FastAPI server (Hybrid Intent Engine) |
| **sphota_db** | 3306 | MySQL 8.0 database |

### Volumes Created

| Volume | Purpose | Data Persistence |
|--------|---------|-------------------|
| `sphota_db_volume` | MySQL data | ✅ Persists between restarts |
| `huggingface_cache` | SBERT models | ✅ Cached for faster startup |
| `chroma_data` | ChromaDB vectors | ✅ **Semantic memory preserved** |

### Tables Created (Via Migrations)

1. **intents** - Intent corpus with embeddings
2. **resolved_intents** - Hybrid resolution results
3. **feedback** - Real-time learning feedback
4. **context_history** - Context factor history

---

## 🔗 Access the Engine

Once startup completes, access:

- **API Base:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

**Example API Call:**
```bash
curl -X POST http://localhost:8000/resolve \
  -H "Content-Type: application/json" \
  -d '{"user_input": "play music", "context": {"location": "bedroom"}}'
```

---

## 📝 Configuration

### Environment Variables

Edit `.env.docker` to customize:

```env
# Database
DB_HOST=sphota_db
DB_PORT=3306
DB_USER=sphota_user
DB_PASSWORD=sphota_secure_password
DB_NAME=sphota_db

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Model
SBERT_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMA_DATA_PATH=/app/chroma_data
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000         # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process (replace PID with actual process ID)
kill -9 <PID>         # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port in docker-compose.yml
```

### Issue: Database Connection Failed

```bash
# Check database logs
docker-compose logs sphota_db

# Verify database is running
docker-compose ps

# Restart database
docker-compose restart sphota_db
```

### Issue: API Container Not Starting

```bash
# Check API logs
docker-compose logs sphota_api

# Rebuild from scratch
docker-compose down --volumes
./start.bat rebuild  # or ./start.sh --rebuild
```

### Issue: Permission Denied on start.sh (macOS/Linux)

```bash
chmod +x start.sh
./start.sh
```

---

## 📊 Monitoring

### View Real-time Logs

```bash
# API logs
docker-compose logs -f sphota_api

# Database logs
docker-compose logs -f sphota_db

# All logs
docker-compose logs -f
```

### Check Container Status

```bash
docker-compose ps

# Or detailed inspection
docker-compose exec sphota_api ps aux
docker-compose exec sphota_db mysql -u sphota_user -psphota_secure_password -e "SELECT COUNT(*) FROM intents;"
```

### Verify Volumes

```bash
# List volumes
docker volume ls | grep sphota

# Inspect volume
docker volume inspect sphota_chroma_data

# Check disk usage
du -sh chroma_data
```

---

## 🔄 Lifecycle Operations

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart sphota_api

# Restart with clean volumes (WARNING: loses data)
docker-compose down --volumes
docker-compose up -d
```

### Backup & Restore

```bash
# Backup database
docker-compose exec sphota_db mysqldump -u sphota_user -psphota_secure_password sphota_db > backup.sql

# Backup ChromaDB
tar -czf chroma_backup.tar.gz chroma_data/

# Restore database
docker-compose exec -T sphota_db mysql -u sphota_user -psphota_secure_password sphota_db < backup.sql

# Restore ChromaDB
tar -xzf chroma_backup.tar.gz
```

### Stop Services

```bash
# Graceful shutdown (preserves data)
docker-compose down

# Complete cleanup (removes volumes/networks)
docker-compose down --volumes
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│  (sphota_network)                       │
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ sphota_api (FastAPI)                ││
│ │ Port: 8000                          ││
│ │ - Hybrid Intent Engine              ││
│ │ - Real-time Learning API            ││
│ │ - Vector Search                     ││
│ └──────────┬──────────────────────────┘│
│            │                           │
│            │ TCP/3306                  │
│            ▼                           │
│ ┌─────────────────────────────────────┐│
│ │ sphota_db (MySQL 8.0)               ││
│ │ Port: 3306                          ││
│ │ - Intent Corpus                     ││
│ │ - Resolution History                ││
│ │ - Feedback Data                     ││
│ └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘

Persistent Volumes:
├── sphota_db_volume          (MySQL data)
├── huggingface_cache         (SBERT models)
└── chroma_data               (Vector DB)
```

---

## 📦 Files Updated

### `requirements.txt`
✅ Added `chromadb==0.4.22` (uncommented)
✅ Added `mysql-connector-python==8.2.0`
✅ Existing: fastapi, uvicorn, sentence-transformers

### `docker-compose.yml`
✅ Added `chroma_data` volume mount
✅ Added `chroma_data` volume definition
✅ API depends on database

### New Files
✅ `start.sh` - Linux/macOS launch script (bash)
✅ `start.bat` - Windows launch script (batch)
✅ `.env.docker` - Environment configuration (auto-created)

---

## 🔐 Security Notes

**Development Mode:**
- Credentials in plaintext in `.env.docker` (OK for local development)
- All ports exposed (OK for local development)
- Hot-reload enabled (OK for development)

**For Production:**
1. Use Docker secrets instead of environment variables
2. Restrict exposed ports
3. Use strong passwords
4. Enable SSL/TLS
5. Set resource limits
6. Use non-root user in Dockerfile
7. Implement proper backup strategy
8. Add monitoring/alerting

---

## 📈 Performance Tips

### Optimize Image Size
```bash
# Use multi-stage builds (already in Dockerfile)
# Remove development dependencies from production

# Build optimization
docker-compose build --no-cache  # Force rebuild, don't use cache
```

### Improve Startup Speed
```bash
# Keep huggingface_cache volume between rebuilds
# Don't use --volumes flag on docker-compose down
docker-compose down  # Preserves volumes
```

### Monitor Resource Usage
```bash
# Watch container stats
docker stats

# Limit resources (add to docker-compose.yml)
services:
  sphota_api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 🆘 Getting Help

### View Detailed Logs

```bash
# With timestamps
docker-compose logs --timestamps sphota_api

# Last 100 lines
docker-compose logs --tail 100 sphota_api

# Follow with timestamps
docker-compose logs --timestamps -f sphota_api
```

### Execute Commands Inside Container

```bash
# Python interpreter
docker-compose exec sphota_api python

# Check installed packages
docker-compose exec sphota_api pip list

# Test database connection
docker-compose exec sphota_api python -c "import mysql.connector; print('MySQL OK')"
```

### Health Checks

```bash
# Verify database
docker-compose exec sphota_db mysqladmin ping -u sphota_user -psphota_secure_password

# Test API endpoint
curl http://localhost:8000/health

# Check ChromaDB
docker-compose exec sphota_api python -c "import chromadb; print('ChromaDB OK')"
```

---

## 📚 Related Documentation

- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sphota Architecture](docs/HYBRID_ARCHITECTURE.md)

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2024
