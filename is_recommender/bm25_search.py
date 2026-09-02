"""
BM25 Lexical Keyword Search for IS-Recommender.
Uses Rank-BM25 with domain-specific tokenization, code normalization, and clause indexing.
"""
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their",
    "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
    "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "shall", "will", "specification", "requirements", "standard", "code"
}

def tokenize_text(text: str) -> List[str]:
    """
    Cleans, lowercases, tokenizes, and handles standard code formats like IS 1786 -> ['is', '1786', 'is1786'].
    """
    if not text:
        return []
    
    text = text.lower()
    
    # Extract standard patterns like IS 1786 or IS-1786 and create joined tokens
    is_matches = re.findall(r'\bis[\s\-_]?(\d+)\b', text)
    extra_tokens = []
    for m in is_matches:
        extra_tokens.append(f"is{m}")
        extra_tokens.append(m)

    # Word tokenization
    raw_tokens = re.findall(r'[a-z0-9]+(?:[\./\-][a-z0-9]+)*', text)
    tokens = []
    for t in raw_tokens:
        # Strip trailing punctuation
        t_clean = t.strip(".-/")
        if len(t_clean) > 1 and t_clean not in STOPWORDS:
            tokens.append(t_clean)

    tokens.extend(extra_tokens)
    return tokens

class BM25Searcher:
    def __init__(self, standards: List[Dict[str, Any]]):
        self.standards = standards
        self.corpus_tokens: List[List[str]] = []
        self.bm25: BM25Okapi = None
        self._build_index()

    def _build_index(self):
        """Prepares tokenized documents for all standards."""
        for s in self.standards:
            doc_parts = [
                s.get("code", ""),
                s.get("code", "").replace(" ", ""),
                s.get("title", ""),
                s.get("sector", ""),
                s.get("scope", ""),
                " ".join(s.get("keywords", [])),
                " ".join(s.get("gem_categories", []))
            ]
            for clause in s.get("clauses", []):
                doc_parts.append(clause.get("clause_no", ""))
                doc_parts.append(clause.get("title", ""))
                doc_parts.append(clause.get("text", ""))

            full_text = " ".join(doc_parts)
            tokens = tokenize_text(full_text)
            self.corpus_tokens.append(tokens)

        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"[BM25Searcher] Indexed {len(self.standards)} standards with BM25.")

    def search(self, query: str, top_k: int = 25) -> List[Tuple[Dict[str, Any], float, int]]:
        """
        Searches using BM25 and returns ranked list of:
        (standard_dict, bm25_score, rank_1_indexed)
        """
        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []

        doc_scores = self.bm25.get_scores(query_tokens)
        
        # Sort indices by score descending
        ranked_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]

        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            score = float(doc_scores[idx])
            results.append((self.standards[idx], score, rank))

        return results
