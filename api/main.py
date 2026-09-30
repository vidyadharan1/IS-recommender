"""
FastAPI application entrypoint for IS-Recommender.
Production-ready REST service designed for GeM (Government e-Marketplace) integration.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Limit thread pools to minimize RAM footprint on cloud containers (e.g. Render 512MB free tier)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

try:
    import torch
    torch.set_num_threads(1)
except ImportError:
    pass

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

# Dynamic CORS Configuration from ALLOWED_ORIGINS env variable
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins.strip():
    allowed_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]
    # Keep local development origins intact
    for orig in default_origins:
        if orig not in allowed_origins:
            allowed_origins.append(orig)
else:
    # Allow all origins if not explicitly restricted (development mode)
    allowed_origins = ["*"]

is_wildcard = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Health Check endpoint (standard requirement for Render, Cloud Run, and load balancers)
@app.get("/health", summary="Root Health Check")
async def health_check_root():
    return {
        "status": "HEALTHY",
        "service": "IS-Recommender API",
        "version": "1.0.0"
    }

# Mount API v1 router
app.include_router(api_v1_router)

@app.get("/", summary="Root Status")
async def root():
    return {
        "service": "IS-Recommender API",
        "problem_statement": "SIH26108 (Ministry of Consumer Affairs & GeM)",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "api_v1_health": "/api/v1/health",
        "recommend_endpoint": "POST /api/v1/recommend",
        "feedback_endpoint": "POST /api/v1/feedback"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[API] Binding to {host}:{port}")
    uvicorn.run("api.main:app", host=host, port=port, reload=False)
