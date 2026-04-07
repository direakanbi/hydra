import json
from llm import LLMClient

class PoCGenerator:
    """
    The Verification Head of the Hydra.
    Generates minimal, safe Python scripts to verify security findings.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    def _create_poc_prompt(self, finding: dict):
        """Builds a prompt to generate a Python PoC script."""
        return [
            {"role": "system", "content": "You are a professional security automation engineer. Your job is to generate a MINIMAL and SAFE Python script to verify a documented security finding. Use 'requests' or 'playwright'. OUTPUT MUST BE A JSON OBJECT containing a 'script' key with the python code as a string."},
            {"role": "user", "content": f"Generate a PoC for this finding: {json.dumps(finding)}. The script should only perform a safe verification (e.g., check for a header, or a non-destructive payload). Ensure the code is self-contained and runnable."}
        ]
        
    def generate_poc(self, finding: dict) -> str:
        """Generates a Python verification script for a given finding."""
        try:
            raw_response = self.llm.generate_completion(self._create_poc_prompt(finding))
            # Clean possible markdown formatting
            clean_json = raw_response.strip().strip("```json").strip("```")
            data = json.loads(clean_json)
            return data.get("script", "# Could not generate PoC script.")
        except Exception as e:
            return f"# PoC Generation failed: {str(e)}"

# Example use
if __name__ == "__main__":
    client = LLMClient()
    gen = PoCGenerator(client)
    sample_finding = {
        "url": "http://example.com",
        "type": "XSS",
        "evidence": "Input 'search' is reflected in the page without escaping."
    }
    print(gen.generate_poc(sample_finding))
