import os
import sqlite3
import pytest
from hydra_s import StateStore

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_hydra.db"
    return str(db_file)

def test_state_store_initialization(temp_db):
    """Test that the StateStore creates the database and tables."""
    store = StateStore(temp_db)
    assert os.path.exists(temp_db)
    
    # Check if tables exist
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
    assert cursor.fetchone() is not None
    conn.close()

def test_add_url_to_state(temp_db):
    """Test adding a URL to the crawl state."""
    store = StateStore(temp_db)
    store.add_url("http://example.com", status="pending")
    
    # Verify in DB
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT url, status FROM urls WHERE url='http://example.com';")
    row = cursor.fetchone()
    assert row == ("http://example.com", "pending")
    conn.close()

def test_update_url_status(temp_db):
    """Test updating the status of a URL."""
    store = StateStore(temp_db)
    store.add_url("http://example.com", status="pending")
    store.update_url_status("http://example.com", "visited")
    
    # Verify in DB
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM urls WHERE url='http://example.com';")
    assert cursor.fetchone()[0] == "visited"
    conn.close()

def test_get_pending_urls(temp_db):
    """Test fetching all pending URLs."""
    store = StateStore(temp_db)
    store.add_url("http://site1.com", status="pending")
    store.add_url("http://site2.com", status="visited")
    store.add_url("http://site3.com", status="pending")
    
    pending = store.get_pending_urls()
    assert len(pending) == 2
    assert "http://site1.com" in pending
    assert "http://site3.com" in pending
