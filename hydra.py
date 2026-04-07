import asyncio
import os
import sys
from hydra_s import StateStore
from llm import LLMClient
from hydra_c import PlaywrightCrawler
from hydra_a import SecurityAnalyzer
from hydra_r import SecurityReporter
import hydra_ui as ui

class Hydra:
    """
    The Master Head of the Hydra.
    Orchestrates crawling, analysis, and dual-format reporting.
    """
    
    def __init__(self, start_url, db_path="hydra_state.db"):
        self.start_url = start_url
        self.db_path = db_path
        
        self.store = StateStore(self.db_path)
        self.llm = LLMClient()
        self.crawler = PlaywrightCrawler(self.start_url, self.store)
        self.analyzer = SecurityAnalyzer(self.llm)
        self.reporter = SecurityReporter(self.store)
        
    async def run(self, max_pages=10):
        """Executes the full security scan workflow."""
        ui.init_ui()
        ui.print_banner()
        
        ui.info(f"Target URL: {ui.BOLD}{self.start_url}{ui.RESET}")
        ui.info(f"Max Pages: {ui.BOLD}{max_pages}{ui.RESET}\n")
        
        self.store.add_url(self.start_url)
        pages_scanned = 0
        
        while pages_scanned < max_pages:
            pending = self.store.get_pending_urls()
            if not pending:
                ui.success("Scan complete: No more URLs to crawl.")
                break
                
            current_url = pending[0]
            ui.info(f"[{pages_scanned + 1}/{max_pages}] Scanning: {current_url}")
            
            page_data = await self.crawler.crawl_page(current_url)
            
            if page_data:
                findings = await self.analyzer.analyze_page(page_data)
                
                if findings:
                    ui.discovery(f"Found {len(findings)} potential vulnerabilities!")
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
            
        ui.info("\nFinalizing scan. Generating reports...")
        
        # Dual-Format Reporting
        report_md = self.reporter.generate_markdown_report()
        report_txt = self.reporter.generate_text_report()
        
        with open("hydra_report.md", "w") as f:
            f.write(report_md)
        with open("hydra_report.txt", "w") as f:
            f.write(report_txt)
            
        ui.success(f"Reports saved: {ui.BOLD}hydra_report.md{ui.RESET} and {ui.BOLD}hydra_report.txt{ui.RESET}")
        return "hydra_report.txt"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hydra.py <target_url>")
        sys.exit(1)
        
    target = sys.argv[1]
    hydra = Hydra(target)
    asyncio.run(hydra.run(max_pages=5))
