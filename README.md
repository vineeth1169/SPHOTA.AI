# Sphota: Cognitive Meaning Engine

## 🕉️ Project Overview

**Sphota** is an intent recognition engine based on **Bhartṛhari's Akhaṇḍapakṣa** (Sentence Holism) - a Sanskrit linguistic philosophy that meaning emerges from the totality of context, not from sequential word processing.

Unlike traditional Large Language Models that predict tokens sequentially, Sphota extracts **holistic sentence meaning** (Vākyasphoṭa) by combining:
- **Semantic similarity** via SBERT embeddings
- **12-Factor Context Resolution Matrix** applying Bhartṛhari's linguistic determinants
- **Apabhraṃśa normalization** to bridge slang/accents to pure meaning

### Key Philosophy

> *"Meaning is not in the words, but in the totality of context."* - Bhartṛhari

This implementation demonstrates that the same input utterance resolves to **different intents** based on contextual factors:
- **"take me to the bank"** → `river_bank` (in nature context with fishing activity)
- **"take me to the bank"** → `financial_bank` (in city context with money association)

---

## ✨ Features

### 1. **12-Factor Context Resolution Matrix (CRM)**
Implements all of Bhartṛhari's linguistic determinants:
- **Sahacarya** - Association/User history
- **Virodhitā** - Opposition/Contrast markers
- **Artha** - Purpose/Goal of utterance
- **Prakaraṇa** - Overall context/situation
- **Liṅga** - Grammatical/semantic signs
- **Śabda-sāmarthya** - Word capacity/strength
- **Aucitī** - Propriety/fitness score
- **Deśa** - Place/Location (GPS-aware)
- **Kāla** - Time/temporal context
- **Vyakti** - User profile/individualization
- **Svara** - Accent/intonation pattern
- **Apabhraṃśa** - Distortion/slang handling

### 2. **Apabhraṃśa Normalization Layer**
Bridges slang, accents, and code-switching to semantic meaning:
- Maps "no cap" → "truthfully"
- Handles "bruh lowkey fire" → normalized form
- 60+ slang mappings

### 3. **Pure Meanings Corpus**
Polysemic intent examples demonstrating context-aware resolution:
- River Bank vs. Financial Bank
- Lights On/Off with automation context
- Navigation, timers, music, etc.

### 4. **Semantic Vector Encoding**
Uses `sentence-transformers` (all-MiniLM-L6-v2) for fast, local embeddings:
- 384-dimensional vectors
- Normalized cosine similarity
- Pre-computed intent embeddings

### 5. **Interactive Streamlit Demo**
Visual demonstration showing:
- Raw AI scores vs. context-adjusted scores
- Color-coded boost/penalty indicators
- Side-by-side comparison
- Full explanation of resolution process

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  VAIKHARĪ LAYER (Input)                                     │
│  Raw user input: "take me to the bank"                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  APABHRAṂŚA LAYER (Normalization)                           │
│  Slang/accent normalization with distortion scoring         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  MADHYAMĀ LAYER (Semantic Processing)                       │
│  • SBERT embedding encoding                                 │
│  • Raw cosine similarity calculation                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CONTEXT RESOLUTION MATRIX (CRM)                            │
│  Apply 12-factor weighting:                                 │
│  - Deśa (location) boost relevant intents                   │
│  - Sahacarya (history) boost familiar patterns              │
│  - Artha (purpose) align with goals                         │
│  - ... (9 more factors)                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  PAŚYANTĪ LAYER (Flash of Insight)                          │
│  Resolved intent: financial_bank (confidence: 0.89)         │
│  Active factors: [desa, sahacarya, artha]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Sphota.AI/
├── core/
│   ├── __init__.py                    # Module exports
│   ├── context_matrix.py              # 12-Factor CRM implementation
│   ├── pasyanti_engine.py             # Main intent resolution engine
│   ├── apabhramsa_layer.py            # Slang normalization layer
│   └── __pycache__/
├── data/
│   └── intents.json                   # Pure Meanings corpus (12 polysemic intents)
├── tests/
│   ├── __init__.py
│   └── test_sphota.py                 # Comprehensive test suite (21+ tests)
├── app.py                             # Streamlit interactive demo
├── requirements.txt                   # Project dependencies
├── README.md                          # Project documentation
├── LICENSE                            # MIT License
├── FIXES_APPLIED.md                   # Technical fixes applied
├── README_TESTS.md                    # Test documentation
├── run_tests.py                       # Test runner
├── validate_all.py                    # Full validation script
└── .gitignore                         # Git ignore patterns
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Sphota.AI.git
cd Sphota.AI

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Interactive Demo

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

### Run Test Suite

```bash
# Full test suite
pytest tests/test_sphota.py -v

# Specific test class
pytest tests/test_sphota.py::TestContextWeighting -v

# Run only "bank" polysemic tests
pytest tests/test_sphota.py -k bank -v
```

### Validation

```bash
python validate_all.py
```

---

## 📊 Test Coverage

### Test Suite: 21+ Tests

#### 1. **TestContextWeighting** (3 tests)
- Bank polysemic resolution in financial context
- Bank polysemic resolution in nature context
- Context flips winner verification

#### 2. **TestApabhramsa** (4 tests)
- Slang normalization ("No cap" → "truthfully")
- Multiple slang terms handling
- Clean input pass-through
- Confidence score reduction with high distortion

#### 3. **TestTwelveFactorSchema** (6 tests)
- All 12 factors present
- Exactly 12 factors count
- Weight ranges validation
- Artha has highest weight
- Factor mappings initialized
- Active factors detection

