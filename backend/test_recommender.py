import os
import sys

# Ensure backend directory is on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from backend.recommender import StandardRecommender
except ImportError:
    from recommender import StandardRecommender

rec = StandardRecommender(os.path.join(os.path.dirname(__file__), "data", "standards.json"))
print(f"Total Standards Loaded: {len(rec.standards)}")

queries = [
    "Portland cement for residential construction, 43 grade",
    "Supply of Fe 500D grade TMT deformed steel bars 12mm",
    "Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher",
    "Unplasticized PVC pipes for potable drinking water supply"
]

for q in queries:
    print("\n" + "=" * 70)
    print(f"TEST QUERY: {q}")
    results = rec.recommend(q, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['score']}%] {r['is_code']} | Category: {r['category']}")
        print(f"     Title: {r['title']}")
        print(f"     Matched: {r['matched_keywords']}")
        print(f"     Reason: {r['reason']}")
