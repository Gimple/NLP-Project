import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from autoCleaner import clean_text, simple_tokenize


class URLAnalyzer:
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
        
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
    
    def fetch_article_data(self, url):
        try:
            # Make HTTP request
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            title = self.extract_title(soup)
            content = self.extract_content(soup)
            source = self.extract_source_domain(url)
            
            return {
                'title': title,
                'content': content,
                'source': source,
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
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
