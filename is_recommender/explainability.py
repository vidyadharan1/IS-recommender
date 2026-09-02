"""
Explainability layer for IS-Recommender.
Generates clause-level mapping, technical keyword matching, plain-English justifications,
Quality Control Order (QCO) alerts, and explicit out-of-scope non-standard flags.
"""
import re
from typing import List, Dict, Any, Tuple
from is_recommender.config import (
    CONFIDENCE_THRESHOLD_HIGH, CONFIDENCE_THRESHOLD_MEDIUM,
    CONFIDENCE_THRESHOLD_LOW, CONFIDENCE_THRESHOLD_MINIMUM,
    QCO_NOTICE_TEXT
)

# Common words to exclude from keyword matching
EXCLUDE_TERMS = {
    "supply", "procurement", "item", "work", "works", "grade", "conforming",
    "specification", "specifications", "standard", "standards", "indian", "bis",
    "required", "quality", "site", "test", "testing", "material", "materials",
    "details", "minimum", "maximum", "per", "nos", "type", "used", "delivery",
    "and", "for", "with", "the", "from", "into", "that", "this", "these", "those",
    "have", "has", "had", "are", "was", "were", "shall", "will", "about", "above",
    "over", "under", "such", "each", "some", "only", "also", "both", "part"
}

# Indicators of service/human-labor contracts that do not have manufactured BIS product standards
SERVICE_INDICATORS = [
    "security guard", "security personnel", "manpower", "cleaning staff",
    "catering service", "driver hiring", "tempo driver", "taxi rental",
    "gardener", "housekeeping staff", "data entry operator", "electrician service"
]

def check_service_contract(spec_text: str) -> bool:
    """Detects if query is a pure manpower or service tender with no BIS product standard."""
    text_lower = spec_text.lower()
    for term in SERVICE_INDICATORS:
        if term in text_lower:
            return True
    return False

def extract_matched_keywords(spec_text: str, standard: Dict[str, Any]) -> List[str]:
    """Finds intersecting technical keywords between procurement spec and standard."""
    spec_clean = re.findall(r'\b[a-z0-9\.\-]{3,}\b', spec_text.lower())
    spec_tokens = {t for t in spec_clean if t not in EXCLUDE_TERMS and not t.isdigit()}

    # Standard tokens from title, keywords, clauses
    std_terms = set()
    for kw in standard.get("keywords", []):
        for part in kw.lower().split():
            if len(part) > 2 and part not in EXCLUDE_TERMS:
                std_terms.add(part)

    for c in standard.get("clauses", []):
        for part in re.findall(r'\b[a-z0-9\.\-]{3,}\b', (c.get("title", "") + " " + c.get("text", "")).lower()):
            if len(part) > 2 and part not in EXCLUDE_TERMS:
                std_terms.add(part)

    for part in re.findall(r'\b[a-z0-9\.\-]{3,}\b', standard.get("title", "").lower()):
        if len(part) > 2 and part not in EXCLUDE_TERMS:
            std_terms.add(part)

    matched = sorted(list(spec_tokens.intersection(std_terms)))
    return matched[:8]

