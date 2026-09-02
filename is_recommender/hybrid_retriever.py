"""
Hybrid retrieval core combining Dense Vector Search + Lexical BM25 using Reciprocal Rank Fusion (RRF).
"""
from typing import List, Dict, Any
from is_recommender.config import (
    BM25_TOP_K, VECTOR_TOP_K, RRF_K_CONSTANT,
    RRF_WEIGHT_DENSE, RRF_WEIGHT_SPARSE, RERANK_TOP_K
)
from is_recommender.bm25_search import BM25Searcher
from is_recommender.vector_store import VectorStore

class HybridRetriever:
    def __init__(self, bm25_searcher: BM25Searcher, vector_store: VectorStore):
        self.bm25_searcher = bm25_searcher
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = RERANK_TOP_K,
        k_constant: int = RRF_K_CONSTANT,
        w_dense: float = RRF_WEIGHT_DENSE,
        w_sparse: float = RRF_WEIGHT_SPARSE
    ) -> List[Dict[str, Any]]:
        """
        Executes parallel BM25 and Vector search, fuses candidate lists using RRF.
        Returns unified candidates with individual and fused scores.
        """
        # 1. Lexical BM25 search
        bm25_results = self.bm25_searcher.search(query, top_k=BM25_TOP_K)
        # 2. Dense Vector search
        vector_results = self.vector_store.search(query, top_k=VECTOR_TOP_K)

        candidates: Dict[str, Dict[str, Any]] = {}

        # Process Dense results
        for standard, dense_score, rank in vector_results:
            sid = standard["standard_id"]
            dense_rrf = w_dense / (k_constant + rank)
            candidates[sid] = {
                "standard": standard,
                "dense_rank": rank,
                "dense_score": round(dense_score, 4),
                "sparse_rank": None,
                "sparse_score": 0.0,
                "rrf_score": dense_rrf
            }

        # Process Sparse BM25 results
        for standard, bm25_score, rank in bm25_results:
            sid = standard["standard_id"]
            sparse_rrf = w_sparse / (k_constant + rank)
            if sid in candidates:
                candidates[sid]["sparse_rank"] = rank
                candidates[sid]["sparse_score"] = round(bm25_score, 2)
                candidates[sid]["rrf_score"] += sparse_rrf
            else:
                candidates[sid] = {
                    "standard": standard,
                    "dense_rank": None,
                    "dense_score": 0.0,
                    "sparse_rank": rank,
                    "sparse_score": round(bm25_score, 2),
                    "rrf_score": sparse_rrf
                }

        # Sort candidates by combined RRF score descending
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["rrf_score"], reverse=True)

        return sorted_candidates[:top_k]
