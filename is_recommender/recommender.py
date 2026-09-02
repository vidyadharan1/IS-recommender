"""
Unified IS-Recommender pipeline.
Orchestrates Data Loader, Hybrid Retrieval, Cross-Encoder Re-ranking,
Explainability Engine, and Feedback Boosting into a single production interface.
"""
import time
from typing import Dict, Any, List, Optional
from is_recommender.data_loader import DataLoader
from is_recommender.bm25_search import BM25Searcher
from is_recommender.vector_store import VectorStore
from is_recommender.hybrid_retriever import HybridRetriever
from is_recommender.reranker import CrossEncoderReranker
from is_recommender.explainability import ExplainabilityEngine
from is_recommender.feedback import FeedbackManager
from is_recommender.config import FINAL_TOP_K

class ISRecommender:
    def __init__(self):
        print("=" * 60)
        print("Initializing IS-Recommender (SIH26108) Engine...")
        print("=" * 60)
        
        start_time = time.time()
        self.data_loader = DataLoader()
        self.standards = self.data_loader.get_all_standards()

        self.bm25_searcher = BM25Searcher(self.standards)
        self.vector_store = VectorStore(self.standards)
        self.hybrid_retriever = HybridRetriever(self.bm25_searcher, self.vector_store)
        self.reranker = CrossEncoderReranker()
        self.explainer = ExplainabilityEngine()
        self.feedback_mgr = FeedbackManager()

        init_duration = round(time.time() - start_time, 2)
        print(f"[ISRecommender] Initialization complete in {init_duration}s. Ready for queries.")

    def recommend(self, spec_text: str, top_k: int = FINAL_TOP_K) -> Dict[str, Any]:
        """
        Takes a free-text procurement specification and returns ranked BIS recommendations
        with confidence scores, matched clauses, and human-readable justifications.
        """
        start_t = time.time()
        spec_clean = spec_text.strip()

        if not spec_clean:
            return {
                "query": spec_text,
                "status": "EMPTY_QUERY",
                "is_confident": False,
                "message": "Procurement specification cannot be empty.",
                "recommendations": [],
                "execution_time_ms": 0
            }

        # 1. Check if the query is a service/labor contract out of BIS scope
        is_valid, reject_msg = self.explainer.verify_query_eligibility(spec_clean)
        if not is_valid:
            duration = round((time.time() - start_t) * 1000, 1)
            return {
                "query": spec_clean,
                "status": "OUT_OF_SCOPE",
                "is_confident": False,
                "message": reject_msg,
                "recommendations": [],
                "execution_time_ms": duration
            }

        # 2. Hybrid Retrieval (BM25 + FAISS Dense + RRF)
        candidates = self.hybrid_retriever.retrieve(spec_clean, top_k=20)

        if not candidates:
            duration = round((time.time() - start_t) * 1000, 1)
            return {
                "query": spec_clean,
                "status": "NO_MATCH",
                "is_confident": False,
                "message": "No relevant standards retrieved for this query.",
                "recommendations": [],
                "execution_time_ms": duration
            }

        # 3. Cross-Encoder Re-ranking
        reranked = self.reranker.rerank(spec_clean, candidates, top_k=top_k * 2)

        # 4. Apply Feedback Boost Adjustments (if any)
        boosts = self.feedback_mgr.get_boost_adjustments(spec_clean)
        if boosts:
            for item in reranked:
                sid = item["standard"]["standard_id"]
                if sid in boosts:
                    old_conf = item["confidence_score"]
                    boost_val = boosts[sid]
                    new_conf = min(0.99, max(0.01, old_conf + boost_val))
                    item["confidence_score"] = round(new_conf, 4)
                    item["confidence_pct"] = round(new_conf * 100, 1)
                    item["officer_boost_applied"] = round(boost_val, 3)

            # Re-sort after boost adjustments
            reranked.sort(key=lambda x: x["confidence_score"], reverse=True)

        final_candidates = reranked[:top_k]

        # 5. Check confidence threshold of top candidate
        top_cand = final_candidates[0] if final_candidates else None
        is_confident, threshold_msg = self.explainer.verify_query_eligibility(spec_clean, top_cand)

        # 6. Enrich recommendations with explainability metadata
        recommendations = []
        for rank, item in enumerate(final_candidates, start=1):
            exp = self.explainer.explain(spec_clean, item)
            s = item["standard"]

            rec = {
                "rank": rank,
                "standard_id": s.get("standard_id"),
                "code": s.get("code"),
                "year": s.get("year"),
                "title": s.get("title"),
                "sector": s.get("sector"),
                "ics_code": s.get("ics_code"),
                "confidence_score": item.get("confidence_score"),
                "confidence_pct": item.get("confidence_pct"),
                "confidence_level": exp.get("confidence_level"),
                "justification": exp.get("justification"),
                "matched_keywords": exp.get("matched_keywords"),
                "matched_clauses": exp.get("matched_clauses"),
                "qco_compliance": exp.get("qco_compliance"),
                "superseded_warning": exp.get("superseded_warning"),
                "dense_score": item.get("dense_score"),
                "sparse_score": item.get("sparse_score"),
                "cross_encoder_score": item.get("cross_encoder_score"),
                "officer_boost_applied": item.get("officer_boost_applied", 0.0)
            }
            recommendations.append(rec)

        duration = round((time.time() - start_t) * 1000, 1)

        return {
            "query": spec_clean,
            "status": "SUCCESS" if is_confident else "LOW_CONFIDENCE",
            "is_confident": is_confident,
            "message": threshold_msg if not is_confident else "Applicable Indian Standards identified.",
            "recommendations": recommendations,
            "execution_time_ms": duration
        }

    def log_feedback(
        self,
        spec_text: str,
        recommended_standard_id: str,
        action: str,
        corrected_standard_id: Optional[str] = None,
        officer_notes: Optional[str] = ""
    ) -> int:
        """Proxies feedback logging through FeedbackManager."""
        return self.feedback_mgr.log_feedback(
            spec_text=spec_text,
            recommended_standard_id=recommended_standard_id,
            action=action,
            corrected_standard_id=corrected_standard_id,
            officer_notes=officer_notes
        )
