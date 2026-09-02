"""
Cross-Encoder re-ranking stage for IS-Recommender.
Uses cross-encoder/ms-marco-MiniLM-L-6-v2 over top candidates with calibrated confidence scoring.
"""
import math
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from is_recommender.config import CROSS_ENCODER_MODEL_NAME, FINAL_TOP_K

def sigmoid(x: float) -> float:
    """Standard numerically stable sigmoid function."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    else:
        z = math.exp(x)
        return z / (1.0 + z)

class CrossEncoderReranker:
    def __init__(self, model_name: str = CROSS_ENCODER_MODEL_NAME):
        self.model_name = model_name
        self.model = CrossEncoder(model_name)
        print(f"[Reranker] Loaded CrossEncoder model: {model_name}")

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = FINAL_TOP_K
    ) -> List[Dict[str, Any]]:
        """
        Takes top-N candidates from hybrid retrieval and scores (query, candidate_text) pairs.
        Calculates calibrated confidence scores and returns top_k ranked results.
        """
        if not candidates:
            return []

        pairs = []
        for item in candidates:
            s = item["standard"]
            # Build representative standard snippet for cross-attention
            clauses_brief = "; ".join([f"{c.get('clause_no', '')} ({c.get('title', '')}): {c.get('text', '')[:160]}" for c in s.get("clauses", [])[:3]])
            doc_text = (
                f"{s.get('code', '')} {s.get('title', '')}. "
                f"Sector: {s.get('sector', '')}. "
                f"Scope: {s.get('scope', '')[:280]}. "
                f"Clauses: {clauses_brief}."
            )
            pairs.append((query, doc_text))

        # Predict cross-encoder logits
        raw_scores = self.model.predict(pairs)

        reranked = []
        for item, raw_score in zip(candidates, raw_scores):
            raw_val = float(raw_score)
            
            # Calibrate raw logit to 0.0 - 1.0 confidence score
            # ms-marco logits: < -7 is irrelevant, -2 to +1 is moderate, > +3 is high
            calibrated_prob = sigmoid((raw_val + 3.2) / 2.0)
            
            # Combine cross-encoder with dense semantic similarity for stable calibration
            dense_sim = item.get("dense_score", 0.0)
            sparse_score = item.get("sparse_score", 0.0)
            
            # If dense similarity is strong, give balanced weighting
            final_confidence = (0.50 * calibrated_prob) + (0.50 * max(0.0, dense_sim))
            if sparse_score > 12.0:
                final_confidence = min(0.99, final_confidence + 0.04)
            final_confidence = min(0.99, max(0.01, final_confidence))

            item_copy = dict(item)
            item_copy["cross_encoder_score"] = round(raw_val, 3)
            item_copy["confidence_score"] = round(final_confidence, 4)
            item_copy["confidence_pct"] = round(final_confidence * 100, 1)

            reranked.append(item_copy)

        # Sort by final confidence score descending
        reranked.sort(key=lambda x: x["confidence_score"], reverse=True)

        return reranked[:top_k]
