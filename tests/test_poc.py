import pytest
import json
from unittest.mock import MagicMock
from hydra_p import PoCGenerator

@pytest.fixture
def mock_llm():
    return MagicMock()

def test_poc_generation_v2(mock_llm):
    """Test that the PoC generator returns a script from JSON LLM output."""
    mock_response = {
        "script": "import requests\nprint('PoC Verified')"
    }
    mock_llm.generate_completion.return_value = json.dumps(mock_response)
    
    gen = PoCGenerator(mock_llm)
    finding = {"type": "XSS", "url": "http://test.com"}
    
    script = gen.generate_poc(finding)
    assert "import requests" in script
    assert "PoC Verified" in script

def test_poc_generation_failure(mock_llm):
    """Test that it handles LLM failures gracefully."""
    mock_llm.generate_completion.side_effect = Exception("API Error")
    
    gen = PoCGenerator(mock_llm)
    script = gen.generate_poc({"type": "XSS"})
    
    assert "# PoC Generation failed" in script
