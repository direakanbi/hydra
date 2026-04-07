import sqlite3
from datetime import datetime
import hydra_ui as ui

class StateStore:
    """
    The persistent memory of the Hydra.
    Manages URLs to crawl and security findings using SQLite.
    """
    
    def __init__(self, db_path="hydra_state.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    url TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    timestamp DATETIME
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    type TEXT,
                    severity TEXT,
                    description TEXT,
                    evidence TEXT,
                    confidence TEXT,
                    poc TEXT,
                    timestamp DATETIME
                )
            """)

    def add_url(self, url, status='pending'):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT OR IGNORE INTO urls (url, status, timestamp) VALUES (?, ?, ?)",
                             (url, status, datetime.now()))
        except Exception as e:
            ui.error(f"Failed to add URL to state: {e}")

    def update_url_status(self, url, status):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE urls SET status = ?, timestamp = ? WHERE url = ?",
                         (status, datetime.now(), url))

    def get_pending_urls(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT url FROM urls WHERE status = 'pending'")
            return [row[0] for row in cursor.fetchall()]

    def add_finding(self, url, f_type, severity, description, evidence, confidence, poc=''):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO findings (url, type, severity, description, evidence, confidence, poc, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (url, f_type, severity, description, evidence, confidence, poc, datetime.now()))
        ui.success(f"Persisted finding: {f_type} at {url}")

    def _get_all_findings(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM findings ORDER BY severity DESC")
            return [dict(row) for row in cursor.fetchall()]
