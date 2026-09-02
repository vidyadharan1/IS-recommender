"""
Data ingestion, SQLite persistence, and catalog management for IS-Recommender.
"""
import json
import sqlite3
import os
from typing import List, Dict, Any, Optional
from is_recommender.config import CATALOG_JSON_PATH, SQLITE_DB_PATH

class DataLoader:
    def __init__(self, json_path=CATALOG_JSON_PATH, db_path=SQLITE_DB_PATH):
        self.json_path = json_path
        self.db_path = db_path
        self.standards: List[Dict[str, Any]] = []
        self._load_data()
        self._init_sqlite()

    def _load_data(self):
        """Loads standards from the JSON catalog."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Catalog JSON file not found at: {self.json_path}")
        
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.standards = json.load(f)
        print(f"[DataLoader] Loaded {len(self.standards)} standards from JSON catalog.")

    def _init_sqlite(self):
        """Initializes SQLite tables for standards, clauses, and feedback logs."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Standards table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS standards (
                standard_id TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                year INTEGER,
                title TEXT NOT NULL,
                sector TEXT NOT NULL,
                ics_code TEXT,
                scope TEXT,
                is_mandatory_qco INTEGER DEFAULT 0,
                superseded_by TEXT,
                keywords TEXT,
                gem_categories TEXT
            )
        """)

        # Clauses table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clauses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                standard_id TEXT NOT NULL,
                clause_no TEXT,
                title TEXT,
                text TEXT,
                FOREIGN KEY (standard_id) REFERENCES standards(standard_id)
            )
        """)

        # Feedback logs table for officer acceptance/rejections
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spec_text TEXT NOT NULL,
                recommended_standard_id TEXT,
                action TEXT NOT NULL,
                corrected_standard_id TEXT,
                officer_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexing for fast lookups
        cur.execute("CREATE INDEX IF NOT EXISTS idx_standards_code ON standards(code);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_standards_sector ON standards(sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clauses_standard ON clauses(standard_id);")

        # Populate standards table if empty
        cur.execute("SELECT COUNT(*) FROM standards")
        count = cur.fetchone()[0]
        if count == 0:
            print(f"[DataLoader] Populating SQLite database at {self.db_path}...")
            for s in self.standards:
                cur.execute("""
                    INSERT INTO standards (
                        standard_id, code, year, title, sector, ics_code,
                        scope, is_mandatory_qco, superseded_by, keywords, gem_categories
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s["standard_id"],
                    s["code"],
                    s.get("year", 2020),
                    s["title"],
                    s.get("sector", "General"),
                    s.get("ics_code", ""),
                    s.get("scope", ""),
                    1 if s.get("is_mandatory_qco", False) else 0,
                    s.get("superseded_by"),
                    json.dumps(s.get("keywords", [])),
                    json.dumps(s.get("gem_categories", []))
                ))

                for c in s.get("clauses", []):
                    cur.execute("""
                        INSERT INTO clauses (standard_id, clause_no, title, text)
                        VALUES (?, ?, ?, ?)
                    """, (s["standard_id"], c.get("clause_no", ""), c.get("title", ""), c.get("text", "")))

            conn.commit()
            print(f"[DataLoader] Successfully inserted {len(self.standards)} standards and their clauses into SQLite.")

        conn.close()

    def get_all_standards(self) -> List[Dict[str, Any]]:
        """Returns all loaded standards."""
        return self.standards

    def get_standard_by_id(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a specific standard by standard_id (e.g. 'IS 1786:2008')."""
        standard_id_clean = standard_id.strip().upper()
        for s in self.standards:
            if s["standard_id"].upper() == standard_id_clean:
                return s
            if s["code"].upper() == standard_id_clean:
                return s
        return None

    def search_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Filter standards by sector name."""
        return [s for s in self.standards if sector.lower() in s.get("sector", "").lower()]
