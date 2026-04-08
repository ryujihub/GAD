"""
scrape_news.py — Facebook Page Scraper Module for GAD News (mbasic version)

Scrapes the latest posts from the MGADO Facebook page using the lightweight mobile basic interface,
uploads images to ImgBB, and saves the results to data/news.json.
"""

import time
import random
import json
import hashlib
import os
import requests
import concurrent.futures
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Set
from playwright.sync_api import sync_playwright, Route

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FACEBOOK_PAGE_URL = "https://mbasic.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_PAGES = 5

# Resolve paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "news.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_flush(msg: str) -> None:
    print(msg, flush=True)

def random_delay(min_seconds: float = 2.0, max_seconds: float = 4.0) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))

def generate_caption_hash(caption: str) -> str:
    return hashlib.md5(caption.strip().encode("utf-8")).hexdigest()[:8]

def normalize_fb_date(raw: str) -> str:
    now = datetime.now()
    t = raw.strip().lower()
    if not t: return now.strftime("%B %d, %Y")
    if t in ("just now", "today"): return now.strftime("%B %d, %Y")
    if t == "yesterday": return (now - timedelta(days=1)).strftime("%B %d, %Y")
    m = re.match(r"^(\d+)\s*d", t)
    if m: return (now - timedelta(days=int(m.group(1)))).strftime("%B %d, %Y")
    return raw.strip()

def load_existing_news() -> Dict[str, Dict[str, Any]]:
    try:
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
            return {item["id"]: item for item in items if "id" in item}
    except Exception: pass
    return {}

def upload_to_imgbb(image_url: str, api_key: str) -> str:
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": api_key, "image": image_url, "expiration": 604800}
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["data"]["url"]
    except Exception as e:
        print_flush(f"   -> [ImgBB Error]: {e}")
    return ""

def ensure_playwright_browsers() -> None:
    import sys, subprocess
    if os.environ.get("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD") == "1": return
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception: pass

# ---------------------------------------------------------------------------
# Main Scraper
# ---------------------------------------------------------------------------
def scrape_facebook_page(url: str, imgbb_api_key: str, target_count: int = 7, max_pages: int = 5, existing: Dict[str, Any] = None):
    ensure_playwright_browsers()
    posts_data = []
    seen_ids = set()
    if existing is None: existing = {}

    with sync_playwright() as p:
        try:
            print_flush("[STATUS] Launching Lightweight Browser (mbasic)...")
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"]
            )
            context = browser.new_context(viewport={"width": 400, "height": 800})
            page = context.new_page()

            # Heavy resource blocking
            page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

            print_flush(f"[ACTION] Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Initial wait for any slow elements
            page.wait_for_timeout(3000)

            # DIAGNOSTIC: Check what containers are available
            print_flush("[DIAGNOSTIC] Checking for post containers...")
            containers = page.locator('div#m_group_stories_container, div#root, article, div[role="article"]').all()
            print_flush(f"[DIAGNOSTIC] Found {len(containers)} potential root containers.")

            pages_crawled = 0
            while len(posts_data) < target_count and pages_crawled < max_pages:
                print_flush(f"[STATUS] Crawling Page {pages_crawled+1}...")
                
                # Robust mbasic post selectors
                # 1. Look for articles
                # 2. Look for divs with data-ft (standard FB mobile metadata)
                # 3. Look for divs inside root that look like segments
                articles = page.locator('article, div[role="article"], div[data-ft], div#root > div > div > div > div')
                count = articles.count()
                print_flush(f"   -> Found {count} post candidates.")

                for i in range(count):
                    if len(posts_data) >= target_count: break
                    
                    article = articles.nth(i)
                    try:
                        # Only consider elements with significant text to avoid empty spacer divs
                        text_content = article.inner_text().strip()
                        if len(text_content) < 40: continue
                        
                        caption = text_content
                        post_id = generate_caption_hash(caption)
                        if post_id in seen_ids: continue
                        seen_ids.add(post_id)

                        if post_id in existing:
                            print_flush(f"   -> [CACHED] {post_id}")
                            posts_data.append(existing[post_id])
                            continue

                        # Extract first image only for speed/stability
                        photo_url = ""
                        img_el = article.locator("img").first
                        if img_el.count() > 0:
                            src = img_el.get_attribute("src") or ""
                            if src and "emoji.php" not in src:
                                clean_img = upload_to_imgbb(src, imgbb_api_key)
                                if clean_img:
                                    photo_url = f"https://wsrv.nl/?url={clean_img}&maxage=1y"

                        posts_data.append({
                            "id": post_id,
                            "caption": caption,
                            "photos": [photo_url] if photo_url else [],
                            "scraped_at": datetime.now().isoformat()
                        })
                        print_flush(f"   -> [SUCCESS] Acquired post {len(posts_data)}")
                    except Exception as e:
                        print_flush(f"   -> [WARN] Node error: {e}")

                # Pagination
                next_link = page.locator('a:has-text("Show more"), a:has-text("See more")').last
                if next_link.count() > 0 and len(posts_data) < target_count:
                    next_url = next_link.get_attribute("href")
                    if next_url:
                        print_flush("[ACTION] Next page...")
                        page.goto(f"https://mbasic.facebook.com{next_url}" if next_url.startswith("/") else next_url)
                        pages_crawled += 1
                        random_delay()
                    else: break
                else: break

        finally:
            browser.close()
    return posts_data

def save_news(posts: List[Dict[str, Any]]):
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=4, ensure_ascii=False)
        print_flush(f"[SAVED] Total posts: {len(posts)}")
    except Exception as e:
        print_flush(f"[ERROR] Save failed: {e}")

if __name__ == "__main__":
    existing = load_existing_news()
    results = scrape_facebook_page(FACEBOOK_PAGE_URL, IMGBB_API_KEY, existing=existing)
    save_news(results)
