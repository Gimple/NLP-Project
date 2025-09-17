import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import math
import os
from playwright.sync_api import sync_playwright

# =======================
# CONFIG
# =======================
SCRAPE_SITES = {
    "Rappler": True,
    "Philstar": True,
    "GMA": True,
    "Inquirer": True,

    "Rappler_FactCheck": True,

    "Reuters": True,
    "AP": True,
    "AlJazeera": True,

    "PeoplesVoice": True,
    "NewsPunch": True,
    "TheOnion": True,
    "ClickHole": True
}

PLAYWRIGHT_AVAILABLE = True
BALANCE_DATASET = True
PAGES_PER_SITE = 2
MAX_ARTICLES_PER_SITE = 1

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:118.0) Gecko/20100101 Firefox/118.0"
]

# =======================
# SESSION
# =======================
SESSION = requests.Session()

# Playwright
playwright_browser = None
def get_playwright_browser():
    global playwright_browser
    if PLAYWRIGHT_AVAILABLE and playwright_browser is None:
        try:
            playwright = sync_playwright().start()
            playwright_browser = playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        except Exception as e:
            print(f"⚠️ Failed to initialize Playwright: {e}")
            return None
    return playwright_browser
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    SESSION.mount("http://", adapter)
    SESSION.mount("https://", adapter)
except Exception:
    pass

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "DNT": "1",
}

# =======================
# UTILITIES
# =======================
existing_hashes = set()
if os.path.exists("news_dataset.csv"):
    with open("news_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            h = row["Title"] + row["Text"][:50]
            existing_hashes.add(h)

def safe_request(url, site_name, log=True):
    time.sleep(random.uniform(1.5, 3.0))
    headers = {**BASE_HEADERS, "User-Agent": random.choice(USER_AGENTS)}
    if log:
        print(f"🌐[{site_name}] {url}")
    try:
        resp = SESSION.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            print(f"⚠️ {site_name} HTTP {resp.status_code}")
            return None
        return resp
    except Exception as e:
        print(f"⚠️ {site_name} error: {e}")
        return None

def scrape(url, selectors, site_name, wait_for_selector=None, extract_text=True):
    if not PLAYWRIGHT_AVAILABLE:
        return None
        
    browser = get_playwright_browser()
    if not browser:
        return None
        
    context = None
    page = None
    
    try:
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            extra_http_headers=BASE_HEADERS
        )
        page = context.new_page()

        print(f"🌐 [Playwright] Loading: {url}")
        page.goto(url, timeout=60000, wait_until='domcontentloaded')
        
        time.sleep(3)
        
        if wait_for_selector:
            try:
                print(f"⏳ [Playwright] Waiting for selector: {wait_for_selector}")
                page.wait_for_selector(wait_for_selector, timeout=10000)
            except Exception as e:
                print(f"⚠️ [Playwright] Selector {wait_for_selector} not found: {e}")
        
        time.sleep(2)
        
        if not extract_text:
            content = page.content()
            return content
        
        content = page.content()
        s = BeautifulSoup(content, "html.parser")
        text_parts = []
        seen_paras = set()
        
        for sel in selectors + [
            "article p", "main p", "div[itemprop='articleBody'] p",
            "div[class*='article'] p", "div[class*='content'] p", 
            "section p", "div.post-content p", "div.entry-content p",
            "p"
        ]:
            try:
                elements = s.select(sel)
                if elements:
                    for elem in elements:
                        txt = elem.get_text(strip=True)
                        if txt and txt not in seen_paras:
                            text_parts.append(txt)
                            seen_paras.add(txt)
            except Exception as e:
                print(f"⚠️ [Playwright] Selector error {sel}: {e}")
        
        text = " ".join(text_parts)
        print(f"✅ [Playwright] {site_name}: Extracted {len(text)} chars")
        return text if len(text) >= 100 else None
            
    except Exception as e:
        print(f"⚠️ [Playwright] Error for {site_name}: {e}")
        return None
        
    finally:
        try:
            if page:
                page.close()
            if context:
                context.close()
        except Exception as e:
            print(f"⚠️ [Playwright] Error during cleanup: {e}")

