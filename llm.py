import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMClient:
    """
    Client for interacting with LLM models via OpenRouter (using OpenAI compatibility).
    """
    
    def __init__(self, api_key=None):
        """Initializes the LLMClient with API credentials."""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment.")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
    def generate_completion(self, messages, model="openrouter/free"):
        """
        Sends a list of messages to the specified LLM model and returns the response content.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4000,
                extra_headers={
                    "HTTP-Referer": "https://github.com/hydra-security/hydra",
                    "X-Title": "Hydra Security Agent"
                }
            )
            return response.choices[0].message.content
            
        except Exception as e:
            # Re-raise or log as needed for higher level error handling
            raise Exception(f"Failed to generate completion: {e}")

# Maintain backwards compatibility or simple test script if run directly
if __name__ == "__main__":
    try:
        client = LLMClient()
        test_messages = [{"role": "user", "content": "What is security testing?"}]
        response = client.generate_completion(test_messages)
        print("\n--- Response ---")
        print(response)
    except Exception as e:
        print(colored(f"Error: {e}", "red"))