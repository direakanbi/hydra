import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class HydraCrawler:
    """
    The first head of the Hydra.
    This module fetches a given URL and extracts all links.
    """
    
    def __init__(self, start_url):
        """
        Initializes the crawler with a starting URL.
        """
        self.start_url = start_url
        self.internal_links = set()
        self.external_links = set()
    
    def _is_valid_url(self, url):
        """
        Helper function to check if a URL is valid.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def crawl_page(self):
        """
        Fetches the content of the start_url and extracts all links.
        Separates links into internal and external.
        """
        print(f"[*] Crawling: {self.start_url}")
        
        try:
            response = requests.get(self.start_url, timeout=10)
            # Raise an HTTPError if the response was an HTTP error
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                
                # Resolve relative URLs
                full_url = urljoin(self.start_url, href)
                
                if self._is_valid_url(full_url):
                    if urlparse(self.start_url).netloc == urlparse(full_url).netloc:
                        # Internal link (same domain)
                        self.internal_links.add(full_url)
                    else:
                        # External link (different domain)
                        self.external_links.add(full_url)
                        
            print("[+] Crawling complete.")
            print(f"[+] Found {len(self.internal_links)} internal links.")
            print(f"[+] Found {len(self.external_links)} external links.")

        except requests.exceptions.RequestException as e:
            print(f"[-] An error occurred: {e}")

#test use case
if __name__ == "__main__":
    
    target_url = "http://ums.caleb university.edu.ng" 
    
    crawler = HydraCrawler(target_url)
    crawler.crawl_page()
    
    print("\n--- Internal Links ---")
    for link in sorted(list(crawler.internal_links)):
        print(link)
    
    print("\n--- External Links ---")
    for link in sorted(list(crawler.external_links)):
        print(link)