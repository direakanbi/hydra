import asyncio
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from hydra_s import StateStore
import hydra_ui as ui

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
        """Removes query parameters and fragments to identify unique page 'templates'."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    async def crawl_page(self, url):
        """Fetches a page with Playwright, extracts data, and updates the StateStore."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            ui.info(f"Crawling: {url}")
            
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                if not response:
                    ui.error(f"No response from {url}")
                    return {}
                
                headers = response.headers
                links = await page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)")
                
                for link in links:
                    full_url = urljoin(url, link)
                    if self._is_internal(full_url):
                        normalized = self._normalize_url(full_url)
                        if normalized not in self.visited_templates:
                            self.store.add_url(full_url, status="pending")
                
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
                
                page_data = {"url": url, "headers": headers, "forms": forms, "links": links}
                
                # Mark as visited
                self.store.update_url_status(url, "visited")
                self.visited_templates.add(self._normalize_url(url))
                
                ui.success(f"Crawl complete for {url}. Found {len(links)} links and {len(forms)} forms.")
                return page_data

            except Exception as e:
                ui.error(f"Error crawling {url}: {e}")
                return {}
            finally:
                await browser.close()
