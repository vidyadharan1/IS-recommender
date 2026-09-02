"""
Pydantic response and request models for GeM-compliant IS-Recommender API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RecommendRequest(BaseModel):
    spec_text: str = Field(..., description="Free-text procurement tender specification from GeM", min_length=5)
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of recommendations to return")

class MatchedClause(BaseModel):
    clause_no: str
    title: str
    text: str
    matched_terms: List[str] = []

class QCOCompliance(BaseModel):
    is_mandatory: bool
    badge: str
    regulatory_note: str

class RecommendationItem(BaseModel):
    rank: int
    standard_id: str
    code: str
    year: Optional[int] = None
    title: str
    sector: str
    ics_code: Optional[str] = None
    confidence_score: float
    confidence_pct: float
    confidence_level: str
    justification: str
    matched_keywords: List[str] = []
    matched_clauses: List[MatchedClause] = []
    qco_compliance: QCOCompliance
    superseded_warning: Optional[str] = None
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    cross_encoder_score: Optional[float] = None
    officer_boost_applied: Optional[float] = 0.0

class RecommendResponse(BaseModel):
    query: str
    status: str
    is_confident: bool
    message: str
    recommendations: List[RecommendationItem] = []
    execution_time_ms: float

class FeedbackRequest(BaseModel):
    spec_text: str = Field(..., description="The procurement specification that was evaluated")
    recommended_standard_id: str = Field(..., description="The standard ID returned by the engine (e.g. 'IS 1786:2008')")
    action: str = Field(..., description="Officer decision: ACCEPT, REJECT, or CORRECT")
    corrected_standard_id: Optional[str] = Field(default=None, description="Correct standard ID if action is CORRECT")
    officer_notes: Optional[str] = Field(default="", description="Optional remarks from the procurement officer")

class FeedbackResponse(BaseModel):
    status: str
    log_id: int
    message: str

class HealthResponse(BaseModel):
    status: str
    version: str
    standards_count: int
    vector_index_ready: bool
    embedding_model: str
    reranker_model: str

class StandardDetailResponse(BaseModel):
    standard_id: str
    code: str
    year: Optional[int] = None
    title: str
    sector: str
    ics_code: Optional[str] = None
    scope: str
    is_mandatory_qco: bool
    superseded_by: Optional[str] = None
    keywords: List[str] = []
    gem_categories: List[str] = []
    clauses: List[Dict[str, Any]] = []

class StandardsListResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    standards: List[StandardDetailResponse]
