import json
import asyncio
from typing import List, Dict
from hydra_p import PoCGenerator

class SecurityAnalyzer:
    """
    The second head of the Hydra.
    Analyzes crawled page data using a Multi-Pass LLM approach (Analyzer + Critic).
    Ensures high-confidence results by cross-validating findings.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.poc_gen = PoCGenerator(llm_client)
        
    def _create_analyzer_prompt(self, page_data: Dict):
        """Builds the primary analysis prompt for the LLM."""
        return [
            {"role": "system", "content": "You are a professional security penetration tester. Analyze the provided web page data for vulnerabilities (OWASP Top 10, CWE). Response MUST be in JSON format."},
            {"role": "user", "content": f"Analyze the following page data: {json.dumps(page_data)}. Identify any vulnerabilities. Output JSON with a 'vulnerabilities' key containing a list of objects with: 'type', 'severity', 'description', 'confidence', 'evidence'."}
        ]
        
    def _create_critic_prompt(self, finding: Dict):
        """Builds the adversarial critic prompt for the second LLM pass."""
        return [
            {"role": "system", "content": "You are a senior security auditor. Your job is to DEBUNK potential security findings. Be skeptical and identify false positives. Response MUST be in JSON format."},
            {"role": "user", "content": f"Evaluate this potential finding: {json.dumps(finding)}. Is it a True Positive or a False Positive? Output JSON with: 'analysis', 'correctness_score' (0-1.0), 'final_verdict' (True Positive/False Positive)."}
        ]

    async def analyze_page(self, page_data: Dict) -> List[Dict]:
        """Runs the multi-pass analysis on the provided page data."""
        
        # 1. First Pass: Initial Analysis
        try:
            raw_analysis = self.llm.generate_completion(self._create_analyzer_prompt(page_data))
            # Clean possible markdown formatting from model output
            clean_json = raw_analysis.strip().strip("```json").strip("```")
            data = json.loads(clean_json)
            initial_vulnerabilities = data.get("vulnerabilities", [])
        except Exception as e:
            print(f"[-] Analyzer failure: {e}")
            return []
            
        validated_findings = []
        
        # 2. Second Pass: Adversarial Review for each finding
        for finding in initial_vulnerabilities:
            try:
                raw_critic = self.llm.generate_completion(self._create_critic_prompt(finding))
                clean_critic = raw_critic.strip().strip("```json").strip("```")
                critic_data = json.loads(clean_critic)
                
                # Rules for inclusion:
                # - Correctness Score > 0.7
                # - Final Verdict is True Positive (Case-insensitive)
                verdict = str(critic_data.get("final_verdict", "")).strip().lower()
                score = critic_data.get("correctness_score", 0)
                
                if score > 0.7 and "true positive" in verdict:
                    finding["confidence_score"] = score
                    # 3. Generate PoC for verified finding
                    print(f"[*] Generating PoC for {finding['type']}...")
                    finding["poc"] = self.poc_gen.generate_poc(finding)
                    validated_findings.append(finding)
                else:
                    print(f"[*] Critic rejected finding: {finding['type']} (Score: {score}, Verdict: {verdict})")
                    
            except Exception as e:
                print(f"[-] Critic failure for finding {finding['type']}: {e}")
                
        return validated_findings

if __name__ == "__main__":
    # Small integration test example
    from llm import LLMClient
    async def test():
        client = LLMClient()
        analyzer = SecurityAnalyzer(client)
        page_data = {"url": "http://example.com", "forms": [{"fields": [{"name": "username"}]}]}
        findings = await analyzer.analyze_page(page_data)
        print(findings)
        
    asyncio.run(test())
