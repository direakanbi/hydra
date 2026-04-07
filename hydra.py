# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""
{CYAN}{BOLD}
    __  Transitions
   / / / /_  ______  / /________ _
  / /_/ / / / / __ \/ ___/ __ `/
 / __  / /_/ / /_/ / /  / /_/ /
/_/ /_/\__, / .___/_/   \__,_/ {RESET}{MAGENTA}(V2){RESET}{CYAN}
      /____/_/                 {RESET}
      
    {BOLD}{WHITE}The AI-Powered Security Multi-Head Agent{RESET}
    {BLUE}Created by: {BOLD}@direakanbi{RESET}
    {BLUE}GitHub: {BOLD}https://github.com/direakanbi/hydra{RESET}
"""

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
        print(BANNER)
        print(f"{BLUE}[*] Target URL:{RESET} {BOLD}{self.start_url}{RESET}")
        print(f"{BLUE}[*] Max Pages: {RESET}{BOLD}{max_pages}{RESET}\n")
        
        # 1. Initialize queue with start URL
        self.store.add_url(self.start_url)
        
        pages_scanned = 0
        
        # 2. Main Scan Loop
        while pages_scanned < max_pages:
            pending = self.store.get_pending_urls()
            if not pending:
                print(f"{GREEN}[+] Scan complete: No more URLs to crawl.{RESET}")
                break
                
            current_url = pending[0]
            print(f"{YELLOW}[*] [{pages_scanned + 1}/{max_pages}] Scanning:{RESET} {current_url}")
            
            # Phase A: Crawl
            page_data = await self.crawler.crawl_page(current_url)
            
            if page_data:
                # Phase B: Analyze
                print(f"{MAGENTA}[*] Deep-Analyzing page content with LLM...{RESET}")
                findings = await self.analyzer.analyze_page(page_data)
                
                if findings:
                    print(f"{RED}[!] Found {len(findings)} potential vulnerabilities!{RESET}")
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
                else:
                    print(f"{GREEN}[+] Analysis clean: No vulnerabilities detected.{RESET}")
            
            pages_scanned += 1
            
        print(f"\n{BLUE}[*] Finalizing scan. Generating professional report...{RESET}")
        
        # 3. Report Generation
        report_md = self.reporter.generate_markdown_report()
        report_file = "hydra_report.md"
        
        with open(report_file, "w") as f:
            f.write(report_md)
            
        print(f"{GREEN}[+]{BOLD} SUCCESS:{RESET} Report saved to {BOLD}{report_file}{RESET}")
        return report_file

if __name__ == "__main__":
    import sys
    # Initialize colorama/windows support if on windows
    if os.name == 'nt':
        os.system('color')

    
    if len(sys.argv) < 2:
        print("Usage: python hydra.py <target_url>")
        sys.exit(1)
        
    target = sys.argv[1]
    hydra = Hydra(target)
    
    asyncio.run(hydra.run(max_pages=5))
