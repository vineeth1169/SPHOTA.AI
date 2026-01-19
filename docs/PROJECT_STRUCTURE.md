# Sphota.AI - Project Structure

## 📁 Directory Organization

```
Sphota.AI/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 main.py                      # FastAPI application entry point
│
├── 📁 core/                        # Core engine implementation
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── models.py                   # Pydantic data models
│   ├── context_engine.py           # Main context resolution engine
│   ├── context_manager.py          # Context state management
│   ├── context_matrix.py           # 12-factor weighting matrix
│   ├── context_weighter.py         # Factor weighting logic
│   ├── intent_engine.py            # Intent resolution pipeline
│   ├── normalization_layer.py      # Input normalization
│   ├── normalization_map.py        # Normalization rules
│   ├── pasyanti_engine.py          # Pasyanti context layer
│   ├── apabhramsa_layer.py         # Apabhramsa context layer
│   ├── apabhramsa_map.py           # Apabhramsa rules
│   ├── fast_memory.py              # ChromaDB integration
│   ├── fast_memory_simple.py       # Simple numpy fallback
│   └── feedback_manager.py         # Real-time learning feedback
│
├── 📁 tests/                       # Test suite
│   ├── __init__.py
│   ├── test_sphota.py              # Unit tests
│   ├── test_feedback.py            # Feedback system tests
│   ├── test_fast_memory_simple.py  # Fast memory tests
│   └── verify_fast_memory.py       # Fast memory verification
│
├── 📁 docs/                        # Documentation
│   ├── REAL_TIME_LEARNING.md       # Real-time learning guide
│   ├── START_HERE_REALTIME_LEARNING.md
│   ├── REAL_TIME_LEARNING_QUICKSTART.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── GITHUB_READY_REALTIME_LEARNING.md
│   ├── REALTIME_LEARNING_STATUS_REPORT.md
│   ├── REALTIME_LEARNING_DOCS_INDEX.md
│   ├── REALTIME_LEARNING_VISUAL_SUMMARY.md
│   ├── REALTIME_LEARNING_FINAL_VERIFICATION.md
│   ├── REALTIME_LEARNING_DELIVERY_SUMMARY.txt
│   ├── FAST_MEMORY_COMPLETE.md
│   ├── FAST_MEMORY_IMPLEMENTATION.md
│   └── FAST_MEMORY_PYTHON314.md
│
├── 📁 data/                        # Data files
│   └── intents.json                # Intent definitions
│
├── 📁 scripts/                     # Utility scripts
│   └── [utility scripts]
│
├── 📁 examples/                    # Example usage
│   └── [usage examples]
│
├── 📁 docker/                      # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── 🔧 Configuration Files
    ├── .env                        # Environment variables
    ├── .env.example               # Example environment file
    ├── .gitignore                 # Git ignore rules
    └── .dockerignore              # Docker ignore rules
```

---

## 📂 Folder Purposes

### `core/`
**Purpose:** Core engine implementation  
**Contains:** All Sphota engine classes and logic  
**Key Files:**
- `context_engine.py` - Main resolution engine
- `intent_engine.py` - Intent resolution pipeline
- `models.py` - Data models (ContextModel, IntentRequest, FeedbackRequest, etc.)

### `tests/`
**Purpose:** Test suite  
**Contains:** Unit tests, integration tests, verification scripts  
**Key Files:**
- `test_sphota.py` - Core engine tests
- `test_feedback.py` - Real-time learning tests
- `verify_fast_memory.py` - Fast Memory verification

### `docs/`
**Purpose:** Documentation  
**Contains:** Guides, API docs, implementation guides  
**Key Files:**
- `REAL_TIME_LEARNING.md` - Complete learning system guide
- `START_HERE_REALTIME_LEARNING.md` - Entry point for learning
- `FAST_MEMORY_*.md` - Fast Memory documentation

### `data/`
**Purpose:** Data files  
**Contains:** Intent definitions, training data  
**Key Files:**
- `intents.json` - Intent mapping definitions

### `scripts/`
**Purpose:** Utility scripts  
**Contains:** Helper scripts for deployment, testing, etc.

### `examples/`
**Purpose:** Usage examples  
**Contains:** Example code, integration samples

---

## 🚀 Quick Navigation

### Getting Started
1. Read: [`README.md`](./README.md) - Project overview
2. Setup: Follow setup instructions in README
3. Run: `python main.py`

### Learning About Real-Time Learning
1. Start: [`docs/START_HERE_REALTIME_LEARNING.md`](./docs/START_HERE_REALTIME_LEARNING.md)
2. Deep dive: [`docs/REAL_TIME_LEARNING.md`](./docs/REAL_TIME_LEARNING.md)
3. Test: `python -m pytest tests/test_feedback.py`

### Learning About Fast Memory
1. Overview: [`docs/FAST_MEMORY_COMPLETE.md`](./docs/FAST_MEMORY_COMPLETE.md)
2. Implementation: [`docs/FAST_MEMORY_IMPLEMENTATION.md`](./docs/FAST_MEMORY_IMPLEMENTATION.md)

### Code Structure
1. Engine: `core/context_engine.py`
2. Models: `core/models.py`
3. Tests: `tests/test_*.py`

### Running Tests
```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_feedback.py

# With verbose output
pytest tests/ -v
```

### Running the API
```bash
# Development
python main.py

# Production
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

---

## 📊 File Organization Summary

| Type | Location | Purpose |
|------|----------|---------|
| **Code** | `core/` | Engine implementation |
| **Tests** | `tests/` | Test suite |
| **Docs** | `docs/` | Documentation |
| **Data** | `data/` | Intent definitions |
| **Config** | Root level | `.env`, `.gitignore`, etc. |
| **API** | `main.py` | FastAPI entry point |

---

## ✅ Organization Best Practices

### Adding New Files
1. **Code Files** → `core/` folder
2. **Test Files** → `tests/` folder
3. **Documentation** → `docs/` folder
4. **Data Files** → `data/` folder
5. **Utility Scripts** → `scripts/` folder
6. **Examples** → `examples/` folder

### File Naming Conventions
- **Python modules:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case()`
- **Constants:** `UPPER_CASE`
- **Documentation:** `DESCRIPTIVE_TITLE.md`

### Git Workflow
- Keep root clean (only essential files)
- Organize by function (code, tests, docs)
- Clear folder purposes
- Ignore unnecessary files (`.gitignore`)

---

## 🔗 Related Files

**Main Entry Point:**
- `main.py` - FastAPI application

**Configuration:**
- `.env` - Environment variables
- `requirements.txt` - Dependencies

**Docker:**
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container setup

**License:**
- `LICENSE` - MIT License

---

## 📝 Next Steps

1. Review the organized structure
2. Use `docs/START_HERE_REALTIME_LEARNING.md` for learning features
3. Run tests: `pytest tests/`
4. Check `core/` for code implementation

---

**Last Updated:** January 18, 2026
**Status:** ✅ Organized & Ready
