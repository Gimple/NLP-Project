import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from autoCleaner import clean_text, simple_tokenize
import random
import time
import threading
from typing import Optional, Dict, Any

# Try to import Playwright
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Playwright not available. Falling back to BeautifulSoup only.")

# Common user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0"
]

# Thread-local storage for Playwright instances
thread_local = threading.local()


class URLAnalyzer:
    
    def __init__(self):
        self.headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        self.timeout = 30
        self.playwright_initialized = False
        
    def validate_url(self, url):
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
            return True, "Valid URL"
        except Exception:
            return False, "Invalid URL format"
    
    def extract_title(self, soup):
        title = ""
        
        # Strategy 1: <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Strategy 2: Open Graph meta tag (if title is too short)
        if not title or len(title) < 10:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '').strip()
        
        # Strategy 3: First <h1> tag (fallback)
        if not title or len(title) < 10:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text().strip()
        
        return title
    
    def extract_content(self, soup):
        content = ""
        
        # Common article content selectors
        article_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main'
        ]
        
        article_element = None
        for selector in article_selectors:
            article_element = soup.select_one(selector)
            if article_element:
                break
        
        if article_element:
            for unwanted in article_element.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                unwanted.decompose()
            
            paragraphs = article_element.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        if not content or len(content) < 100:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        return content
    
    def extract_source_domain(self, url):
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc.replace('www.', '')
        except Exception:
            return "unknown"
    
    def _get_playwright_instance(self):
        if not PLAYWRIGHT_AVAILABLE:
            return None
            
        thread_id = threading.get_ident()
        
        # Initialize Playwright for this thread if not already done
        if not hasattr(thread_local, 'playwright'):
            try:
                thread_local.playwright = sync_playwright().start()
                thread_local.browser = thread_local.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ],
                    ignore_default_args=['--enable-automation']
                )
                print(f"Initialized Playwright for thread {thread_id}")
            except Exception as e:
                print(f"⚠️ Failed to initialize Playwright for thread {thread_id}: {e}")
                if hasattr(thread_local, 'playwright'):
                    thread_local.playwright.stop()
                return None
                
        return thread_local

    def _scrape_with_playwright(self, url: str) -> Optional[Dict[str, Any]]:
        thread_data = self._get_playwright_instance()
        if not thread_data or not hasattr(thread_data, 'browser') or not thread_data.browser:
            print("[Playwright] Browser not available")
            return None

        context = None
        page = None
        
        try:
            # Create a new context with browser-like headers
            context = thread_data.browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1366, 'height': 768},
                locale='en-US',
                timezone_id='Asia/Manila',
                extra_http_headers={
                    **self.headers,
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': 'Windows',
                },
                bypass_csp=True,
                java_script_enabled=True,
                ignore_https_errors=True
            )
            
            # Create a new page
            page = context.new_page()
            
            # Set extra headers
            page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
                'DNT': '1'
            })
            
            # Disable WebDriver flag
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """)
            
            # Navigate to the URL with a realistic delay
            print(f"[Playwright] Loading: {url}")
            page.goto(
                url,
                timeout=60000,
                wait_until='domcontentloaded',
                referer='https://www.google.com/'
            )
            
            # Wait for dynamic content to load with realistic delays
            page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(random.uniform(1.5, 3.5))  # Human-like delay
            
            # Common content containers to wait for
            content_selectors = [
                'article',
                'main',
                'div[itemprop="articleBody"]',
                'div.article-content',
                'div.post-content',
                'div.entry-content',
                'div.content',
                'section',
                'div[class*="article"]',
                'div[class*="content"]',
                'div.story',
                'div.article-body',
                'div.article__content'
            ]
            
            # Try to wait for any of the content selectors
            content_element = None
            for selector in content_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    content_element = page.query_selector(selector)
                    if content_element:
                        break
                except Exception as e:
                    continue
            
            # Get the page content
            if content_element:
                content = content_element.inner_text()
            else:
                # Fallback to full page content
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                content = self.extract_content(soup)
            
            # Get the title
            title = page.title()
            if not title or len(title.strip()) < 10:
                title = self.extract_title(BeautifulSoup(page.content(), 'html.parser'))
            
            source = self.extract_source_domain(url)
            
            # Additional content extraction if needed
            if not content or len(content.strip()) < 100:
                paragraphs = page.query_selector_all('p')
                content = '\n'.join([p.inner_text().strip() for p in paragraphs if p.inner_text().strip()])
            
            print(f"[Playwright] Successfully extracted content from {source}")
            return {
                'title': title,
                'content': content,
                'source': source,
                'url': url,
                'method': 'playwright'
            }
            
        except Exception as e:
            print(f"[Playwright] Error: {str(e)}")
            return None
            
        finally:
            # Clean up resources
            try:
                if page:
                    page.close()
                if context:
                    context.close()
            except Exception as e:
                print(f"[Playwright] Error during cleanup: {e}")
                
    def __del__(self):
        # Cleanup method to be called when the object is destroyed
        if hasattr(thread_local, 'browser') and thread_local.browser:
            try:
                thread_local.browser.close()
            except:
                pass
        if hasattr(thread_local, 'playwright') and thread_local.playwright:
            try:
                thread_local.playwright.stop()
            except:
                pass

    def fetch_article_data(self, url, use_playwright_fallback: bool = True):
        # First try with BeautifulSoup
        try:
            # Make HTTP request with a random user agent
            headers = {**self.headers, 'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            title = self.extract_title(soup)
            content = self.extract_content(soup)
            source = self.extract_source_domain(url)
            
            # If content is too short, try with Playwright if enabled
            if use_playwright_fallback and PLAYWRIGHT_AVAILABLE and (not content or len(content.strip()) < 100):
                print(f"Content too short ({len(content or '')} chars), trying with Playwright...")
                playwright_result = self._scrape_with_playwright(url)
                if playwright_result and playwright_result.get('content'):
                    return playwright_result
            
            return {
                'title': title,
                'content': content,
                'source': source,
                'url': url,
                'method': 'beautifulsoup'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            
            # If request failed, try with Playwright if enabled
            if use_playwright_fallback and PLAYWRIGHT_AVAILABLE:
                print("Falling back to Playwright due to request error...")
                playwright_result = self._scrape_with_playwright(url)
                if playwright_result:
                    return playwright_result
            
            raise Exception(f"Failed to fetch URL: {str(e)}")
            
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            
            # If extraction failed, try with Playwright if enabled
            if use_playwright_fallback and PLAYWRIGHT_AVAILABLE:
                print("Falling back to Playwright due to extraction error...")
                playwright_result = self._scrape_with_playwright(url)
                if playwright_result:
                    return playwright_result
            
            raise Exception(f"Failed to extract article content: {str(e)}")
    
    def process_article_text(self, article_data, log=False):
        if log:
            print(f"\n=== URL ANALYSIS PIPELINE ===")
            print(f"Processing article: {article_data['title']}")
            print(f"Source: {article_data['source']}")
        
        # Clean title and content separately
        title_cleaned = clean_text(article_data['title'], log=log) if article_data['title'] else ''
        
        if log:
            print(f"\n--- Processing Article Content ---")
        content_cleaned = clean_text(article_data['content'], log=log) if article_data['content'] else ''
        
        combined_text = f"{title_cleaned} {content_cleaned}".strip()
        
        if log:
            print(f"\n--- Tokenizing Combined Text ---")
        tokens = simple_tokenize(combined_text) if combined_text else []
        
        if log:
            print(f"[pipeline] tokenization: {tokens}")
            print(f"[pipeline] token_count: {len(tokens)}")
            print(f"=== URL ANALYSIS COMPLETE ===\n")
        
        return {
            'title_cleaned': title_cleaned,
            'content_cleaned': content_cleaned,
            'combined_text': combined_text,
            'tokens': tokens,
            'token_count': len(tokens)
        }
    
    def analyze_url(self, url, log=False):
        # Validate URL format
        is_valid, validation_message = self.validate_url(url)
        if not is_valid:
            raise Exception(validation_message)
        
        # Fetch article data
        article_data = self.fetch_article_data(url)
        
        # Process text content
        processing_results = self.process_article_text(article_data, log=log)
        
        # Combine results
        return {
            'success': True,
            'article': article_data,
            'cleaned_text': processing_results['combined_text'],
            'tokens': processing_results['tokens'],
            'token_count': processing_results['token_count'],
            'processing_details': {
                'title_cleaned': processing_results['title_cleaned'],
                'content_cleaned': processing_results['content_cleaned']
            }
        }


def extract_article_content(url):
    analyzer = URLAnalyzer()
    return analyzer.fetch_article_data(url)
