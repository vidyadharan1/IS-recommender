import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load local environment if available
load_dotenv()

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender import StandardRecommender

app = FastAPI(
    title="StandardsFinder API",
    description="AI-Powered Indian Standards (BIS / IS) Recommendation Engine for Procurement Specifications (SIH26108)",
    version="1.0.0"
)

# CORS Configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    origins = ["*"]
else:
    origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender instance
recommender = StandardRecommender()


# Pydantic Schemas
class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1500, description="Procurement specification text")
    top_k: int = Field(5, ge=1, le=50, description="Number of top standards to return")


class RecommendationItem(BaseModel):
    is_code: str
    title: str
    category: str
    score: float
    matched_keywords: List[str]
    reason: str


class StandardItem(BaseModel):
    is_code: str
    title: str
    category: str
    scope: str
    keywords: List[str]


class StandardsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    standards: List[StandardItem]


class HealthResponse(BaseModel):
    status: str
    standards_count: int
    version: str


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint to verify backend status and standards index count."""
    return HealthResponse(
        status="ok",
        standards_count=len(recommender.standards),
        version="1.0.0"
    )


@app.post("/api/recommend", response_model=List[RecommendationItem], tags=["Recommendation"])
def get_recommendations(req: RecommendRequest):
    """
    Accepts procurement specifications and returns top ranked Indian Standards (BIS / IS codes)
    using TF-IDF cosine similarity, synonym expansion, and keyword boosting.
    """
    clean_query = req.query.strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty or solely whitespace.")

    try:
        results = recommender.recommend(clean_query, top_k=req.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error processing recommendation: {str(e)}")


@app.get("/api/standards", response_model=StandardsResponse, tags=["Standards"])
def list_standards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Cement, Steel, Electrical)"),
    search: Optional[str] = Query(None, description="Free text search filter across codes and descriptions")
):
    """List or search through the Indian Standards catalog with pagination and filtering."""
    try:
        data = recommender.get_standards(
            page=page,
            page_size=page_size,
            category=category,
            search=search
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error retrieving standards: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
