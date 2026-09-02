"""
Unit tests for IS-Recommender retrieval core, hybrid search, explainability, and feedback.
"""
import pytest
from is_recommender.data_loader import DataLoader
from is_recommender.bm25_search import BM25Searcher
from is_recommender.vector_store import VectorStore
from is_recommender.hybrid_retriever import HybridRetriever
from is_recommender.reranker import CrossEncoderReranker
from is_recommender.explainability import ExplainabilityEngine
from is_recommender.recommender import ISRecommender

@pytest.fixture(scope="module")
def recommender():
    return ISRecommender()

def test_data_loader():
    loader = DataLoader()
    standards = loader.get_all_standards()
    assert len(standards) >= 500, f"Expected at least 500 standards, got {len(standards)}"
    
    is_1786 = loader.get_standard_by_id("IS 1786:2008")
    assert is_1786 is not None
    assert is_1786["code"] == "IS 1786"
    assert is_1786["is_mandatory_qco"] is True

def test_bm25_search(recommender):
    query = "TMT steel bars Fe 500D concrete reinforcement tensile proof stress"
    results = recommender.bm25_searcher.search(query, top_k=5)
    assert len(results) > 0
    top_codes = [r[0]["code"] for r in results]
    assert "IS 1786" in top_codes

def test_vector_search(recommender):
    query = "500 kVA outdoor oil immersed copper distribution transformer"
    results = recommender.vector_store.search(query, top_k=5)
    assert len(results) > 0
    top_codes = [r[0]["code"] for r in results]
    assert "IS 1180 Part 1" in top_codes

def test_hybrid_rrf_retrieval(recommender):
    query = "portable ABC dry powder fire extinguisher 6kg pressure gauge"
    candidates = recommender.hybrid_retriever.retrieve(query, top_k=10)
    assert len(candidates) > 0
    top_codes = [c["standard"]["code"] for c in candidates[:3]]
    assert "IS 15683" in top_codes

def test_reranker(recommender):
    query = "disposable 3-ply surgical face mask with meltblown filter layer BFE 98%"
    candidates = recommender.hybrid_retriever.retrieve(query, top_k=15)
    reranked = recommender.reranker.rerank(query, candidates, top_k=3)
    assert len(reranked) > 0
    assert reranked[0]["standard"]["code"] == "IS 16289"
    assert reranked[0]["confidence_score"] > 0.60

def test_explainability_and_justification(recommender):
    query = "Fe 500D grade TMT bars 12mm with tensile strength 565 N/mm2 and elongation 16%"
    result = recommender.recommend(query, top_k=3)
    assert result["status"] == "SUCCESS"
    assert result["is_confident"] is True
    top_rec = result["recommendations"][0]
    assert top_rec["code"] == "IS 1786"
    assert len(top_rec["justification"]) > 20
    assert top_rec["qco_compliance"]["is_mandatory"] is True
    assert "Clause 7" in [c["clause_no"] for c in top_rec["matched_clauses"]]

def test_out_of_scope_service_rejection(recommender):
    query = "Hiring of 5 security personnel for night patrol duty"
    result = recommender.recommend(query)
    assert result["status"] == "OUT_OF_SCOPE"
    assert result["is_confident"] is False
    assert len(result["recommendations"]) == 0
    assert "OUT OF SCOPE" in result["message"]

def test_feedback_logging_and_boost(recommender):
    spec = "Supply of specialized high strength bolts for bridge superstructure"
    log_id = recommender.log_feedback(
        spec_text=spec,
        recommended_standard_id="IS 1367 Part 3:2002",
        action="ACCEPT",
        officer_notes="Verified by GeM procurement manager"
    )
    assert log_id > 0
    summary = recommender.feedback_mgr.get_feedback_summary()
    assert summary["accepted_count"] >= 1
