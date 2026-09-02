"""
Unit and integration tests for FastAPI endpoints in IS-Recommender.
"""
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "IS-Recommender" in data["service"]

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["standards_count"] >= 500
    assert data["vector_index_ready"] is True

def test_recommend_endpoint_success(client):
    payload = {
        "spec_text": "Supply of Fe 500D grade TMT steel bars 12mm and 16mm dia for bridge construction",
        "top_k": 3
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["recommendations"]) == 3
    top_rec = data["recommendations"][0]
    assert top_rec["code"] == "IS 1786"
    assert top_rec["confidence_score"] > 0.60
    assert top_rec["qco_compliance"]["is_mandatory"] is True

def test_recommend_endpoint_out_of_scope(client):
    payload = {
        "spec_text": "Hiring of 5 tempo drivers and 2 supervisors for transport service",
        "top_k": 3
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OUT_OF_SCOPE"
    assert len(data["recommendations"]) == 0

def test_feedback_endpoint(client):
    payload = {
        "spec_text": "Supply of unplasticized PVC pipes Class 3 110mm dia for potable water supply",
        "recommended_standard_id": "IS 4985:2000",
        "action": "ACCEPT",
        "officer_notes": "Approved by GeM Technical Officer"
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["log_id"] > 0

def test_get_standard_detail(client):
    response = client.get("/api/v1/standards/IS 1786:2008")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "IS 1786"
    assert len(data["clauses"]) > 0

def test_get_standards_list(client):
    response = client.get("/api/v1/standards?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 500
    assert len(data["standards"]) == 10
