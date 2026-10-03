import json
import os
import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "will", "with", "you", "your", "yours", "yourself", "yourselves",
    # Procurement generic noise words:
    "procurement", "supply", "purchase", "purchasing", "tender", "bidding", "contract", "required", 
    "requirement", "requirements", "specification", "specifications", "spec", "specs", "standard", 
    "standards", "conforming", "confirming", "shall", "item", "items", "material", "materials", 
    "purpose", "purposes", "per", "details", "work", "works"
}

SYNONYMS = {
    "cement": ["opc", "portland", "pozzolana", "ppc", "psc", "slag", "concrete", "mortar", "compressive"],
    "portland": ["cement", "opc", "ordinary", "clinker"],
    "opc": ["ordinary", "portland", "cement", "43", "53", "33"],
    "ppc": ["portland", "pozzolana", "flyash", "fly", "ash", "cement"],
    "tmt": ["steel", "rebar", "fe500d", "fe500", "fe415", "fe550", "deformed", "reinforcement", "rebars"],
    "rebar": ["tmt", "steel", "fe500d", "reinforcement", "bars"],
    "rebars": ["tmt", "steel", "fe500d", "reinforcement", "bars"],
    "steel": ["tmt", "rebar", "structural", "e250", "e350", "angles", "beams", "plates", "reinforcement"],
    "structural": ["e250", "e350", "is2062", "beams", "angles", "channels", "hot", "rolled"],
    "cable": ["cables", "wire", "wires", "conductor", "copper", "aluminum", "pvc", "xlpe", "frls", "insulation"],
    "wire": ["cable", "cables", "conductor", "copper", "aluminum", "frls", "wiring"],
    "transformer": ["transformers", "distribution", "11kv", "433v", "kva", "oil", "substation", "bee"],
    "mcb": ["circuit", "breaker", "breakers", "miniature", "overcurrent", "switchgear"],
    "switch": ["modular", "switches", "socket", "sockets", "piano"],
    "lamp": ["led", "bulb", "bulbs", "lighting", "luminaire"],
    "light": ["led", "lamp", "luminaire", "lighting"],
    "led": ["lamp", "bulb", "lighting", "luminaire"],
    "earthing": ["grounding", "electrode", "pit", "chemical"],
    "pipe": ["pipes", "upvc", "cpvc", "hdpe", "ductile", "iron", "potable", "water", "plumbing", "drainage"],
    "pipes": ["pipe", "upvc", "cpvc", "hdpe", "ductile", "iron", "potable", "water", "plumbing"],
    "upvc": ["unplasticized", "pvc", "potable", "water", "plumbing", "pipes"],
    "cpvc": ["chlorinated", "hot", "cold", "plumbing", "potable", "water"],
    "hdpe": ["polyethylene", "sewerage", "drainage", "pipes", "pe100"],
    "water": ["potable", "drinking", "mineral", "bottled", "purified", "packaged", "aquifer"],
    "drinking": ["potable", "water", "packaged", "bottled", "tds"],
    "flour": ["wheat", "atta", "chakki", "maida", "grain", "rations"],
    "atta": ["wheat", "flour", "chakki", "grain", "rations"],
    "sugar": ["cane", "refined", "sweetener", "sucrose"],
    "salt": ["iodized", "edible", "sodium", "chloride"],
    "oil": ["edible", "vegetable", "cooking", "mustard", "sunflower"],
    "mask": ["masks", "surgical", "3ply", "meltblown", "bfe", "respirator", "n95", "ffp2", "medical"],
    "masks": ["mask", "surgical", "3ply", "meltblown", "bfe", "respirator", "n95", "ffp2"],
    "ppe": ["coveralls", "protective", "mask", "gloves", "face", "shield"],
    "jacket": ["vest", "reflective", "high", "visibility", "warning"],
    "vest": ["reflective", "high", "visibility", "jacket", "fluorescent"],
    "paint": ["paints", "enamel", "emulsion", "primer", "coating", "synthetic", "acrylic"],
    "paints": ["paint", "enamel", "emulsion", "primer", "coating"],
    "primer": ["red", "oxide", "zinc", "chrome", "anti", "corrosive", "metal", "paint"],
    "enamel": ["synthetic", "alkyd", "gloss", "paint"],
    "box": ["boxes", "corrugated", "carton", "cartons", "packaging", "kraft"],
    "boxes": ["box", "corrugated", "carton", "cartons", "packaging", "kraft"],
    "carton": ["box", "corrugated", "packaging", "kraft"],
    "sack": ["sacks", "bag", "bags", "hdpe", "pp", "woven", "packaging"],
    "bag": ["bags", "sack", "sacks", "woven", "packaging"],
    "extinguisher": ["fire", "extinguishers", "abc", "powder", "safety", "co2"],
    "helmet": ["helmets", "hard", "hat", "head", "protection", "industrial", "safety"],
    "shoe": ["shoes", "boots", "footwear", "safety", "steel", "toe"],
    "shoes": ["shoe", "boots", "footwear", "safety", "steel", "toe"],
    "boot": ["boots", "safety", "shoes", "footwear"],
    "harness": ["fall", "arrest", "safety", "belt", "lanyard"],
    "server": ["servers", "rack", "datacenter", "computer", "it", "hardware"],
    "laptop": ["notebook", "computer", "pc", "desktop", "workstation"],
    "computer": ["desktop", "laptop", "server", "workstation", "pc", "it"],
    "pump": ["pumps", "centrifugal", "submersible", "monobloc", "water"],
    "pumps": ["pump", "centrifugal", "submersible", "monobloc", "water"],
    "valve": ["valves", "sluice", "butterfly", "gate", "globe", "check"],
    "valves": ["valve", "sluice", "butterfly", "gate", "globe", "check"],
    "earthquake": ["seismic", "zone", "base", "shear", "ductile", "vibration"],
    "seismic": ["earthquake", "ductile", "structural", "response", "spectrum"],
    "soil": ["geotechnical", "bearing", "capacity", "foundation", "cbr", "compaction"],
    "concrete": ["cement", "rcc", "mix", "cube", "slump", "admixture", "reinforced"],
    "ups": ["uninterruptible", "power", "backup", "inverter", "battery", "online"],
    "solar": ["photovoltaic", "pv", "module", "panel", "inverter", "renewable"],
    "cybersecurity": ["security", "isms", "iso27001", "encryption", "privacy", "protection"]
}


