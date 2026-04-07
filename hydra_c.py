import asyncio
import re
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from hydra_s import StateStore

class PlaywrightCrawler:
    """
    The first head of the Hydra (V2).
    Uses Playwright to crawl JavaScript-heavy sites, capturing links, forms, and headers.
    Integrated with the SQLite StateStore for persistent progress tracking.
    """
    
    def __init__(self, start_url, store: StateStore):
        self.start_url = start_url
        self.store = store
        self.base_domain = urlparse(start_url).netloc
        self.visited_templates = set()
        
    def _is_internal(self, url):
        """Checks if a URL belongs to the same domain as the start URL."""
        return urlparse(url).netloc == self.base_domain
        
    def _normalize_url(self, url):
        """
        Heuristic template normalization. 
        Removes query parameters and fragments to identify unique page 'templates'.
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    async def crawl_page(self, url):
        """
        Fetches a page with Playwright, extracts data, and updates the StateStore.
        Returns a dictionary of findings for the Analyzer.
        """
        async with async_playwright() as p:
            # We use an incognito-style context to avoid side effects
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"[*] Browsing: {url}")
            
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                if not response:
                    print(f"[-] No response from {url}")
                    return {}
                
                # 1. Capture Headers
                headers = response.headers
                
                # 2. Extract Links
                links = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                """)
                
                for link in links:
                    full_url = urljoin(url, link)
                    if self._is_internal(full_url):
                        # Normalize to avoid scanning same template (e.g. /product/1 vs /product/2)
                        normalized = self._normalize_url(full_url)
                        if normalized not in self.visited_templates:
                            self.store.add_url(full_url, status="pending")
                            # We keep the raw URL in the queue but the normalized one in our 'templates' filter
                
                # 3. Extract Forms
                forms = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('form')).map(form => {
                        return {
                            action: form.getAttribute('action') || window.location.pathname,
                            method: (form.getAttribute('method') || 'GET').toUpperCase(),
                            fields: Array.from(form.querySelectorAll('input, textarea, select')).map(input => {
                                return {
                                    name: input.getAttribute('name') || input.getAttribute('id'),
                                    type: input.getAttribute('type') || 'text'
                                }
                            })
                        }
                    })
                """)
                
                page_data = {
                    "url": url,
                    "headers": headers,
                    "forms": forms,
                    "links": links
                }
                
                # Mark as visited in the store
                self.store.update_url_status(url, "visited")
                self.visited_templates.add(self._normalize_url(url))
                
                print(f"[+] Crawl complete for {url}. Found {len(links)} links and {len(forms)} forms.")
                
                return page_data

            except Exception as e:
                print(f"[-] Error crawling {url}: {e}")
                return {}
            finally:
                await browser.close()

# test use case
if __name__ == "__main__":
    async def run_test():
        store = StateStore("hydra_test.db")
        target = "https://example.com"
        crawler = PlaywrightCrawler(target, store)
        await crawler.crawl_page(target)
        
    asyncio.run(run_test())