def process_article(link, site, title, selectors, label, source, **kwargs):
    global existing_hashes
    print(f"🌐 {site}: {title[:60]}...")
    
    use_playwright = kwargs.get('use_playwright', False)
    wait_for_selector = kwargs.get('wait_for_selector', None)
    
    if use_playwright and PLAYWRIGHT_AVAILABLE:
        print(f"  🚀 Using Playwright for article content...")
        text = scrape(
            url=link,
            selectors=selectors,
            site_name=site,
            wait_for_selector=wait_for_selector,
            extract_text=True
        )
        
        if not text:
            print(f"❌ {site}: Failed to extract content with Playwright")
            return None, False
            
        soup = BeautifulSoup("<html><body><p>" + text + "</p></body></html>", 'html.parser')
    else:
        resp = safe_request(link, site, log=False)
        if not resp:
            return None, True
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        initial_text = soup.get_text(strip=True)
        if len(initial_text) < 200 and PLAYWRIGHT_AVAILABLE:
            print(f"  🔄 Falling back to Playwright for better content extraction...")
            text = scrape(
                url=link,
                selectors=selectors,
                site_name=site,
                wait_for_selector=wait_for_selector,
                extract_text=True
            )
            if text:
                soup = BeautifulSoup("<html><body><p>" + text + "</p></body></html>", 'html.parser')
    
    text = ""
    seen_paras = set()
    text_parts = []
    
    for sel in selectors:
        elements = soup.select(sel)
        if elements:
            for e in elements:
                txt = e.get_text(strip=True)
                if txt and txt not in seen_paras:
                    text_parts.append(txt)
                    seen_paras.add(txt)
            if text_parts:
                break
    
    text = " ".join(text_parts)

    if len(text) < 200 and PLAYWRIGHT_AVAILABLE:
        print(f"🔄 {site}: BeautifulSoup failed, trying Playwright...")
        playwright_text = scrape(link, selectors, site)
        if playwright_text:
            text = playwright_text
        else:
            print(f"❌ {site}: Both BeautifulSoup and Playwright failed for {title[:60]}")
            return None, False
    elif len(text) < 200:
        print(f"❌ {site}: No usable content for {title[:60]}")
        return None, False

    h = title + text[:50]
    if h in existing_hashes:
        print("⚠️ Skipped (already exists)")
        return None, True

    print(f"📝 Collected: {title[:60]}")
    existing_hashes.add(h)
    return {"Title": title, "Text": text, "Label": label, "Source": source}, False

def limit_articles(articles):
    return articles[:MAX_ARTICLES_PER_SITE]

def scrape_generic(base_url, site, link_selectors, content_selectors, label, pages=1, prefix="", **kwargs):
    articles = []
    skip_count = 0
    use_playwright = kwargs.get('use_playwright', False)
    wait_for_selector = kwargs.get('wait_for_selector', None)
    
    for page in range(1, pages + 1):
        url = base_url.format(page=page) if "{page}" in base_url else base_url
        
        if use_playwright and PLAYWRIGHT_AVAILABLE:
            print(f"🚀 Using Playwright for {site}...")
            html_content = scrape(url, wait_for_selector, site)
            if not html_content:
                continue
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            resp = safe_request(url, site, log=False)
            if not resp:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

        links = []
        seen_hrefs = set()
        # Loop through multiple link selectors and Dedupe (HREF)
        for sel in link_selectors:
            for a in soup.select(sel):
                href = a.get("href", "")
                if not href:
                    continue
                # Normalize relative links
                if prefix and href.startswith("/") and not href.startswith("//"):
                    href_norm = prefix + href
                elif href.startswith("http"):
                    href_norm = href
                elif prefix:
                    href_norm = prefix + href
                else:
                    href_norm = href

                if href_norm in seen_hrefs:
                    continue
                seen_hrefs.add(href_norm)
                links.append((a, href_norm))

        for a, link in links:
            if len(articles) >= MAX_ARTICLES_PER_SITE:
                break
            site_config = SITES_CONFIG.get(site, {})
            
            use_playwright_for_article = (use_playwright or site_config.get('use_playwright', False)) and PLAYWRIGHT_AVAILABLE
            wait_selector = site_config.get('wait_for_selector')

            title = a.get_text(strip=True)
            if not title:
                title = f"Untitled Article from {site}"

            record, skipped = process_article(
                link=link, 
                site=site, 
                title=title, 
                selectors=content_selectors, 
                label=label, 
                source=site,
                use_playwright=use_playwright_for_article,
                wait_for_selector=wait_selector
            )
            if skipped:
                skip_count += 1
                if skip_count >= 10:
                    print(f"⏭️ {site}: reached 10 consecutive skips, moving to next page")
                    break
                continue

            skip_count = 0
            if record:
                articles.append(record)

    print(f"✅ {site}: {len(articles)}")
    return limit_articles(articles)