class StandardRecommender:
    def __init__(self, data_path: str | None = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), "data", "standards.json")
        self.data_path = data_path
        self.standards: list[dict[str, Any]] = []
        self.corpus: list[str] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        """Loads standards from JSON and builds the TF-IDF index."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Standards data file not found at: {self.data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.standards = json.load(f)
            
        self.corpus = []
        for s in self.standards:
            # We give high weight to IS code, title, and keywords in the document
            code_text = s.get("is_code", "")
            title_text = s.get("title", "")
            cat_text = s.get("category", "")
            scope_text = s.get("scope", "")
            keywords_text = " ".join(s.get("keywords", []))
            
            # Weighted document representation
            doc = f"{code_text} {code_text} {title_text} {title_text} {cat_text} {keywords_text} {keywords_text} {scope_text}"
            self.corpus.append(self.preprocess_text(doc))

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Extract clean alphanumeric tokens."""
        text = text.lower()
        # Normalize specific patterns like "fe 500d" -> "fe500d"
        text = re.sub(r'fe[\s\-_]?(\d{3}[a-z]?)', r'fe\1', text)
        text = re.sub(r'is[\s\-_]?(\d+)', r'is \1', text)
        tokens = re.findall(r'[a-z0-9]+', text)
        return tokens

    def preprocess_text(self, text: str, expand_synonyms: bool = False) -> str:
        """Tokenize, remove stopwords, and optionally expand domain synonyms."""
        tokens = self.tokenize(text)
        filtered_tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
        
        if expand_synonyms:
            expanded = list(filtered_tokens)
            for token in filtered_tokens:
                if token in SYNONYMS:
                    expanded.extend(SYNONYMS[token])
            return " ".join(expanded)
            
        return " ".join(filtered_tokens)

    def extract_matched_keywords(self, query_tokens: set, standard: dict[str, Any]) -> list[str]:
        """Finds overlap between query terms/synonyms and standard keywords/title, filtering out stopwords."""
        matched = []
        std_keywords = standard.get("keywords", [])
        title_lower = standard.get("title", "").lower()
        scope_lower = standard.get("scope", "").lower()
        
        # Filter query tokens so no stopwords or 1-letter tokens are considered
        clean_query_tokens = {t for t in query_tokens if t.lower() not in STOPWORDS and len(t) > 1}

        # Check standard keywords
        for kw in std_keywords:
            kw_lower = kw.strip().lower()
            if kw_lower in STOPWORDS:
                continue
            kw_tokens = [t for t in self.tokenize(kw) if t not in STOPWORDS and len(t) > 1]
            if not kw_tokens:
                continue
            # If all meaningful tokens of the keyword are in clean_query_tokens
            if set(kw_tokens).issubset(clean_query_tokens) or any(t in clean_query_tokens for t in kw_tokens if len(t) > 3):
                matched.append(kw)
                
        # Also check prominent domain tokens from query
        for qt in clean_query_tokens:
            if (
                len(qt) >= 3
                and qt not in STOPWORDS
                and (qt in title_lower or qt in scope_lower)
                and not any(qt in m.lower() for m in matched)
            ):
                matched.append(qt)

        # De-duplicate while preserving order, and strictly filter out any stopwords
        unique_matches = []
        for m in matched:
            m_lower = m.strip().lower()
            if m_lower not in STOPWORDS and m not in unique_matches:
                # Ensure multi-word phrases have at least one non-stopword token
                m_tokens = [t for t in self.tokenize(m) if t not in STOPWORDS]
                if m_tokens:
                    unique_matches.append(m)
        return unique_matches[:6]

    def generate_reason(self, query: str, standard: dict[str, Any], score: float, matched_kws: list[str]) -> str:
        """Generates a contextual, human-friendly explanation for the recommendation."""
        cat = standard.get("category", "General")
        is_code = standard.get("is_code", "")
        title = standard.get("title", "")
        
        # Check if direct code match
        code_nums = re.findall(r'\d+', is_code)
        query_nums = re.findall(r'\d+', query)
        direct_code_hit = any(num in query_nums for num in code_nums if len(num) >= 3)
        
        if direct_code_hit:
            return f"Exact Indian Standard code match for '{is_code}'. Provides mandatory BIS specifications, grades, and compliance benchmarks for {title.lower()}."
            
        if matched_kws:
            terms_str = ", ".join([f"'{k}'" for k in matched_kws[:3]])
            if score >= 80:
                return f"High confidence match in {cat} category on {terms_str}. Formulated specifically for requirements defined in {is_code} ({title})."
            elif score >= 60:
                return f"Applicable {cat} standard matching key parameters ({terms_str}). Covers testing methods and quality thresholds under {is_code}."
            else:
                return f"Relevant reference standard for {cat} matching {terms_str}. Provides foundational testing and safety tolerances."
        
        return f"Ranked in the {cat} sector for general compatibility with the procurement specification under {is_code}."

    def recommend(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Recommends top-k Indian Standards for a free-text procurement specification."""
        if not query or not query.strip():
            return []

        clean_query = query.strip()
        expanded_query_str = self.preprocess_text(clean_query, expand_synonyms=True)
        raw_query_tokens = set(self.tokenize(clean_query))
        clean_query_tokens = {t for t in raw_query_tokens if t not in STOPWORDS and len(t) > 1}
        
        # Include synonym expansions in query token set for keyword matching (excluding stopwords)
        expanded_tokens = set(clean_query_tokens)
        for token in clean_query_tokens:
            if token in SYNONYMS:
                for syn in SYNONYMS[token]:
                    if syn not in STOPWORDS and len(syn) > 1:
                        expanded_tokens.add(syn)

        # 1. TF-IDF Cosine Similarity
        query_vec = self.vectorizer.transform([expanded_query_str])
        tfidf_sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        results = []
        for idx, standard in enumerate(self.standards):
            base_sim = float(tfidf_sims[idx])
            
            # 2. Keyword & Specific Code Boosting
            boost = 0.0
            is_code = standard.get("is_code", "").lower()
            title = standard.get("title", "").lower()
            category = standard.get("category", "").lower()

            # Direct IS code number match (e.g. user typed "1786" or "IS 1786")
            code_digits = re.findall(r'\d+', is_code)
            for cd in code_digits:
                if len(cd) >= 3 and cd in raw_query_tokens:
                    boost += 0.40  # Massive boost for explicit standard reference
                    break

            # Exact phrase match in title
            title_tokens = set(self.tokenize(title))
            matched_title_tokens = raw_query_tokens.intersection(title_tokens)
            if matched_title_tokens:
                boost += min(0.20, len(matched_title_tokens) * 0.06)

            # Category match bonus
            if category in raw_query_tokens or any(cat_term in raw_query_tokens for cat_term in self.tokenize(category)):
                boost += 0.08

            # Keyword overlap bonus
            matched_kws = self.extract_matched_keywords(expanded_tokens, standard)
            if matched_kws:
                boost += min(0.25, len(matched_kws) * 0.05)

            # Raw score calculation
            raw_score = (base_sim * 0.65) + boost
            
            # Normalize to 0 - 100 scale with smooth non-linear curve
            if raw_score <= 0.01:
                final_score = 0.0
            else:
                # Sigmoidal-like scaling to make good matches reach 85-98 range
                scaled = min(1.0, raw_score * 1.4)
                final_score = round(scaled * 100, 1)

            if final_score > 5.0 or boost > 0.05:
                reason = self.generate_reason(clean_query, standard, final_score, matched_kws)
                results.append({
                    "is_code": standard.get("is_code"),
                    "title": standard.get("title"),
                    "category": standard.get("category"),
                    "score": final_score,
                    "matched_keywords": matched_kws,
                    "reason": reason,
                    "_scope": standard.get("scope", "")  # kept for UI preview if needed
                })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        top_results = results[:top_k]

        # Clean internal fields for API output
        output = []
        for r in top_results:
            item = dict(r)
            item.pop("_scope", None)
            output.append(item)
            
        return output

    def get_standards(
        self,
        page: int = 1,
        page_size: int = 10,
        category: str | None = None,
        search: str | None = None
    ) -> dict[str, Any]:
        """Returns paginated and filtered list of standards."""
        filtered = self.standards
        
        if category and category.strip() and category.lower() != "all":
            cat_lower = category.strip().lower()
            filtered = [s for s in filtered if s.get("category", "").lower() == cat_lower]
            
        if search and search.strip():
            s_lower = search.strip().lower()
            filtered = [
                s for s in filtered
                if s_lower in s.get("is_code", "").lower()
                or s_lower in s.get("title", "").lower()
                or s_lower in s.get("category", "").lower()
                or s_lower in s.get("scope", "").lower()
                or any(s_lower in kw.lower() for kw in s.get("keywords", []))
            ]

        total = len(filtered)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_standards = filtered[start_idx:end_idx]
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "standards": paginated_standards
        }
