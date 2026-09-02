"""
FastAPI application entrypoint for IS-Recommender.
Production-ready REST service designed for GeM (Government e-Marketplace) integration.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from is_recommender.recommender import ISRecommender
from api.routes import router as api_v1_router, set_recommender

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preloads the IS-Recommender models and indices on startup."""
    print("[API] Starting IS-Recommender API Server...")
    engine = ISRecommender()
    set_recommender(engine)
    print("[API] IS-Recommender Engine successfully mounted and warm.")
    yield
    print("[API] Shutting down IS-Recommender API Server...")

app = FastAPI(
    title="IS-Recommender API (SIH26108)",
    description=(
        "Production-grade AI recommendation engine that takes free-text procurement "
        "specifications from GeM (Government e-Marketplace) listings and recommends "
        "applicable Indian Standards (BIS) with confidence scores and human-readable justifications."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for seamless communication with React frontend & GeM portal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router)

@app.get("/", summary="Root Status")
async def root():
    return {
        "service": "IS-Recommender API",
        "problem_statement": "SIH26108 (Ministry of Consumer Affairs & GeM)",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "recommend_endpoint": "POST /api/v1/recommend",
        "feedback_endpoint": "POST /api/v1/feedback"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
