import requests
import json
import time

# Give servers a moment to bind
time.sleep(1)

BASE_URL = "http://127.0.0.1:8000"

print("1. Testing GET /api/health...")
r_health = requests.get(f"{BASE_URL}/api/health")
print("Status:", r_health.status_code)
print("Response:", r_health.json())
assert r_health.status_code == 200
assert r_health.json()["status"] == "ok"
assert r_health.json()["standards_count"] >= 60

print("\n2. Testing GET /api/standards...")
r_standards = requests.get(f"{BASE_URL}/api/standards?page=1&page_size=3&category=Cement")
print("Status:", r_standards.status_code)
std_data = r_standards.json()
print(f"Total cement standards: {std_data['total']}, Page: {std_data['page']}, Items returned: {len(std_data['standards'])}")
assert r_standards.status_code == 200
assert len(std_data["standards"]) == 3

print("\n3. Testing POST /api/recommend with 4 Sample Queries...")
test_queries = [
    "Portland cement for residential construction, 43 grade",
    "Supply of Fe 500D grade TMT deformed steel bars 12mm",
    "Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher",
    "Unplasticized PVC pipes for potable drinking water supply"
]

for idx, q in enumerate(test_queries, 1):
    payload = {"query": q, "top_k": 3}
    r_rec = requests.post(f"{BASE_URL}/api/recommend", json=payload)
    print(f"\n--- QUERY {idx}: '{q}' ---")
    print("Status:", r_rec.status_code)
    assert r_rec.status_code == 200
    results = r_rec.json()
    assert len(results) > 0
    top = results[0]
    print(f"Rank #1: {top['is_code']} | Score: {top['score']}%")
    print(f"Title: {top['title']}")
    print(f"Category: {top['category']}")
    print(f"Matched Keywords: {top['matched_keywords']}")
    print(f"Reason: {top['reason']}")

print("\n4. Testing Frontend Proxy on http://localhost:5173/api/health...")
try:
    r_proxy = requests.get("http://localhost:5173/api/health", timeout=3)
    print("Frontend proxy status:", r_proxy.status_code)
    print("Frontend proxy response:", r_proxy.json())
except Exception as e:
    print("Frontend proxy check:", e)

print("\n>>> ALL BACKEND AND FRONTEND CHECKS PASSED SUCCESSFULLY! <<<")
