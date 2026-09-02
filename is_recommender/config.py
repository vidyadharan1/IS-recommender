"""
Configuration settings for IS-Recommender.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "data" / "indices"

# Data file paths
CATALOG_JSON_PATH = DATA_DIR / "bis_standards_catalog.json"
EVALUATION_JSON_PATH = DATA_DIR / "evaluation_dataset.json"
SQLITE_DB_PATH = DATA_DIR / "is_recommender.db"
FAISS_INDEX_PATH = INDEX_DIR / "standards_faiss.index"
INDEX_METADATA_PATH = INDEX_DIR / "index_metadata.json"

# Model settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Retrieval parameters
BM25_TOP_K = 25
VECTOR_TOP_K = 25
RRF_K_CONSTANT = 60
RRF_WEIGHT_DENSE = 0.55
RRF_WEIGHT_SPARSE = 0.45
RERANK_TOP_K = 20
FINAL_TOP_K = 5

# Confidence thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.70
CONFIDENCE_THRESHOLD_MEDIUM = 0.48
CONFIDENCE_THRESHOLD_LOW = 0.32
# If the top score is below this threshold, classify as UNCERTAIN / NO STANDARD APPLIES
CONFIDENCE_THRESHOLD_MINIMUM = 0.28

# Quality Control Order (QCO) regulatory notice
QCO_NOTICE_TEXT = "MANDATORY FOR GeM: Covered under Ministry Quality Control Order (QCO) - ISI Certification Mark is legally required for public procurement."
