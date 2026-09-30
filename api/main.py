"""
FastAPI application entrypoint for IS-Recommender.
Production-ready REST service designed for GeM (Government e-Marketplace) integration.
"""
import os
import sys
from pathlib import Path
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

from api.routes import router as api_v1_router, get_recommender

# Initialize FastAPI without blocking lifespan so Render can bind to the port immediately
app = FastAPI(
    title="IS-Recommender API (SIH26108)",
    description=(
        "Production-grade AI recommendation engine that takes free-text procurement "
        "specifications from GeM (Government e-Marketplace) listings and recommends "
        "applicable Indian Standards (BIS) with confidence scores and human-readable justifications."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    for orig in default_origins:
        if orig not in allowed_origins:
            allowed_origins.append(orig)
else:
    allowed_origins = ["*"]

is_wildcard = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Health check responds instantly for Render so port check never times out
@app.get("/health", summary="Root Health Check")
def health_check():
    return {"status": "ok"}

# Mount API v1 router (uses lazy loading: model loads on first actual query)
app.include_router(api_v1_router)

# Also expose top-level /recommend endpoint with lazy loader
@app.post("/recommend", summary="Recommend Indian Standards (BIS)")
def recommend_root(payload: dict):
    recommender = get_recommender()
    spec_text = payload.get("spec_text", "")
    top_k = payload.get("top_k", 5)
    return recommender.recommend(spec_text, top_k=top_k)

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
