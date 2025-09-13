
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import math
import os

# =======================
# CONFIG
# =======================
SCRAPE_SITES = {
    "Rappler": True,
    "Philstar": True,

    "Rappler_FactCheck": True,

    "Reuters": True,
    "AP": True,
    "AlJazeera": True,

    "PeoplesVoice": True,
    "NewsPunch": True
}

BALANCE_DATASET = True
PAGES_PER_SITE = 10
MAX_ARTICLES_PER_SITE = 2

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

def process_article(link, site, title, selectors, label):
    art = safe_request(link, f"{site} Article")
    if not art:
        return None, False

    s = BeautifulSoup(art.text, "html.parser")
    text_parts = []
    seen_paras = set()

    # Multiple selectors 
    for sel in selectors + [
        "article p", "main p", "div[itemprop='articleBody'] p",
        "div[class*='article'] p", "div[class*='content'] p", "section p", "p"
    ]:
        ps = s.select(sel)
        if ps:
            for p in ps:
                txt = p.get_text(strip=True)
                if not txt:
                    continue
                # Unique Only(Preserves Order)
                if txt not in seen_paras:
                    text_parts.append(txt)
                    seen_paras.add(txt)

    text = " ".join(text_parts)

    if len(text) < 200:
        print(f"❌ {site}: No usable content for {title[:60]}")
        return None, False

    h = title + text[:50]
    if h in existing_hashes:
        print("⚠️ Skipped (already exists)")
        return None, True

    print(f"📝 Collected: {title[:60]}")
    existing_hashes.add(h)
    return {"Title": title, "Text": text, "Label": label}, False

def limit_articles(articles):
    return articles[:MAX_ARTICLES_PER_SITE]

def scrape_generic(base_url, site, link_selectors, content_selectors, label, pages=1, prefix=""):
    articles = []
    skip_count = 0
    for page in range(1, pages + 1):
        url = base_url.format(page=page) if "{page}" in base_url else base_url
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
                if prefix and href.startswith("/"):
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
            title = a.get_text(strip=True)
            record, skipped = process_article(link, site, title, content_selectors, label)
            # NextPage
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
        w = csv.DictWriter(f, fieldnames=["Title", "Text", "Label"])
        if mode == "w":
            w.writeheader()
        w.writerows(data)

save_csv("news_dataset.csv", dataset, mode="a" if os.path.exists("news_dataset.csv") else "w")
#save_csv("train_dataset.csv", train, mode="w")
#save_csv("test_dataset.csv", test, mode="w")

print(f"✅ Total={len(dataset)}")
#| Train={len(train)} | Test={len(test)}