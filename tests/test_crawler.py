import http.server
import threading
import time
import pytest
import os
from hydra_c import PlaywrightCrawler
from hydra_s import StateStore

# --- Mock Server Setup ---
class MockServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("X-Security-Header", "Present")
            self.end_headers()
            self.wfile.write(b"<html><body><a href='/page1'>Page 1</a><form action='/login' method='POST'><input name='user'></form></body></html>")
        elif self.path == "/page1":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><a href='/'>Home</a></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

def run_mock_server():
    server = http.server.HTTPServer(('127.0.0.1', 8080), MockServerHandler)
    server.serve_forever()

@pytest.fixture(scope="module", autouse=True)
def mock_server():
    thread = threading.Thread(target=run_mock_server, daemon=True)
    thread.start()
    time.sleep(1) # Give server time to start
    yield
    # No easy way to stop serve_forever, but daemon=True handles it

# --- Tests ---

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "crawler_test.db"
    return str(db_file)

def test_crawler_initialization(temp_db):
    store = StateStore(temp_db)
    crawler = PlaywrightCrawler("http://127.0.0.1:8080", store)
    assert crawler.start_url == "http://127.0.0.1:8080"
    assert crawler.store == store

@pytest.mark.asyncio
async def test_crawl_single_page(temp_db):
    """Test that crawler extracts links and headers from a single page."""
    store = StateStore(temp_db)
    crawler = PlaywrightCrawler("http://127.0.0.1:8080", store)
    
    # Run a single page crawl
    await crawler.crawl_page("http://127.0.0.1:8080")
    
    # Check if links were added to store (Page 1)
    pending = store.get_pending_urls()
    assert any("page1" in url for url in pending)
    
    # Check if the start URL is marked as visited (Implementation detail: we'll handle this in the crawler)
    # For now, let's just assert the crawler found the links.

@pytest.mark.asyncio
async def test_form_extraction(temp_db):
    """Test that the crawler identifies forms on the page."""
    store = StateStore(temp_db)
    crawler = PlaywrightCrawler("http://127.0.0.1:8080", store)
    
    page_data = await crawler.crawl_page("http://127.0.0.1:8080")
    forms = page_data.get("forms", [])
    assert len(forms) == 1
    assert forms[0]["action"] == "/login"
    assert forms[0]["method"] == "POST"
    assert "user" in [f["name"] for f in forms[0]["fields"]]

@pytest.mark.asyncio
async def test_header_extraction(temp_db):
    """Test that the crawler captures security headers."""
    store = StateStore(temp_db)
    crawler = PlaywrightCrawler("http://127.0.0.1:8080", store)
    
    page_data = await crawler.crawl_page("http://127.0.0.1:8080")
    headers = page_data.get("headers", {})
    # Playwright normalizes header keys to lowercase
    assert headers.get("x-security-header") == "Present"
