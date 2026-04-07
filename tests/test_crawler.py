import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from hydra_c import PlaywrightCrawler

@pytest.fixture
def mock_store():
    return MagicMock()

@pytest.fixture
def mock_ui():
    with patch('hydra_c.ui') as mock:
        yield mock

@pytest.mark.asyncio
async def test_crawler_initialization(mock_store):
    crawler = PlaywrightCrawler("http://example.com", mock_store)
    assert crawler.start_url == "http://example.com"
    assert crawler.base_domain == "example.com"

@pytest.mark.asyncio
async def test_crawl_page_success(mock_store, mock_ui):
    """Test standard crawling of a page with links and forms."""
    
    # Mock Playwright interactions
    with patch('hydra_c.async_playwright') as mock_pw:
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_pw.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock Page Content
        mock_page.goto.return_value = MagicMock(headers={"server": "nginx"})
        mock_page.evaluate.side_effect = [
            ["http://example.com/about", "http://external.com"], # Links
            [{"action": "/login", "method": "POST", "fields": [{"name": "user"}]}] # Forms
        ]
        
        crawler = PlaywrightCrawler("http://example.com", mock_store)
        data = await crawler.crawl_page("http://example.com")
        
        assert data["url"] == "http://example.com"
        assert len(data["forms"]) == 1
        mock_store.add_url.assert_called_with("http://example.com/about", status="pending")
        mock_ui.success.assert_called()
