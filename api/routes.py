"""
FastAPI route definitions for IS-Recommender API (v1).
Designed for seamless consumption by GeM (Government e-Marketplace).
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from api.schemas import (
    RecommendRequest, RecommendResponse, FeedbackRequest, FeedbackResponse,
    HealthResponse, StandardDetailResponse, StandardsListResponse
)
from is_recommender.recommender import ISRecommender
from is_recommender.config import EMBEDDING_MODEL_NAME, CROSS_ENCODER_MODEL_NAME

router = APIRouter(prefix="/api/v1")

# Global singleton recommender instance (injected via main.py)
_recommender_instance: Optional[ISRecommender] = None

def get_recommender() -> ISRecommender:
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ISRecommender()
    return _recommender_instance

def set_recommender(rec: ISRecommender):
    global _recommender_instance
    _recommender_instance = rec

@router.post("/recommend", response_model=RecommendResponse, summary="Recommend Indian Standards (BIS)")
async def recommend_standards(
    payload: RecommendRequest,
    recommender: ISRecommender = Depends(get_recommender)
):
    """
    Takes a free-text procurement tender specification and returns ranked
    Indian Standards (BIS) with confidence scores, matched clauses, and plain-English justification.
    """
    try:
        result = recommender.recommend(payload.spec_text, top_k=payload.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")

@router.post("/feedback", response_model=FeedbackResponse, summary="Log Officer Feedback")
async def log_officer_feedback(
    payload: FeedbackRequest,
    recommender: ISRecommender = Depends(get_recommender)
):
    """
    Logs procurement officer decisions (ACCEPT, REJECT, or CORRECT) to calibrate the engine
    and dynamically boost matching standards in future tenders.
    """
    try:
        log_id = recommender.log_feedback(
            spec_text=payload.spec_text,
            recommended_standard_id=payload.recommended_standard_id,
            action=payload.action,
            corrected_standard_id=payload.corrected_standard_id,
            officer_notes=payload.officer_notes
        )
        return {
            "status": "SUCCESS",
            "log_id": log_id,
            "message": f"Officer decision '{payload.action.upper()}' recorded successfully."
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback recording error: {str(e)}")

@router.get("/standards", response_model=StandardsListResponse, summary="List / Search Indian Standards")
async def list_standards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sector: Optional[str] = Query(None, description="Filter by sector name"),
    search: Optional[str] = Query(None, description="Keyword search in code or title"),
    recommender: ISRecommender = Depends(get_recommender)
):
    """
    Returns a paginated list of Indian Standards in the catalog with optional search and sector filters.
    """
    all_standards = recommender.standards

    filtered = all_standards
    if sector:
        filtered = [s for s in filtered if sector.lower() in s.get("sector", "").lower()]

    if search:
        s_clean = search.lower()
        filtered = [
            s for s in filtered
            if s_clean in s.get("code", "").lower() or s_clean in s.get("title", "").lower()
        ]

    total_count = len(filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged = filtered[start_idx:end_idx]

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "standards": paged
    }

@router.get("/standards/{standard_id}", response_model=StandardDetailResponse, summary="Get Standard Details")
async def get_standard_details(
    standard_id: str,
    recommender: ISRecommender = Depends(get_recommender)
):
    """
    Retrieves full technical details, scope, and clauses for a specific Indian Standard ID.
    """
    standard = recommender.data_loader.get_standard_by_id(standard_id)
    if not standard:
        raise HTTPException(status_code=404, detail=f"Standard '{standard_id}' not found in BIS catalog.")
    return standard

@router.get("/admin/coverage-gaps", summary="Admin View of Standards Coverage Gaps")
async def get_coverage_gaps(recommender: ISRecommender = Depends(get_recommender)):
    """
    Admin endpoint providing statistics on officer actions and audit log of rejected/corrected recommendations.
    """
    return recommender.feedback_mgr.get_feedback_summary()

@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check(recommender: ISRecommender = Depends(get_recommender)):
    """
    Returns operational health status, index readiness, and model metadata.
    """
    return {
        "status": "HEALTHY",
        "version": "1.0.0",
        "standards_count": len(recommender.standards),
        "vector_index_ready": recommender.vector_store.index is not None,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "reranker_model": CROSS_ENCODER_MODEL_NAME
    }
