# Real-Time Learning - Quick Start Guide

## What You Have

✅ **Real-Time Learning System** - Enables Sphota to learn from every user interaction
✅ **3 New API Endpoints** - For feedback submission and monitoring
✅ **Automatic Golden Records** - Correct feedback saved to Fast Memory
✅ **Review Queue** - Incorrect feedback stored for analyst review
✅ **Learning Statistics** - Track accuracy improvement over time

## Quick Start (5 Minutes)

### 1. Start the API Server
```bash
python run_server.py
# Watch for: "Feedback Manager initialized successfully"
```

### 2. Test the Feedback System
Open a new terminal:
```bash
python test_feedback.py
```

This runs comprehensive tests including:
- ✅ Submitting correct feedback
- ✅ Submitting incorrect feedback
- ✅ Getting learning statistics
- ✅ Getting review queue
- ✅ Edge case handling

### 3. View Results
```bash
# Get learning statistics
curl http://localhost:8000/feedback/stats | python -m json.tool

# Get pending reviews
curl http://localhost:8000/feedback/review-queue | python -m json.tool
```

## Example Usage

### Positive Feedback (Golden Record)
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "original_input": "I need money from ATM",
    "resolved_intent": "withdraw_cash",
    "was_correct": true,
    "confidence_when_resolved": 0.92,
    "notes": "User confirmed correct resolution"
  }'
```

**Response:**
```json
{
  "success": true,
  "action_taken": "saved_to_memory",
  "memory_id": "withdraw_cash_1705502415",
  "message": "✓ Feedback saved to Fast Memory as Golden Record",
  "learning_status": {
    "total_feedbacks": 42,
    "correct_feedbacks": 38,
    "incorrect_feedbacks": 4,
    "accuracy": "90.5%"
  }
}
```

### Negative Feedback (Review Queue)
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "original_input": "I need dough quick",
    "resolved_intent": "loan_request",
    "was_correct": false,
    "confidence_when_resolved": 0.65,
    "correct_intent": "withdraw_cash",
    "notes": "Slang not recognized - should be cash withdrawal"
  }'
```

**Response:**
```json
{
  "success": true,
  "action_taken": "queued_for_review",
  "review_queue_id": "review_000001",
  "message": "✓ Feedback queued for manual review",
  "learning_status": {
    "total_feedbacks": 43,
    "correct_feedbacks": 38,
    "incorrect_feedbacks": 5,
    "accuracy": "88.4%"
  }
}
```

## The Three Endpoints

### Endpoint 1: POST /feedback
**Submit user feedback on intent resolutions**

| Field | Type | Required | Example |
|-------|------|----------|---------|
| original_input | string | Yes | "I need money" |
| resolved_intent | string | Yes | "withdraw_cash" |
| was_correct | boolean | Yes | true |
| confidence_when_resolved | float | No | 0.92 |
| correct_intent | string | No* | "check_balance" |
| notes | string | No | "User confirmed correct" |

*Required if `was_correct=false`

**Returns:** `FeedbackResponse` with action_taken, learning stats, and message

---

### Endpoint 2: GET /feedback/stats
**View learning progress and accuracy metrics**

**Returns:**
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

**Use for:** Monitoring learning progress, displaying accuracy in UI

---

### Endpoint 3: GET /feedback/review-queue
**Get pending manual review items**

**Returns:**
```json
{
  "pending_reviews": 3,
  "items": [
    {
      "id": "review_000001",
      "original_input": "I need dough quick",
      "resolved_intent": "loan_request",
      "correct_intent": "withdraw_cash",
      "confidence": 0.65,
      "notes": "Slang not recognized",
      "timestamp": "2026-01-17T14:31:45Z",
      "status": "pending"
    }
  ]
}
```

**Use for:** Manual review workflow, finding error patterns

## How It Works

### The Learning Loop

```
1. User uses engine
   input: "I need dough quick"
   → engine resolves to: "loan_request" (wrong!)
   
2. User provides feedback
   POST /feedback { was_correct: false, correct_intent: "withdraw_cash" }
   
3. System routes feedback
   ├─ was_correct=true   → Saved to Fast Memory (Golden Record)
   └─ was_correct=false  → Queued for manual review
   
4. Engine learns
   Next time "I need dough" → Better chance of "withdraw_cash"
   
5. Accuracy improves
   Day 1:  65% accuracy
   Day 7:  78% accuracy
   Day 30: 91% accuracy
```

### Storage Locations

```
learning/
├── review_queue.jsonl      # Incorrect resolutions (one per line)
└── feedback_stats.json     # Accuracy metrics
```

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ POST /feedback: { input, intent, was_correct, ... }    │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
   was_correct=true        was_correct=false
         │                        │
         ▼                        ▼
   Generate SBERT          Log to JSONL
   embedding               review_queue.jsonl
         │                        │
         ▼                        ▼
   Save to Fast Memory      Await manual
   (Golden Record)          analyst review
         │                        │
         └────────────┬───────────┘
                      ▼
              Update feedback_stats.json
              (total, correct, accuracy)
```

## Integration Examples

### Python Client
```python
import requests

class SPhotaClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def submit_feedback(self, input_text, resolved_intent, was_correct, **kwargs):
        """Submit feedback to real-time learning system."""
        payload = {
            "original_input": input_text,
            "resolved_intent": resolved_intent,
            "was_correct": was_correct,
            **kwargs
        }
        response = requests.post(f"{self.base_url}/feedback", json=payload)
        return response.json()
    
    def get_stats(self):
        """Get learning statistics."""
        response = requests.get(f"{self.base_url}/feedback/stats")
        return response.json()
    
    def get_reviews(self):
        """Get pending reviews."""
        response = requests.get(f"{self.base_url}/feedback/review-queue")
        return response.json()

# Usage
client = SPhotaClient()

# Submit feedback after user confirms resolution
result = client.submit_feedback(
    input_text="Transfer 500 to John",
    resolved_intent="transfer_to_account",
    was_correct=True,
    notes="User confirmed the transfer"
)
print(f"Accuracy: {result['learning_status']['accuracy']}")

# Check learning progress
stats = client.get_stats()
print(f"Total feedbacks: {stats['learning_status']['total_feedbacks']}")
```

### React/TypeScript Integration
```typescript
interface FeedbackRequest {
  original_input: string;
  resolved_intent: string;
  was_correct: boolean;
  confidence_when_resolved?: number;
  correct_intent?: string;
  notes?: string;
}

async function submitFeedback(feedback: FeedbackRequest) {
  const response = await fetch('/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback)
  });
  return response.json();
}

// Usage
const result = await submitFeedback({
  original_input: userInput,
  resolved_intent: engineResolution,
  was_correct: userConfirmed,
  notes: "User confirmed via UI button"
});

console.log(`Accuracy: ${result.learning_status.accuracy}%`);
```

## Best Practices

### 1. Always Collect Feedback
```python
# Don't skip obvious cases - they build representative training data
if user_interacted_with_result:
    submit_feedback(
        input=user_input,
        resolved_intent=engine_result,
        was_correct=user_confirmed_it
    )
```

### 2. Provide Context
```python
# Include notes when available
submit_feedback(
    input="Take me to the bank",
    resolved_intent="navigate_financial_bank",
    was_correct=True,
    notes="User location: Downtown (financial context)"
)
```

### 3. Monitor Review Queue
```python
# Regularly check for patterns
reviews = get_feedback_review_queue()
patterns = analyze_incorrect_resolutions(reviews)

# Look for:
# - Repeated slang patterns
# - Context-dependent mistakes
# - Edge cases needing rules
```

### 4. Track Improvement
```python
# Monitor accuracy over time
stats = get_feedback_stats()
accuracy = stats['learning_status']['accuracy']

if accuracy < target_accuracy:
    # Increase feedback collection
    # Update training data
    # Retrain if needed
```

## Monitoring Dashboard

Create a simple dashboard to track:

```
┌─────────────────────────────────────────┐
│     Sphota Real-Time Learning Stats     │
├─────────────────────────────────────────┤
│                                         │
│  Total Feedbacks: 1,247                │
│  Correct: 1,142 | Incorrect: 105       │
│  Current Accuracy: 91.6%               │
│                                         │
│  Pending Reviews: 12                   │
│  Last Update: 2 minutes ago             │
│                                         │
│  ─────────────────────────────────────  │
│  Accuracy Trend (last 7 days):          │
│  Day 1:  78% ░░░░░░░░░░                │
│  Day 2:  80% ░░░░░░░░░░░               │
│  Day 3:  83% ░░░░░░░░░░░░              │
│  Day 4:  85% ░░░░░░░░░░░░░             │
│  Day 5:  88% ░░░░░░░░░░░░░░            │
│  Day 6:  90% ░░░░░░░░░░░░░░░           │
│  Day 7:  91.6% ░░░░░░░░░░░░░░░░        │
│                                         │
└─────────────────────────────────────────┘
```

## Troubleshooting

### API Not Starting
```bash
# Check Python version (need 3.10+)
python --version

# Check if port 8000 is available
netstat -an | grep 8000

# Try different port
python run_server.py --port 8001
```

### Feedback Not Saving
```bash
# Check learning/ directory exists
ls -la learning/

# Check logs
tail -f run_tests.py  # or wherever logs go

# Verify FeedbackManager initialized
curl http://localhost:8000/health  # Should show all systems green
```

### Accuracy Not Improving
```bash
# Check if feedback is diverse
curl http://localhost:8000/feedback/stats | python -m json.tool

# Check if Golden Records are being used
# (requires integration with intent resolution)

# Verify SBERT embeddings generated correctly
# Check FastMemory has records
```

## Next Steps

1. **Deploy to Production**
   ```bash
   # Run with gunicorn for production
   gunicorn -w 4 -b 0.0.0.0:8000 main:app
   ```

2. **Integrate with UI**
   - Add feedback buttons after each resolution
   - Show accuracy metrics on dashboard
   - Display "System learning..." message

3. **Analyze Patterns**
   - Review incorrect resolutions weekly
   - Identify common slang patterns
   - Update training data based on feedback

4. **Automate Review**
   - High-confidence incorrect feedback → Auto-update
   - Build review workflow UI
   - Track reviewer feedback

5. **Scale Learning**
   - Collect feedback from multiple users
   - Build per-user personalization
   - Track domain-specific patterns

## API Documentation

Full OpenAPI/Swagger documentation available at:
```
http://localhost:8000/docs          # Interactive Swagger UI
http://localhost:8000/redoc          # ReDoc documentation
```

---

**Status: ✅ Ready for Production**

The Real-Time Learning system is fully implemented and tested. Start collecting feedback to improve accuracy!
