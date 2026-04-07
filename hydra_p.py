import json
from llm import LLMClient
import hydra_ui as ui

class PoCGenerator:
    """
    The Verification Head of the Hydra.
    Generates minimal, safe Python scripts to verify security findings.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    def _create_poc_prompt(self, finding: dict):
        return [
            {"role": "system", "content": "You are a professional security automation engineer. Generate a MINIMAL and SAFE Python script to verify. OUTPUT JSON with 'script' key."},
            {"role": "user", "content": f"Generate PoC for: {json.dumps(finding)}."}
        ]
        
    def generate_poc(self, finding: dict) -> str:
        """Generates a Python verification script for a given finding."""
        ui.info(f"Generating automated PoC script for {finding['type']}...")
        try:
            raw_response = self.llm.generate_completion(self._create_poc_prompt(finding))
            clean_json = raw_response.strip().strip("```json").strip("```")
            data = json.loads(clean_json)
            script = data.get("script", "# Could not generate PoC script.")
            ui.success(f"PoC generated successfully.")
            return script
        except Exception as e:
            ui.error(f"PoC Generation failed: {str(e)}")
            return f"# PoC Generation failed: {str(e)}"
