# Sphota.AI - Hybrid Intent Resolution Engine

**Status:** ✅ **Production Ready**  
**All Errors Resolved:** ✅ **YES**  

---

## 🎯 Quick Start

### Start the Engine (Docker)

**Windows:**
```powershell
.\start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

### API Endpoints

- **Base API:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`
- **API Specification:** `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
├── core/              # Engine implementation (hybrid architecture)
├── data/              # Intent corpus and datasets
├── docs/              # Complete documentation
├── tests/             # Test suite
├── examples/          # Usage examples
├── scripts/           # Utility scripts
├── docker-compose.yml # Multi-container orchestration
├── Dockerfile         # Container build spec
├── requirements.txt   # Python dependencies
├── main.py           # Entry point
└── README.md         # Full documentation
```

---

## ✨ Key Features

- **Hybrid Intent Resolution:** Two-stage semantic + deterministic processing
- **Vector Memory:** Real-time ambiguity resolution with ChromaDB
- **Context-Aware:** 12 dynamic context factors
- **Privacy-First:** Runs entirely locally
- **Production Ready:** Fully containerized with Docker

---

## 📖 Documentation

See `docs/` folder for:
- Architecture documentation
- Docker deployment guide
- API usage examples
- Configuration options
- Troubleshooting guides

---

## 🔧 Development

### Run Tests
```bash
python run_tests.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Build Docker Images
```bash
docker-compose build
```

---

## 📋 Recent Fixes

**All errors have been resolved:**
- ✅ ChromaDB import issues fixed
- ✅ Timestamp type handling fixed
- ✅ Workspace organized
- ✅ Python 3.14 compatibility ensured

**See:** `ERROR_RESOLUTION_REPORT.md` for details

---

## 🚀 Deploy

### Option 1: Docker (Recommended)
```bash
./start.sh          # macOS/Linux
.\start.bat         # Windows
```

### Option 2: Manual Docker Compose
```bash
docker-compose build
docker-compose up -d
```

### Option 3: Local Development
```bash
pip install -r requirements.txt
python main.py
```

---

## 📞 Support

- Check `docs/` for comprehensive guides
- Review error logs: `docker-compose logs`
- See `ERROR_RESOLUTION_REPORT.md` for recent fixes

---

**Ready to deploy! 🎉**
