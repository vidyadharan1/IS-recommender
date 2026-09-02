"""
Feedback management and dynamic match boosting for procurement officer decisions.
Logs accept/reject/correct actions in SQLite and adjusts candidate rankings for similar specs.
"""
import sqlite3
from typing import Dict, Any, List, Optional
from is_recommender.config import SQLITE_DB_PATH
from is_recommender.bm25_search import tokenize_text

def jaccard_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Computes Jaccard word similarity between two token lists."""
    s1, s2 = set(tokens1), set(tokens2)
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

class FeedbackManager:
    def __init__(self, db_path=SQLITE_DB_PATH):
        self.db_path = db_path

    def log_feedback(
        self,
        spec_text: str,
        recommended_standard_id: str,
        action: str, # "ACCEPT", "REJECT", "CORRECT"
        corrected_standard_id: Optional[str] = None,
        officer_notes: Optional[str] = ""
    ) -> int:
        """Logs officer feedback to SQLite and updates boost weights."""
        action_clean = action.strip().upper()
        if action_clean not in {"ACCEPT", "REJECT", "CORRECT"}:
            raise ValueError(f"Invalid action: {action}. Must be ACCEPT, REJECT, or CORRECT.")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO feedback_logs (
                spec_text, recommended_standard_id, action, corrected_standard_id, officer_notes
            ) VALUES (?, ?, ?, ?, ?)
        """, (spec_text.strip(), recommended_standard_id, action_clean, corrected_standard_id, officer_notes))
        log_id = cur.lastrowid
        conn.commit()
        conn.close()

        print(f"[FeedbackManager] Logged feedback #{log_id}: Action={action_clean} for standard {recommended_standard_id}")
        return log_id

    def get_boost_adjustments(self, query: str) -> Dict[str, float]:
        """
        Scans past feedback logs. If the current query has high lexical overlap (> 0.50)
        with a previously reviewed spec, returns boost adjustments:
        +0.20 for ACCEPT / CORRECT target, -0.25 for REJECT.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT spec_text, recommended_standard_id, action, corrected_standard_id FROM feedback_logs")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return {}

        query_tokens = tokenize_text(query)
        adjustments: Dict[str, float] = {}

        for spec_text, rec_id, action, corr_id in rows:
            logged_tokens = tokenize_text(spec_text)
            sim = jaccard_similarity(query_tokens, logged_tokens)

            if sim >= 0.45:
                # Strong match with prior officer-reviewed spec
                if action == "ACCEPT":
                    adjustments[rec_id] = adjustments.get(rec_id, 0.0) + (0.20 * sim)
                elif action == "CORRECT" and corr_id:
                    # Penalize mistaken recommendation and boost corrected standard
                    adjustments[rec_id] = adjustments.get(rec_id, 0.0) - (0.20 * sim)
                    adjustments[corr_id] = adjustments.get(corr_id, 0.0) + (0.25 * sim)
                elif action == "REJECT":
                    adjustments[rec_id] = adjustments.get(rec_id, 0.0) - (0.25 * sim)

        return adjustments

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Returns statistics of officer actions for dashboard/admin metrics."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT action, COUNT(*) FROM feedback_logs GROUP BY action")
        counts = dict(cur.fetchall())

        cur.execute("""
            SELECT id, spec_text, recommended_standard_id, action, corrected_standard_id, officer_notes, created_at
            FROM feedback_logs ORDER BY id DESC LIMIT 20
        """)
        recent_logs = []
        for r in cur.fetchall():
            recent_logs.append({
                "id": r[0],
                "spec_text": r[1],
                "recommended_standard_id": r[2],
                "action": r[3],
                "corrected_standard_id": r[4],
                "officer_notes": r[5],
                "created_at": r[6]
            })

        conn.close()
        return {
            "total_feedback_count": sum(counts.values()),
            "accepted_count": counts.get("ACCEPT", 0),
            "rejected_count": counts.get("REJECT", 0),
            "corrected_count": counts.get("CORRECT", 0),
            "recent_logs": recent_logs
        }
