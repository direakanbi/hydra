import json
from typing import List, Dict
from hydra_p import PoCGenerator
import hydra_ui as ui

class SecurityAnalyzer:
    """
    The second head of the Hydra.
    Analyzes crawled page data using a Multi-Pass LLM approach (Analyzer + Critic).
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.poc_gen = PoCGenerator(llm_client)
        
    def _create_analyzer_prompt(self, page_data: Dict):
        return [
            {"role": "system", "content": "You are a professional security penetration tester. Analyze for vulnerabilities. Response MUST be in JSON format."},
            {"role": "user", "content": f"Analyze page data: {json.dumps(page_data)}. Output JSON with 'vulnerabilities' key."}
        ]
        
    def _create_critic_prompt(self, finding: Dict):
        return [
            {"role": "system", "content": "You are a senior security auditor. DEBUNK findings. Response MUST be in JSON format."},
            {"role": "user", "content": f"Evaluate finding: {json.dumps(finding)}. Output JSON with 'analysis', 'correctness_score', 'final_verdict'."}
        ]

    async def analyze_page(self, page_data: Dict) -> List[Dict]:
        """Runs the multi-pass analysis on the provided page data."""
        ui.analysis("Initiating Deep-Pass LLM Analysis...")
        
        try:
            raw_analysis = self.llm.generate_completion(self._create_analyzer_prompt(page_data))
            clean_json = raw_analysis.strip().strip("```json").strip("```")
            data = json.loads(clean_json)
            initial_vulnerabilities = data.get("vulnerabilities", [])
        except Exception as e:
            ui.error(f"LLM Analyzer failure: {e}")
            return []
            
        validated_findings = []
        for finding in initial_vulnerabilities:
            try:
                ui.analysis(f"Critic reviewing finding: {finding.get('type', 'Unknown')}...")
                raw_critic = self.llm.generate_completion(self._create_critic_prompt(finding))
                clean_critic = raw_critic.strip().strip("```json").strip("```")
                critic_data = json.loads(clean_critic)
                
                verdict = str(critic_data.get("final_verdict", "")).strip().lower()
                score = critic_data.get("correctness_score", 0)
                
                if score > 0.7 and "true positive" in verdict:
                    ui.discovery(f"Verified {finding['type']} (Confidence: {score})")
                    finding["confidence_score"] = score
                    finding["poc"] = self.poc_gen.generate_poc(finding)
                    validated_findings.append(finding)
                else:
                    ui.info(f"Critic rejected finding: {finding['type']} (Score: {score})")
                    
            except Exception as e:
                ui.error(f"LLM Critic failure: {e}")
                
        return validated_findings