# =======================
# SITE CONFIG
# =======================
SITES_CONFIG = {
    # --- PHILIPPINES REAL ---
    "Rappler": {
        "url": "https://www.rappler.com/section/nation/page/{page}",
        "link_sel": ["h3 a", "h2 a"],
        "content_sel": ["article p", "div.c-article__body p", "div.article__content p"],
        "label": "Real",
        "prefix": "https://www.rappler.com"
    },
    "Philstar": {
        "url": "https://www.philstar.com/headlines?page={page}",
        "link_sel": ["h2 a", "h3 a"],
        "content_sel": ["article p", "div.article__content p", "div.c-article__body p"],
        "label": "Real",
        "prefix": "https://www.philstar.com"
    },
    "GMA": {
        "url": "https://www.gmanetwork.com/news/",
        "link_sel": ["h3 a", "h2 a", ".story-title a", "a[href*='/news/']"],
        "content_sel": ["article p", "div.article-content p", "div.story-content p", ".story-body p"],
        "label": "Real",
        "prefix": "https://www.gmanetwork.com"
    },
    "Inquirer": {
        "url": "https://www.inquirer.net/",
        "link_sel": ["h3 a", "h2 a", ".entry-title a", "a[href*='/news/']", "a[href*='/globalnation/']"],
        "content_sel": ["article p", "div.article-content p", ".entry-content p", ".story-body p", "div[itemprop='articleBody'] p"],
        "label": "Real",
        "prefix": "https://www.inquirer.net",
        "use_playwright": True,
        "wait_for_selector": "article"
    },

    # --- FACT-CHECK ---
    "Rappler_FactCheck": {
        "url": "https://www.rappler.com/section/fact-check/page/{page}",
        "link_sel": ["h3 a", "h2 a"],
        "content_sel": ["article p", "div.c-article__body p", "div.article__content p"],
        "label": "Fake",
        "prefix": "https://www.rappler.com"
    },

    # --- INTERNATIONAL REAL ---
    "Reuters": {
        "url": "https://www.reuters.com/world/?page={page}",
        "link_sel": ["a[data-testid='Heading']", "h3 a"],
        "content_sel": ["p[data-testid='paragraph']", "article p"],
        "label": "Real",
        "prefix": "https://www.reuters.com"
    },
    "AP": {
        "url": "https://apnews.com/",
        "link_sel": ["a[data-key='card-headline']", "h3 a"],
        "content_sel": ["div.Article p", "article p"],
        "label": "Real",
        "prefix": "https://apnews.com"
    },
    "AlJazeera": {
        "url": "https://www.aljazeera.com/news/",
        "link_sel": ["a.u-clickable-card__link", "h3 a"],
        "content_sel": ["div.wysiwyg p", "article p"],
        "label": "Real",
        "prefix": "https://www.aljazeera.com"
    },

    # --- INTERNATIONAL FAKE ---
    "PeoplesVoice": {
        "url": "https://thepeoplesvoice.tv/page/{page}",
        "link_sel": ["h3.entry-title a"],
        "content_sel": ["div.td-post-content p", "article p"],
        "label": "Fake",
        "prefix": ""
    },
    "NewsPunch": {
        "url": "https://newspunch.com/",
        "link_sel": ["h3.entry-title a"],
        "content_sel": ["div.td-post-content p", "article p"],
        "label": "Fake",
        "prefix": ""
    },
    "TheOnion": {
        "url": "https://www.theonion.com/latest",
        "link_sel": ["article a[data-ga-item='headline']", "h2 a", "h3 a"],
        "content_sel": ["div.duet--article--article-body-component p", "article p"],
        "label": "Fake",
        "prefix": "https://www.theonion.com"
    },
    "ClickHole": {
        "url": "https://www.clickhole.com/latest/",
        "link_sel": ["a[data-ga-item='headline']", "h2 a", "h3 a", "h4 a", "article a"],
        "content_sel": ["div.duet--article--article-body-component p", "article p", ".post-content p", "div[class*='content'] p", "div[class*='body'] p"],
        "label": "Fake",
        "prefix": "https://www.clickhole.com",
        "use_playwright": True,
        "wait_for_selector": "article"
    }
}

# =======================
# RUN SCRAPERS
# =======================
dataset = []
for site, conf in SITES_CONFIG.items():
    if SCRAPE_SITES.get(site):
        dataset.extend(scrape_generic(conf["url"], site, conf["link_sel"], conf["content_sel"], conf["label"], pages=PAGES_PER_SITE, prefix=conf["prefix"]))

# Shuffle + Save
real = [a for a in dataset if a["Label"] == "Real"]
fake = [a for a in dataset if a["Label"] == "Fake"]

if BALANCE_DATASET and real and fake:
    n = min(len(real), len(fake))
    dataset = real[:n] + fake[:n]
else:
    dataset = real + fake

random.shuffle(dataset)
split = math.floor(len(dataset) * 0.8)
train, test = dataset[:split], dataset[split:]

def save_csv(fname, data, mode="w"):
    with open(fname, mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Title", "Text", "Label", "Source"])
        if mode == "w":
            w.writeheader()
        w.writerows(data)

save_csv("news_dataset.csv", dataset, mode="a" if os.path.exists("news_dataset.csv") else "w")
#save_csv("train_dataset.csv", train, mode="w")
#save_csv("test_dataset.csv", test, mode="w")

# Cleanup
if playwright_browser:
    try:
        playwright_browser.close()
    except:
        pass

print(f"✅ Total={len(dataset)}")
#| Train={len(train)} | Test={len(test)}