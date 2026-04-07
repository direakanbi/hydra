import asyncio
import os
from hydra_s import StateStore
from llm import LLMClient
from hydra_c import PlaywrightCrawler
from hydra_a import SecurityAnalyzer
from hydra_r import SecurityReporter

class Hydra:
    """
    The Master Head of the Hydra.
    Orchestrates the crawling, analysis, and reporting phases.
    """
    
    def __init__(self, start_url, db_path="hydra_state.db"):
        self.start_url = start_url
        self.db_path = db_path
        
        # Initialize sub-modules
        self.store = StateStore(self.db_path)
        self.llm = LLMClient()
        self.crawler = PlaywrightCrawler(self.start_url, self.store)
        self.analyzer = SecurityAnalyzer(self.llm)
        self.reporter = SecurityReporter(self.store)
        
    async def run(self, max_pages=10):
        """
        Executes the full security scan workflow.
        """
        print(f"\n[!] Starting Hydra Scan: {self.start_url}")
        print(f"[!] Max Pages: {max_pages}")
        
        # 1. Initialize queue with start URL
        self.store.add_url(self.start_url)
        
        pages_scanned = 0
        
        # 2. Main Scan Loop
        while pages_scanned < max_pages:
            pending = self.store.get_pending_urls()
            if not pending:
                print("[+] No more URLs to crawl.")
                break
                
            current_url = pending[0]
            
            # Phase A: Crawl
            page_data = await self.crawler.crawl_page(current_url)
            
            if page_data:
                # Phase B: Analyze
                findings = await self.analyzer.analyze_page(page_data)
                
                # Phase C: Persist Findings
                for f in findings:
                    self.store.add_finding(
                        url=current_url,
                        f_type=f['type'],
                        severity=f['severity'],
                        description=f['description'],
                        evidence=f['evidence'],
                        confidence=str(f.get('confidence_score', 'High')),
                        poc=f.get('poc', '')
                    )
            
            pages_scanned += 1
            
        print("\n[!] Scan complete. Generating report...")
        
        # 3. Report Generation
        report_md = self.reporter.generate_markdown_report()
        report_file = "hydra_report.md"
        
        with open(report_file, "w") as f:
            f.write(report_md)
            
        print(f"[+] Report saved to {report_file}")
        return report_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hydra.py <target_url>")
        sys.exit(1)
        
    target = sys.argv[1]
    hydra = Hydra(target)
    
    asyncio.run(hydra.run(max_pages=5))
