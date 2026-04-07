import sqlite3
import os

class StateStore:
    """
    Manages the persistent state of the Hydra security agent using SQLite.
    Stores URLs, findings, and metadata to ensure scan resumption and deduplication.
    """
    
    def __init__(self, db_path="hydra_state.db"):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        """Creates the necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for tracking URL crawl status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crawl_state (
                    url TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for tracking site findings (Vulnerabilities)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    type TEXT,
                    severity TEXT,
                    description TEXT,
                    evidence TEXT,
                    confidence TEXT,
                    poc TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration: Ensure 'poc' column exists in case the table was created previously
            try:
                cursor.execute("ALTER TABLE findings ADD COLUMN poc TEXT")
            except sqlite3.OperationalError:
                pass # Column already exists
            
            conn.commit()
            
    def add_url(self, url, status="pending"):
        """Adds a URL to the crawl queue."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO crawl_state (url, status) VALUES (?, ?)",
                (url, status)
            )
            conn.commit()

    def update_url_status(self, url, status):
        """Updates the status of a specific URL (e.g., from 'pending' to 'visited')."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE crawl_state SET status = ? WHERE url = ?",
                (status, url)
            )
            conn.commit()

    def get_pending_urls(self):
        """Returns a list of all URLs with 'pending' status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM crawl_state WHERE status = 'pending'")
            return [row[0] for row in cursor.fetchall()]
            
    def add_finding(self, url, f_type, severity, description, evidence, confidence, poc=""):
        """Records a security finding in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO findings (url, type, severity, description, evidence, confidence, poc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url, f_type, severity, description, evidence, confidence, poc))
            conn.commit()

    def _get_all_findings(self):
        """Internal helper to retrieve all findings for reporting."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Access by column name
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM findings")
            return [dict(row) for row in cursor.fetchall()]
