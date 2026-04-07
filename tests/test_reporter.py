import pytest
from unittest.mock import MagicMock
from hydra_r import SecurityReporter

@pytest.fixture
def mock_store():
    store = MagicMock()
    # Mock data as returned by sqlite3 fetchall typically
    store._get_all_findings.return_value = [
        {
            "id": 1,
            "url": "http://example.com/login",
            "type": "SQL Injection",
            "severity": "High",
            "description": "Found potential blind SQLi.",
            "evidence": "Payload sleep(5) delayed response.",
            "confidence": "90%",
            "timestamp": "2026-04-05"
        }
    ]
    return store

def test_reporter_initialization(mock_store):
    reporter = SecurityReporter(mock_store)
    assert reporter.store == mock_store

def test_generate_markdown_report_structure(mock_store):
    """Test that the reporter generates a valid-looking MD structure."""
    reporter = SecurityReporter(mock_store)
    report = reporter.generate_markdown_report()
    
    assert "# Hydra Security Report" in report
    assert "## Summary" in report
    assert "## Detailed Findings" in report
    assert "### SQL Injection" in report
    assert "http://example.com/login" in report
    assert "Payload sleep(5) delayed response." in report
    assert "90%" in report

def test_reporter_handles_no_findings(mock_store):
    """Test that the reporter handles empty findings list gracefully."""
    mock_store._get_all_findings.return_value = []
    reporter = SecurityReporter(mock_store)
    report = reporter.generate_markdown_report()
    
    assert "No high-confidence vulnerabilities found." in report
