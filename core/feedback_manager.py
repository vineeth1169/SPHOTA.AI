"""
Real-Time Learning Feedback Manager

Handles user feedback on intent resolutions, enabling continuous learning.

Workflow:
1. User provides feedback on intent resolution
2. If correct → Save to ChromaDB (Fast Memory) as "Golden Record"
3. If incorrect → Log to SQL Review Queue for manual analysis
4. Engine improves accuracy over time
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class FeedbackManager:
    """
    Manages the feedback loop for continuous learning.
    
    Maintains:
    - Review queue (incorrect resolutions)
    - Learning statistics
    - Audit trail
    """
    
    def __init__(
        self,
        fast_memory=None,
        review_queue_path: str = "./learning/review_queue.jsonl",
        stats_path: str = "./learning/feedback_stats.json"
    ):
        """
        Initialize Feedback Manager.
        
        Args:
            fast_memory: Fast Memory instance for saving golden records
            review_queue_path: Path to store incorrect feedback
            stats_path: Path to store learning statistics
        """
        self.fast_memory = fast_memory
        self.review_queue_path = Path(review_queue_path)
        self.stats_path = Path(stats_path)
        
        # Create learning directory
        self.review_queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.stats_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize stats
        self.stats = self._load_stats()
    
    def process_feedback(
        self,
        original_input: str,
        resolved_intent: str,
        was_correct: bool,
        embedding: Optional[Any] = None,
        confidence: Optional[float] = None,
        correct_intent: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user feedback and update learning.
        
        Args:
            original_input: Original user input
            resolved_intent: Intent the engine resolved to
            was_correct: Whether resolution was correct
            embedding: Pre-computed embedding (optional)
            confidence: Engine confidence score
            correct_intent: If incorrect, the correct intent
            notes: Optional user notes
            
        Returns:
            Feedback response with action taken
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if was_correct:
            # Save to Fast Memory as Golden Record
            action = self._save_to_fast_memory(
                original_input=original_input,
                intent_id=resolved_intent,
                embedding=embedding,
                confidence=confidence,
                timestamp=timestamp
            )
            
            self.stats["correct_feedbacks"] += 1
        else:
            # Log to Review Queue
            action = self._queue_for_review(
                original_input=original_input,
                resolved_intent=resolved_intent,
                correct_intent=correct_intent,
                confidence=confidence,
                notes=notes,
                timestamp=timestamp
            )
            
            self.stats["incorrect_feedbacks"] += 1
        
        # Update stats
        self.stats["total_feedbacks"] += 1
        self.stats["last_update"] = timestamp
        self._compute_accuracy()
        self._save_stats()
        
        return {
            "success": True,
            "action_taken": action["action"],
            "memory_id": action.get("memory_id"),
            "review_queue_id": action.get("review_queue_id"),
            "message": action.get("message", "Feedback processed"),
            "learning_status": {
                "total_feedbacks": self.stats["total_feedbacks"],
                "correct_feedbacks": self.stats["correct_feedbacks"],
                "incorrect_feedbacks": self.stats["incorrect_feedbacks"],
                "accuracy": self.stats["accuracy"],
                "last_update": self.stats["last_update"]
            }
        }
    
    def _save_to_fast_memory(
        self,
        original_input: str,
        intent_id: str,
        embedding: Optional[Any] = None,
        confidence: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save confirmed feedback to Fast Memory as a Golden Record.
        
        Args:
            original_input: User input
            intent_id: Resolved intent
            embedding: SBERT embedding
            confidence: Engine confidence
            timestamp: When feedback was given
            
        Returns:
            Action details with memory_id
        """
        # Handle None timestamp with fallback
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.utcnow().isoformat() + 'Z'
        
        memory_id = f"{intent_id}_{int(timestamp.replace(':', '').replace('-', '').replace('T', '').replace('Z', ''))}"
        
        metadata = {
            "feedback_type": "golden_record",
            "user_confirmed": True,
            "confidence": confidence,
            "feedback_timestamp": timestamp
        }
        
        if self.fast_memory:
            try:
                self.fast_memory.add_memory(
                    user_input=original_input,
                    resolved_intent_id=intent_id,
                    embedding=embedding,
                    metadata=metadata
                )
                
                return {
                    "action": "saved_to_memory",
                    "memory_id": memory_id,
                    "message": f"✓ Feedback saved to Fast Memory as Golden Record. Engine will use '{original_input}' to disambiguate similar requests in the future."
                }
            except Exception as e:
                return {
                    "action": "save_failed",
                    "message": f"Failed to save to Fast Memory: {str(e)}"
                }
        
        return {
            "action": "saved_to_memory",
            "memory_id": memory_id,
            "message": "Feedback recorded (Fast Memory not available)"
        }
    
    def _queue_for_review(
        self,
        original_input: str,
        resolved_intent: str,
        correct_intent: Optional[str] = None,
        confidence: Optional[float] = None,
        notes: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log incorrect feedback to Review Queue.
        
        Args:
            original_input: User input
            resolved_intent: What engine resolved to (incorrect)
            correct_intent: What it should have resolved to
            confidence: Engine confidence
            notes: User notes
            timestamp: When feedback was given
            
        Returns:
            Action details with review_queue_id
        """
        review_id = f"review_{len(self._load_review_queue()) + 1:06d}"
        
        review_record = {
            "id": review_id,
            "original_input": original_input,
            "resolved_intent": resolved_intent,
            "correct_intent": correct_intent or "UNKNOWN",
            "confidence": confidence,
            "notes": notes or "",
            "timestamp": timestamp,
            "status": "pending",
            "processed_by": None
        }
        
        # Append to review queue
        with open(self.review_queue_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(review_record) + "\n")
        
        return {
            "action": "queued_for_review",
            "review_queue_id": review_id,
            "message": f"✓ Feedback queued for manual review (ID: {review_id}). An analyst will review this incorrect resolution and help improve the engine."
        }
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load or initialize feedback statistics."""
        if self.stats_path.exists():
            try:
                with open(self.stats_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "total_feedbacks": 0,
            "correct_feedbacks": 0,
            "incorrect_feedbacks": 0,
            "accuracy": 0.0,
            "last_update": None
        }
    
    def _save_stats(self) -> None:
        """Save statistics to disk."""
        with open(self.stats_path, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def _compute_accuracy(self) -> None:
        """Compute current accuracy percentage."""
        if self.stats["total_feedbacks"] > 0:
            accuracy = (self.stats["correct_feedbacks"] / self.stats["total_feedbacks"]) * 100
            self.stats["accuracy"] = round(accuracy, 1)
    
    def _load_review_queue(self) -> List[Dict[str, Any]]:
        """Load all review queue items."""
        items = []
        if self.review_queue_path.exists():
            try:
                with open(self.review_queue_path, "r") as f:
                    for line in f:
                        items.append(json.loads(line))
            except Exception:
                pass
        
        return items
    
    def get_review_queue(self) -> List[Dict[str, Any]]:
        """Get all pending review items."""
        return [item for item in self._load_review_queue() if item.get("status") == "pending"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current learning statistics."""
        return self.stats.copy()
    
    def mark_reviewed(self, review_id: str, corrected_intent: Optional[str] = None) -> bool:
        """
        Mark a review item as processed.
        
        Args:
            review_id: ID of review item
            corrected_intent: The correct intent (if known)
            
        Returns:
            Whether marking was successful
        """
        items = self._load_review_queue()
        updated = False
        
        for item in items:
            if item["id"] == review_id:
                item["status"] = "resolved"
                item["corrected_intent"] = corrected_intent
                updated = True
                break
        
        # Rewrite file
        with open(self.review_queue_path, "w") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")
        
        return updated
