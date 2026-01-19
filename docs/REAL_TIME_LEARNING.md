# Real-Time Learning Feedback Loop

## Overview

The **Real-Time Learning** system enables Sphota to continuously improve accuracy through user feedback. It transforms the engine from a static model into an adaptive system that learns from real-world usage patterns.

## Architecture

```
User Provides Feedback
        ↓
POST /feedback
        ↓
Feedback Manager decides:
    ├─ was_correct=True  → Save to Fast Memory (Golden Record)
    └─ was_correct=False → Queue for Manual Review (SQL)
        ↓
Engine learns automatically
```

## Endpoints

### 1. POST /feedback
Submit feedback on an intent resolution.

**Request:**
```json
{
  "original_input": "I need dough quick",
  "resolved_intent": "withdraw_cash",
  "was_correct": true,
  "confidence_when_resolved": 0.85,
  "notes": "Correctly resolved slang to cash withdrawal"
}
```

**Response (was_correct=True):**
```json
{
  "success": true,
  "action_taken": "saved_to_memory",
  "memory_id": "withdraw_cash_1705502415123",
  "message": "✓ Feedback saved to Fast Memory as Golden Record...",
  "learning_status": {
    "total_feedbacks": 42,
    "correct_feedbacks": 38,
    "incorrect_feedbacks": 4,
    "accuracy": "90.5%",
    "last_update": "2026-01-17T14:30:15Z"
  }
}
```

**Response (was_correct=False):**
```json
{
  "success": true,
  "action_taken": "queued_for_review",
  "review_queue_id": "review_000001",
  "message": "✓ Feedback queued for manual review (ID: review_000001)...",
  "learning_status": {
    "total_feedbacks": 43,
    "correct_feedbacks": 38,
    "incorrect_feedbacks": 5,
    "accuracy": "88.4%",
    "last_update": "2026-01-17T14:31:45Z"
  }
}
```

### 2. GET /feedback/stats
Get learning statistics and feedback metrics.

**Response:**
```json
{
  "learning_status": {
    "total_feedbacks": 100,
    "correct_feedbacks": 92,
    "incorrect_feedbacks": 8,
    "accuracy": 92.0,
    "last_update": "2026-01-17T15:00:00Z"
  },
  "timestamp": "2026-01-17T15:05:30Z"
}
```

### 3. GET /feedback/review-queue
Get pending manual review items.

**Response:**
```json
{
  "pending_reviews": 3,
  "items": [
    {
      "id": "review_000001",
      "original_input": "Need some bread",
      "resolved_intent": "loan_request",
      "correct_intent": "withdraw_cash",
      "confidence": 0.65,
      "notes": "Should have been cash withdrawal",
      "timestamp": "2026-01-17T14:31:45Z",
      "status": "pending",
      "processed_by": null
    }
  ],
  "timestamp": "2026-01-17T15:05:30Z"
}
```

## Files Generated

### Learning Data Structure
```
learning/
├── review_queue.jsonl      # Incorrect resolutions waiting for review
└── feedback_stats.json     # Aggregate learning statistics
```

### Review Queue Entry Format
```json
{
  "id": "review_000001",
  "original_input": "User's actual input",
  "resolved_intent": "What engine resolved to",
  "correct_intent": "What it should have been",
  "confidence": 0.65,
  "notes": "Optional user notes",
  "timestamp": "2026-01-17T14:31:45Z",
  "status": "pending",
  "processed_by": null
}
```

## Workflow Examples

### Example 1: Correct Resolution (Golden Record)

```python
# User input
original = "I need money from ATM"
context = {"location": "Bank"}

# Engine resolution
response = engine.resolve_intent(original, context)
# → resolved_intent: "withdraw_cash"
# → confidence: 0.92

# User confirms it's correct
feedback = {
    "original_input": "I need money from ATM",
    "resolved_intent": "withdraw_cash",
    "was_correct": True,
    "confidence_when_resolved": 0.92
}

result = client.post("/feedback", json=feedback)
# Action: Saved to Fast Memory
# Next time similar input arrives, engine remembers this
```

### Example 2: Incorrect Resolution (Review Queue)

```python
# User input with slang
original = "I need dough quick"
context = {"location": "Bank"}

# Engine misresolves
response = engine.resolve_intent(original, context)
# → resolved_intent: "borrow_money"  ❌ WRONG
# → confidence: 0.65

# User corrects
feedback = {
    "original_input": "I need dough quick",
    "resolved_intent": "borrow_money",
    "was_correct": False,
    "correct_intent": "withdraw_cash",
    "confidence_when_resolved": 0.65,
    "notes": "Should have resolved to cash withdrawal based on banking context"
}

result = client.post("/feedback", json=feedback)
# Action: Queued for manual review
# Analyst reviews and updates training data
```

### Example 3: Context Learning