def find_matching_clauses(spec_text: str, standard: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identifies specific clauses in the standard that address parameters mentioned in the spec."""
    spec_lower = spec_text.lower()
    matched_clauses = []

    for c in standard.get("clauses", []):
        clause_text = (c.get("title", "") + " " + c.get("text", "")).lower()
        clause_words = [w for w in re.findall(r'\b[a-z0-9]{3,}\b', clause_text) if w not in EXCLUDE_TERMS]
        
        matches = [w for w in clause_words if w in spec_lower]
        if matches:
            matched_clauses.append({
                "clause_no": c.get("clause_no", ""),
                "title": c.get("title", ""),
                "text": c.get("text", ""),
                "matched_terms": list(set(matches))[:4]
            })

    return matched_clauses

def generate_justification(
    spec_text: str,
    standard: Dict[str, Any],
    matched_keywords: List[str],
    matched_clauses: List[Dict[str, Any]],
    confidence_level: str
) -> str:
    """
    Synthesizes a plain-English, human-readable justification for the recommendation.
    """
    code = standard.get("code", "")
    title = standard.get("title", "")

    # Clean short title
    short_title = title.split(" - ")[0].strip()

    if matched_clauses:
        best_clause = matched_clauses[0]
        clause_ref = f"{best_clause.get('clause_no', '')} ({best_clause.get('title', '')})"
        if matched_keywords:
            kw_str = ", ".join(matched_keywords[:3])
            return (
                f"Recommended because the specification mandates {kw_str}, which are directly governed under "
                f"{code} under {clause_ref}. The standard specifies compulsory material grades, test methods, "
                f"and acceptance tolerances for {short_title.lower()}."
            )
        else:
            return (
                f"Recommended because the procurement requirements directly fall within the scope of {code} "
                f"({short_title}), specifically addressed in {clause_ref}."
            )
    elif matched_keywords:
        kw_str = ", ".join(matched_keywords[:4])
        return (
            f"Recommended because technical requirements matching '{kw_str}' correspond to the mandatory "
            f"specifications defined in {code} ({short_title})."
        )
    else:
        return (
            f"Applicable based on high semantic alignment with {code} for procurement of {short_title.lower()}."
        )

class ExplainabilityEngine:
    def __init__(self):
        pass

    def explain(self, query: str, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a ranked candidate with explainability metrics:
        - Confidence badge (HIGH, MEDIUM, LOW, UNCERTAIN)
        - Matched keywords
        - Matched clauses
        - Plain-English justification
        - QCO mandate notice
        - Superseded warning
        """
        standard = recommendation["standard"]
        conf_score = recommendation.get("confidence_score", 0.0)

        # 1. Determine confidence tier
        if conf_score >= CONFIDENCE_THRESHOLD_HIGH:
            confidence_level = "HIGH"
        elif conf_score >= CONFIDENCE_THRESHOLD_MEDIUM:
            confidence_level = "MEDIUM"
        elif conf_score >= CONFIDENCE_THRESHOLD_LOW:
            confidence_level = "LOW"
        else:
            confidence_level = "UNCERTAIN"

        # 2. Extract keywords & clauses
        matched_kw = extract_matched_keywords(query, standard)
        matched_cls = find_matching_clauses(query, standard)

        # 3. Generate justification
        justification = generate_justification(query, standard, matched_kw, matched_cls, confidence_level)

        # 4. QCO compliance check
        is_qco = standard.get("is_mandatory_qco", False)
        qco_details = {
            "is_mandatory": is_qco,
            "badge": "QCO MANDATORY" if is_qco else "OPTIONAL / CODE OF PRACTICE",
            "regulatory_note": QCO_NOTICE_TEXT if is_qco else "Voluntary standard or code of practice unless explicitly stipulated in tender NIT."
        }

        # 5. Superseded warning
        superseded_warning = None
        if standard.get("superseded_by"):
            superseded_warning = f"NOTE: This standard is superseded by {standard.get('superseded_by')}. Procurement officers should verify current tender schedule."

        explanation = {
            "confidence_level": confidence_level,
            "matched_keywords": matched_kw,
            "matched_clauses": matched_cls[:3], # Top 3 relevant clauses
            "justification": justification,
            "qco_compliance": qco_details,
            "superseded_warning": superseded_warning
        }
        return explanation

    def verify_query_eligibility(self, spec_text: str, top_candidate: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Checks if the query is a service contract or below valid threshold.
        Returns (is_valid, rejection_reason).
        """
        if check_service_contract(spec_text):
            return False, (
                "OUT OF SCOPE: This specification is for human services, labor hiring, or vehicle rental. "
                "Indian Standards (BIS) prescribe quality and safety specifications for manufactured commodities, "
                "materials, and testing methods rather than service or manpower contracts."
            )

        if top_candidate and top_candidate.get("confidence_score", 0.0) < CONFIDENCE_THRESHOLD_MINIMUM:
            return False, (
                "NO APPLICABLE BIS STANDARD FOUND: The confidence score for all standards is below the "
                f"minimum threshold ({CONFIDENCE_THRESHOLD_MINIMUM * 100:.0f}%). "
                "The procurement specification may be overly vague, proprietary, or not covered under an existing Indian Standard."
            )

        return True, ""
