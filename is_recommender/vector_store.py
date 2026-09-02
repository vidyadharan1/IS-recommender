"""
Dense vector retrieval using SentenceTransformers and FAISS (IndexFlatIP).
Embeds rich standard definitions and scopes; caches index to disk for fast startup.
"""
import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from is_recommender.config import (
    EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, INDEX_METADATA_PATH, INDEX_DIR
)

def build_document_text(standard: Dict[str, Any]) -> str:
    """Constructs a comprehensive, dense semantic representation of an Indian Standard."""
    clauses_summary = " ".join([f"{c.get('clause_no', '')} {c.get('title', '')}: {c.get('text', '')}" for c in standard.get("clauses", [])])
    keywords_str = ", ".join(standard.get("keywords", []))
    gem_cats = ", ".join(standard.get("gem_categories", []))

    text = (
        f"Standard {standard.get('code', '')} ({standard.get('standard_id', '')}): {standard.get('title', '')}. "
        f"Sector: {standard.get('sector', '')}. "
        f"Scope: {standard.get('scope', '')} "
        f"Key Clauses: {clauses_summary} "
        f"Keywords: {keywords_str}. "
        f"GeM Categories: {gem_cats}."
    )
    return text

class VectorStore:
    def __init__(self, standards: List[Dict[str, Any]], model_name: str = EMBEDDING_MODEL_NAME):
        self.standards = standards
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index: faiss.IndexFlatIP = None
        self.id_to_standard: Dict[int, Dict[str, Any]] = {i: s for i, s in enumerate(standards)}
        self._initialize_index()

    def _initialize_index(self):
        """Loads index from disk or encodes standards and creates FAISS FlatIP index."""
        os.makedirs(INDEX_DIR, exist_ok=True)
        
        index_file = str(FAISS_INDEX_PATH)
        meta_file = str(INDEX_METADATA_PATH)

        if os.path.exists(index_file) and os.path.exists(meta_file):
            try:
                print(f"[VectorStore] Loading cached FAISS index from {index_file}...")
                self.index = faiss.read_index(index_file)
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if meta.get("count") == len(self.standards) and meta.get("model") == self.model_name:
                    print(f"[VectorStore] Successfully loaded FAISS index with {self.index.ntotal} vectors.")
                    return
                else:
                    print("[VectorStore] Index metadata mismatch or standard count changed. Rebuilding index...")
            except Exception as e:
                print(f"[VectorStore] Failed to load cached index: {e}. Rebuilding...")

        print(f"[VectorStore] Building FAISS vector index for {len(self.standards)} standards...")
        corpus_texts = [build_document_text(s) for s in self.standards]
        
        # Compute embeddings in batches
        embeddings = self.model.encode(corpus_texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.ascontiguousarray(embeddings.astype("float32"))

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension) # Inner Product on normalized vectors == Cosine Similarity
        self.index.add(embeddings)

        # Save to disk
        try:
            faiss.write_index(self.index, index_file)
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump({"count": len(self.standards), "dimension": dimension, "model": self.model_name}, f)
            print(f"[VectorStore] Saved FAISS index to {index_file} ({self.index.ntotal} vectors).")
        except Exception as e:
            print(f"[VectorStore] Warning: Could not cache index to disk: {e}")

    def search(self, query: str, top_k: int = 25) -> List[Tuple[Dict[str, Any], float, int]]:
        """
        Embeds query, executes cosine similarity search, and returns:
        (standard_dict, cosine_similarity_score, rank_1_indexed)
        """
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        query_embedding = np.ascontiguousarray(query_embedding.astype("float32"))

        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx != -1 and idx in self.id_to_standard:
                standard = self.id_to_standard[idx]
                results.append((standard, float(score), rank))

        return results
