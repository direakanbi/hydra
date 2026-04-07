import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from hydra import Hydra

@pytest.fixture
def mock_components():
    return {
        "store": MagicMock(),
        "crawler": AsyncMock(),
        "analyzer": AsyncMock(),
        "reporter": MagicMock()
    }

@pytest.mark.asyncio
async def test_hydra_orchestration_flow(mock_components):
    """Test that Hydra calls the modules in the correct order."""
    
    # Setup Mocks
    mock_components["crawler"].crawl_page.return_value = {"url": "http://test.com", "data": "dummy"}
    mock_components["analyzer"].analyze_page.return_value = [{"type": "Vuln", "severity": "High", "description": "desc", "evidence": "evid"}]
    mock_components["reporter"].generate_markdown_report.return_value = "# Report"
    
    # Mock Store setup
    mock_components["store"].get_pending_urls.side_effect = [
        ["http://test.com"], # First call for crawl queue
        [] # Second call (queue empty)
    ]
    
    # Patch the initializations inside Hydra.__init__
    with patch('hydra.StateStore', return_value=mock_components["store"]), \
         patch('hydra.LLMClient', return_value=MagicMock()), \
         patch('hydra.PlaywrightCrawler', return_value=mock_components["crawler"]), \
         patch('hydra.SecurityAnalyzer', return_value=mock_components["analyzer"]), \
         patch('hydra.SecurityReporter', return_value=mock_components["reporter"]):
        
        hydra = Hydra("http://test.com")
        
        # Run Orchestrator
        report_path = await hydra.run(max_pages=1)
        
        # Verify Crawler was called
        mock_components["crawler"].crawl_page.assert_called_once_with("http://test.com")
        
        # Verify Analyzer was called
        mock_components["analyzer"].analyze_page.assert_called_once()
        
        # Verify Store.add_finding was called
        mock_components["store"].add_finding.assert_called_once()
        
        # Verify Reporter was called
        mock_components["reporter"].generate_markdown_report.assert_called_once()
        
        assert report_path == "hydra_report.md"
