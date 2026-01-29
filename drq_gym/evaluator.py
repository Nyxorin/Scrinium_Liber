import difflib
from typing import Dict

class Evaluator:
    """
    The Evaluator scores the Defender's performance by comparing the corrected text
    against the Ground Truth.
    """
    def __init__(self):
        pass

    def evaluate(self, corrected: str, ground_truth: str) -> Dict[str, float]:
        """
        Computes similarity metrics between corrected text and ground truth.
        Returns a dictionary with scores (e.g., accuracy, similarity).
        """
        score = difflib.SequenceMatcher(None, corrected, ground_truth).ratio()
        
        # We can add more sophisticated metrics here (Word Error Rate, etc.)
        
        return {
            "similarity_score": score,
            "exact_match": 1.0 if corrected == ground_truth else 0.0
        }

    def generate_report(self, results: list) -> str:
        """
        Aggregates results and returns a summary string.
        """
        total_score = sum(r['similarity_score'] for r in results)
        avg_score = total_score / len(results) if results else 0
        return f"Average Similarity Score: {avg_score:.4f}"
