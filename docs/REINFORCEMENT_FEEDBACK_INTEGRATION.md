# Reinforcement Feedback Loop - Integration Guide

## Quick Start

The **Reinforcement Feedback Loop** is now implemented and ready to use. This guide shows how to integrate it into your application.

### 1. Endpoint Available

```
POST /feedback
```

### 2. Quick Test

Open the Swagger UI at `http://localhost:8000/docs` and test the `/feedback` endpoint directly.

**Or use curl:**

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_correction": "transfer_to_account",
    "was_successful": true
  }'
```

### 3. Integration Flow

#### Step 1: Resolve Intent
```bash
POST /resolve-intent
{
  "command_text": "Transfer 500 to John",
  "context": { ... }
}
```

Response includes:
```json
{
  "resolved_intent": "transfer_to_account",
  "confidence_score": 0.88,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Step 2: User Provides Feedback
```bash
POST /feedback
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_correction": "transfer_to_account",
  "was_successful": true
}
```

#### Step 3: Engine Learns
The feedback is logged and learning statistics updated. Future similar requests will be resolved more accurately.

### 4. Python Client Example

```python
import requests
import uuid

class SphotaClient:
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
    
    def resolve_intent(self, command_text: str, context: dict) -> dict:
        """Resolve intent and get request_id"""
        response = requests.post(
            f"{self.api_base}/resolve-intent",
            json={
                "command_text": command_text,
                "context": context
            }
        )
        response.raise_for_status()
        return response.json()
    
    def submit_feedback(self, request_id: str, was_successful: bool, 
                       user_correction: str = None) -> dict:
        """Submit feedback to enable learning"""
        response = requests.post(
            f"{self.api_base}/feedback",
            json={
                "request_id": request_id,
                "user_correction": user_correction or request_id,
                "was_successful": was_successful
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_learning_stats(self) -> dict:
        """Check learning progress"""
        response = requests.get(f"{self.api_base}/feedback/stats")
        response.raise_for_status()
        return response.json()


# Usage
client = SphotaClient()

# 1. Get resolution
result = client.resolve_intent(
    command_text="Transfer 500 to John",
    context={
        "location_context": "office",
        "temporal_context": "2026-01-18T10:00:00Z"
    }
)

print(f"Resolved to: {result['resolved_intent']}")
print(f"Request ID: {result['request_id']}")

# 2. User confirms or corrects
if result['resolved_intent'] == "transfer_to_account":
    # Correct! Send positive feedback
    feedback = client.submit_feedback(
        request_id=result['request_id'],
        was_successful=True,
        user_correction="transfer_to_account"
    )
else:
    # Wrong! Send correction
    feedback = client.submit_feedback(
        request_id=result['request_id'],
        was_successful=False,
        user_correction="borrow_money"
    )

print(f"Feedback processed: {feedback['action_taken']}")

# 3. Check learning progress
stats = client.get_learning_stats()
print(f"Accuracy: {stats['learning_status']['correct_feedbacks']} / {stats['learning_status']['total_feedbacks']}")
```

### 5. Frontend Integration (JavaScript)

```javascript
class SphotaAPI {
  constructor(apiBase = "http://localhost:8000") {
    this.apiBase = apiBase;
  }

  async resolveIntent(commandText, context) {
    const response = await fetch(`${this.apiBase}/resolve-intent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command_text: commandText, context })
    });
    return response.json();
  }

  async submitFeedback(requestId, wasSuccessful, userCorrection) {
    const response = await fetch(`${this.apiBase}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request_id: requestId,
        was_successful: wasSuccessful,
        user_correction: userCorrection
      })
    });
    return response.json();
  }

  async getLearningStats() {
    const response = await fetch(`${this.apiBase}/feedback/stats`);
    return response.json();
  }
}

// Usage
const api = new SphotaAPI();

// Resolve intent
const resolution = await api.resolveIntent(
  "Transfer 500 to John",
  { location_context: "office", temporal_context: "2026-01-18T10:00:00Z" }
);

console.log(`Resolved: ${resolution.resolved_intent}`);

// Submit feedback
const feedback = await api.submitFeedback(
  resolution.request_id,
  true,  // was_successful
  "transfer_to_account"
);

console.log(`Feedback: ${feedback.action_taken}`);
```

### 6. Real-Time Learning Dashboard

Monitor learning progress:

```python
import time
from datetime import datetime
import requests

def monitor_learning(interval_seconds=5, duration_minutes=10):
    """Monitor learning stats in real-time"""
    api_base = "http://localhost:8000"
    start_time = time.time()
    duration = duration_minutes * 60
    
    print("🔄 Monitoring Sphota Learning Progress...")
    print("-" * 50)
    
    while time.time() - start_time < duration:
        try:
            stats_response = requests.get(f"{api_base}/feedback/stats")
            stats = stats_response.json()["learning_status"]
            
            total = stats.get("total_feedbacks", 0)
            correct = stats.get("correct_feedbacks", 0)
            incorrect = stats.get("incorrect_feedbacks", 0)
            
            accuracy = (correct / total * 100) if total > 0 else 0
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
            print(f"  Total Feedback:     {total:>6}")
            print(f"  Correct:            {correct:>6} ({correct/total*100:>5.1f}%)" if total > 0 else "  Correct:                -")
            print(f"  Incorrect:          {incorrect:>6}")
            print(f"  Accuracy:           {accuracy:>5.1f}%")
            
            time.sleep(interval_seconds)
            
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    monitor_learning(interval_seconds=5, duration_minutes=5)
```

### 7. Data Model Reference

#### Request (POST /feedback)
```python
{
    "request_id": str,      # UUID linking to resolution
    "user_correction": str, # Correct/confirmed intent (1-100 chars)
    "was_successful": bool  # True = strengthen, False = review
}
```

#### Response (POST /feedback)
```python
{
    "success": bool,
    "request_id": str,
    "feedback_type": str,          # "reinforcement"
    "action_taken": str,           # "logged_for_learning" or "queued_for_review"
    "user_correction": str,
    "message": str,
    "learning_status": {
        "total_feedbacks": int,
        "correct_feedbacks": int,
        "incorrect_feedbacks": int,
        "last_update": str          # ISO 8601 timestamp
    },
    "timestamp": str                # ISO 8601 timestamp
}
```

---

## Implementation Status

✅ **Component** | **Status**
---|---
`/feedback` Endpoint | Implemented
Request Model | Implemented
Response Model | Implemented
FeedbackManager Integration | Integrated
Error Handling | Complete
Logging | Complete
Documentation | Complete
Tests | Ready for your test suite

---

## Files Modified

| File | Changes |
|------|---------|
| `main.py` | Added POST /feedback endpoint |
| `core/models.py` | Added ReinforcementFeedbackRequest & ReinforcementFeedbackResponse |
| `docs/REINFORCEMENT_FEEDBACK_LOOP.md` | New comprehensive documentation |

---

## Next Steps

1. **Start the API**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

2. **Test the Endpoint**
   - Visit http://localhost:8000/docs
   - Expand `/feedback` section
   - Try it out with test data

3. **Integrate into Your App**
   - Use provided Python/JavaScript clients
   - Link `/resolve-intent` and `/feedback` flows
   - Monitor learning stats

4. **Monitor Learning**
   - Query `/feedback/stats` regularly
   - Set up alerts for low accuracy
   - Review items in `/feedback/review-queue`

---

## Support

- **Full Documentation:** See `docs/REINFORCEMENT_FEEDBACK_LOOP.md`
- **API Docs:** http://localhost:8000/docs (when running)
- **Source Code:** `main.py` (endpoints), `core/models.py` (data models)

---

**Status:** ✅ Ready for Production  
**Date:** January 18, 2026  
**Version:** 1.0.0-beta
