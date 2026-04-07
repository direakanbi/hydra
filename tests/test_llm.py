import pytest
from unittest.mock import MagicMock, patch
from llm import LLMClient

@pytest.fixture
def mock_openai(mocker):
    """Mocks the OpenAI client and its response."""
    mock_client = MagicMock()
    mocker.patch('llm.OpenAI', return_value=mock_client)
    
    # Mock the chat.completions.create response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response content"))]
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client

def test_llm_client_initialization(mocker):
    """Test that the LLMClient initialized the OpenAI client with correct base_url."""
    mocker.patch('os.environ.get', return_value="fake_api_key")
    patch_openai = mocker.patch('llm.OpenAI')
    
    client = LLMClient()
    patch_openai.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1",
        api_key="fake_api_key"
    )

def test_generate_completion(mock_openai, mocker):
    """Test generating a completion using the LLMClient."""
    mocker.patch('os.environ.get', return_value="fake_api_key")
    client = LLMClient()
    
    response = client.generate_completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="google/gemini-pro-1.5"
    )
    
    assert response == "Mocked response content"
    mock_openai.chat.completions.create.assert_called_once_with(
        model="google/gemini-pro-1.5",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=4000,
        extra_headers={
            "HTTP-Referer": "https://github.com/hydra-security/hydra",
            "X-Title": "Hydra Security Agent"
        }
    )

def test_generate_completion_error(mock_openai, mocker):
    """Test that LLMClient handles API errors gracefully."""
    mocker.patch('os.environ.get', return_value="fake_api_key")
    mock_openai.chat.completions.create.side_effect = Exception("API Connection Error")
    
    client = LLMClient()
    with pytest.raises(Exception) as excinfo:
        client.generate_completion([{"role": "user", "content": "Hello"}])
    
    assert "API Connection Error" in str(excinfo.value)