```python
# First interaction
original = "Take me to the bank"
context = {"location": "Nature_Reserve"}
# → resolved_intent: "navigate_river_bank"

# User confirms
feedback = {
    "original_input": "Take me to the bank",
    "resolved_intent": "navigate_river_bank",
    "was_correct": True,
    "confidence_when_resolved": 0.94
}
client.post("/feedback", json=feedback)

# Later - similar input but different context
original = "Take me to the bank"
context = {"location": "Downtown"}
# With feedback saved: resolved_intent: "navigate_financial_bank"
# Engine learned context matters!
```

## Benefits

### 1. Cold-Start → Warm-Start
- **Day 1:** Engine uses training data only
- **After 100 interactions:** Engine learns user patterns
- **After 1000 interactions:** Engine fine-tuned to real usage

### 2. Handles Slang Automatically
```
"I need dough" → Learns "dough" = "money"
"Need some bread" → Learns "bread" = "money"
"Gimme cash" → Learns all slang variations
```

### 3. Context Matters
```
"Bank" + Location=Nature_Reserve → River bank
"Bank" + Location=Downtown → Financial bank
Engine learns both!
```

### 4. Real User Needs vs. Training Data
- Training: Theoretical scenarios
- Feedback: Actual user behavior
- Engine improves toward real needs

### 5. 100% Deterministic
- Same input + feedback = Same learning
- No randomness
- Full audit trail for compliance

## Learning Statistics

### Accuracy Metric
```
Accuracy = (correct_feedbacks / total_feedbacks) * 100
```

**Example:**
```
42 correct feedbacks
8 incorrect feedbacks
─────────────────────
50 total feedbacks

Accuracy = (42/50) * 100 = 84.0%
```

### Improvement Tracking
```json
{
  "day_1": {"accuracy": 0.65},
  "day_7": {"accuracy": 0.78},
  "day_30": {"accuracy": 0.91},
  "day_90": {"accuracy": 0.96}
}
```

## Integration Examples

### Python Client
```python
import requests

engine_url = "http://localhost:8000"

# Submit feedback
feedback = {
    "original_input": "Transfer 500 to John",
    "resolved_intent": "transfer_to_account",
    "was_correct": True,
    "confidence_when_resolved": 0.94,
    "notes": "User confirmed correct"
}

response = requests.post(f"{engine_url}/feedback", json=feedback)
print(response.json())

# Check learning progress
stats = requests.get(f"{engine_url}/feedback/stats").json()
print(f"Accuracy: {stats['learning_status']['accuracy']}")

# Check pending reviews
reviews = requests.get(f"{engine_url}/feedback/review-queue").json()
print(f"Pending reviews: {reviews['pending_reviews']}")
```

### cURL
```bash
# Submit positive feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "original_input": "I need money",
    "resolved_intent": "withdraw_cash",
    "was_correct": true,
    "confidence_when_resolved": 0.92
  }'

# Get learning stats
curl http://localhost:8000/feedback/stats

# Get review queue
curl http://localhost:8000/feedback/review-queue
```

## Best Practices

### 1. Capture All Feedback
```python
# Always provide feedback, even on obvious cases
# This builds a representative training set
```

### 2. Include Context When Available
```python
feedback = {
    "original_input": "...",
    "resolved_intent": "...",
    "was_correct": True,
    "notes": "User at banking location during business hours"
}
```

### 3. Monitor Review Queue
```python
# Regularly check for patterns in incorrect resolutions
reviews = client.get("/feedback/review-queue").json()

# Look for:
# - Repeated mistakes on same input
# - Slang patterns not yet learned
# - Edge cases needing context rules
```

### 4. Periodically Retrain
```python
# When review_queue grows large:
# 1. Analyze patterns
# 2. Update training data
# 3. Fine-tune weights
# 4. Re-deploy
```

## Compliance & Audit

### Full Audit Trail
- Every feedback logged with timestamp
- Every action (save/review) tracked
- Review queue searchable for compliance

### Data Retention
```
Golden Records: Indefinite (improving model)
Review Queue: 90 days + manual override
Feedback Stats: Indefinite (analytics)
```

### Privacy
- No user PII stored
- Only intent/context/feedback stored
- Compliant with GDPR, CCPA

## Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| **Accuracy** | Correct / Total * 100 | >90% |
| **Learning Velocity** | Accuracy improvement/day | >0.5% |
| **Review Rate** | Reviews / Total | <10% |
| **Golden Records** | Saved memories | Growing |
| **Cold-Start → Warm-Start** | Days to 90% accuracy | <30 days |

## Troubleshooting

### Review Queue Growing Too Large
```
Symptom: More than 20% incorrect resolutions
Solution:
1. Analyze patterns in reviews
2. Update context rules (CRM weights)
3. Retrain on corrected data
```

### Learning Not Improving
```
Symptom: Accuracy plateau after 100 feedbacks
Solution:
1. Check if feedback is diverse
2. Ensure context is complete
3. Verify Golden Records are being retrieved
```

### Memory Growing Too Large
```
Symptom: Fast Memory has 100K+ records
Solution:
1. Prune old low-confidence records
2. Consolidate duplicate inputs
3. Archive to cold storage
```

---

**Real-Time Learning:** Where Static Data Meets Adaptive AI ✨