#### 4. **TestZeroContextFallback** (4 tests)
- Empty context handling
- None context handling
- Highest raw probability wins
- Graceful degradation

#### 5. **TestIntegration** (3+ tests)
- Full pipeline with slang and context
- Multilingual code-switching
- Explanation generation

#### 6. **TestPerformance** (3+ tests)
- Large intent corpus
- Very long input
- Special characters

**Run tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/test_sphota.py -v
```

---

## 💻 Usage Example

```python
from core import PasyantiEngine, ContextObject
from datetime import datetime

# Initialize engine
engine = PasyantiEngine(intents_path="data/intents.json")

# Context 1: Nature scenario
context_nature = ContextObject(
    desa="nature",
    sahacarya=["fishing", "outdoor"],
    kala=datetime.now()
)

results = engine.resolve_intent("take me to the bank", context_nature)
print(results[0].intent.id)  # Output: river_bank

# Context 2: City scenario
context_city = ContextObject(
    desa="city",
    sahacarya=["money", "atm"],
    artha="finance"
)

results = engine.resolve_intent("take me to the bank", context_city)
print(results[0].intent.id)  # Output: financial_bank
```

---

## 🧠 Bhartṛhari's Philosophy

### Akhaṇḍapakṣa (Sentence Holism)
> "The meaning of a sentence is a unitary whole (sphoṭa), not a combination of word meanings."

**Traditional approach (token-based):**
- Process: "take" → "me" → "to" → "the" → "bank"
- Each word contributes incrementally
- Context lost in sequential processing

**Sphota approach (holistic):**
- Process: Entire utterance + ALL contextual factors together
- Meaning emerges from totality
- Context IS the meaning

### The 12 Factors
Bhartṛhari identified 12 linguistic determinants that resolve ambiguity. Sphota implements weighted factors that boost/penalize intent scores based on their presence in the context.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `sentence-transformers` | 5.2.0 | SBERT embeddings |
| `numpy` | 2.4.0 | Numerical operations |
| `torch` | 2.9.1 | Deep learning backend |
| `pydantic` | 2.12.5 | Data validation |
| `streamlit` | 1.52.2 | Web UI framework |
| `pytest` | 9.0.2 | Testing framework |
| `pytest-mock` | 3.15.1 | Mocking utilities |

---

## 🔬 Key Algorithms

### 1. Cosine Similarity Calculation
```
similarity = dot_product(embedding1, embedding2) / (norm1 × norm2)
```
Vectors are pre-normalized, so: `similarity = embedding1 · embedding2`

### 2. Context Resolution
```
context_adjusted_score = base_score + sum(factor_adjustments)
```
Each active factor contributes weighted boost/penalty.

### 3. Intent Selection
```
winner = argmax(context_adjusted_scores)
resolved_intents = sort_by_score(top_k)
```

---

## 🎯 Use Cases

1. **Voice Assistants** - Understand commands in context
2. **Chatbots** - Resolve ambiguous user intents
3. **Smart Home** - Context-aware automation ("lights on" differently in night vs. daytime)
4. **Accessibility Tools** - Understand accented/informal speech
5. **Linguistic Research** - Validate Bhartṛhari's theories computationally

---

## 🐛 Known Limitations

1. **Fixed Intent Corpus** - Currently 12 pre-defined intents (can be extended)
2. **No User Learning** - Vyakti (user profile) factor not dynamically learned
3. **Single Language** - English primary, limited multilingual support
4. **No Prosody** - Svara (accent/intonation) is placeholder
5. **Local Only** - No cloud integration or distributed processing

---

## 🔮 Future Work

- [ ] Dynamic intent discovery from user interactions
- [ ] Real GPS integration for Deśa factor
- [ ] Prosody analysis from audio (Whisper integration)
- [ ] User preference learning (Vyakti personalization)
- [ ] Multi-language support
- [ ] ChromaDB vector store integration
- [ ] REST API server
- [ ] Mobile app deployment

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

**Copyright © 2026 Sphota AI Contributors**

You are free to:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Use privately

Under the condition:
- ⚠️ Include license and copyright notice

---

## 🙏 Acknowledgments

- **Bhartṛhari** (5th century Sanskrit grammarian) - Theoretical foundation
- **Vaiseṣika School** - Philosophy of language and meaning
- **Sentence-BERT Team** - Embedding models
- **Streamlit Team** - Interactive UI framework

---

## 📚 References

1. Bhartṛhari. *Vākyapadīya* (5th century)
2. Iyer, K. A. S. (1969). *Vākyapadīya of Bhartṛhari with the Prakīrṇaprakāśikā*
3. Cardona, George. (1997). *Pāṇini: His Work and Its Traditions*
4. Reimers & Gurevych. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

---

## 📞 Contact & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email@example.com]

---

## ⭐ Citation

If you use Sphota in research, please cite:

```bibtex
@software{sphota2026,
  title={Sphota: Cognitive Meaning Engine},
  author={[Your Name]},
  year={2026},
  url={https://github.com/yourusername/Sphota.AI},
  note={Based on Bhartṛhari's Akhaṇḍapakṣa}
}
```

---

## 📖 Learn More

- [Test Documentation](README_TESTS.md)
- [Technical Fixes Applied](FIXES_APPLIED.md)
- [Core Architecture Details](core/context_matrix.py)

---

**Vākyasphoṭa through Code** 🕉️

*Extract holistic meaning, not token predictions.*
