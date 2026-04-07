import pytest
import json
from unittest.mock import MagicMock, patch
from hydra_a import SecurityAnalyzer

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def mock_ui():
    with patch('hydra_a.ui') as mock:
        yield mock

def test_analyzer_initialization(mock_llm):
    analyzer = SecurityAnalyzer(mock_llm)
    assert analyzer.llm == mock_llm

@pytest.mark.asyncio
async def test_analyze_page_finds_vulnerability(mock_llm, mock_ui):
    """Test that the analyzer identifies vulnerabilities from crawler data."""
    
    # Mock Analyzer Output
    analyzer_response = {
        "vulnerabilities": [
            {
                "type": "SQL Injection",
                "severity": "High",
                "description": "Potential SQLi in search field.",
                "confidence": "High",
                "evidence": "Search input reflected in query."
            }
        ]
    }
    
    # Mock Critic Output (Confirming)
    critic_response = {
        "analysis": "The finding is valid because X, Y, Z.",
        "correctness_score": 0.9,
        "final_verdict": "True Positive"
    }
    
    mock_llm.generate_completion.side_effect = [
        json.dumps(analyzer_response),
        json.dumps(critic_response)
    ]
    
    analyzer = SecurityAnalyzer(mock_llm)
    page_data = {
        "url": "http://example.com",
        "forms": [{"fields": [{"name": "search"}]}],
        "headers": {}
    }
    
    findings = await analyzer.analyze_page(page_data)
    
    assert len(findings) == 1
    assert findings[0]["type"] == "SQL Injection"
    assert findings[0]["confidence_score"] == 0.9
    mock_ui.discovery.assert_called()

@pytest.mark.asyncio
async def test_analyzer_critic_rejects_false_positive(mock_llm, mock_ui):
    """Test that the critic pass filters out false positives."""
    
    # Analyzer flags something
    analyzer_response = {
        "vulnerabilities": [{"type": "XSS", "severity": "Medium", "description": "Lame", "confidence": "Medium", "evidence": "text"}]
    }
    
    # Critic says it's wrong
    critic_response = {
        "analysis": "This is a false positive because the input is sanitized.",
        "correctness_score": 0.2,
        "final_verdict": "False Positive"
    }
    
    mock_llm.generate_completion.side_effect = [
        json.dumps(analyzer_response),
        json.dumps(critic_response)
    ]
    
    analyzer = SecurityAnalyzer(mock_llm)
    page_data = {"url": "http://example.com/test", "forms": [], "headers": {}}
    
    findings = await analyzer.analyze_page(page_data)
    
    # Findings should be filtered out due to low score/verdict
    assert len(findings) == 0
    mock_ui.info.assert_called_with("Critic rejected finding: XSS (Score: 0.2)")
