import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from hydra import Hydra

@pytest.fixture
def mock_ui():
    with patch('hydra.ui') as mock:
        yield mock

@pytest.fixture
def mock_store():
    with patch('hydra.StateStore') as mock:
        yield mock

@pytest.fixture
def mock_crawler():
    with patch('hydra.PlaywrightCrawler') as mock:
        yield mock

@pytest.fixture
def mock_analyzer():
    with patch('hydra.SecurityAnalyzer') as mock:
        yield mock

@pytest.fixture
def mock_reporter():
    with patch('hydra.SecurityReporter') as mock:
        yield mock

@pytest.fixture
def mock_llm_client():
    with patch('hydra.LLMClient') as mock:
        yield mock

@pytest.mark.asyncio
async def test_hydra_run_coordination(mock_ui, mock_store, mock_crawler, mock_analyzer, mock_reporter, mock_llm_client):
    """Test that the main Hydra orchestrator coordinates crawling, analysis, and reporting."""
    
    # Setup Mocks
    mock_store_instance = mock_store.return_value
    mock_store_instance.get_pending_urls.side_effect = [["http://example.com"], []] # Loop 1 then empty
    
    mock_crawler_instance = mock_crawler.return_value
    mock_crawler_instance.crawl_page = AsyncMock(return_value={"url": "http://example.com", "data": "dummy"})
    
    mock_analyzer_instance = mock_analyzer.return_value
    mock_analyzer_instance.analyze_page = AsyncMock(return_value=[{"type": "Bug", "severity": "High", "description": "Lame", "evidence": "text"}])
    
    mock_reporter_instance = mock_reporter.return_value
    mock_reporter_instance.generate_markdown_report.return_value = "MD Report"
    mock_reporter_instance.generate_text_report.return_value = "TXT Report"
    
    hydra_engine = Hydra("http://example.com")
    
    # Mock open for report files
    with patch('builtins.open', MagicMock()):
        await hydra_engine.run(max_pages=1)
    
    # Verify Coordination
    mock_store_instance.add_url.assert_called()
    mock_crawler_instance.crawl_page.assert_called_with("http://example.com")
    mock_analyzer_instance.analyze_page.assert_called()
    mock_store_instance.add_finding.assert_called()
    mock_reporter_instance.generate_markdown_report.assert_called()
    mock_reporter_instance.generate_text_report.assert_called()
    mock_ui.success.assert_called()
