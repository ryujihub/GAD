"""
scrape_news.py — Facebook Page Scraper Module for GAD News (Desktop version - RAM Optimized)
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
FACEBOOK_PAGE_URL = "https://www.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_SCROLLS = 15

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "news.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_flush(msg: str) -> None:
    print(msg, flush=True)

def generate_caption_hash(caption: str) -> str:
    return hashlib.md5(caption.strip().encode("utf-8")).hexdigest()[:8]

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
    except Exception: pass
    return ""

# ---------------------------------------------------------------------------
# Core Scraper
# ---------------------------------------------------------------------------
def scrape_facebook_page(url: str, imgbb_api_key: str, target_count: int = 7, max_scrolls: int = 15, existing: Dict[str, Any] = None):
    posts_data = []
    seen_ids = set()
    if existing is None: existing = {}

    with sync_playwright() as p:
        try:
            print_flush("[STATUS] Launching Optimized Desktop Browser...")
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer"]
            )
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # EXTREME BLOCKING (Block CSS, Fonts, Images to save RAM)
            def block_heavy(route: Route):
                if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                    route.abort()
                else:
                    route.continue_()
            page.route("**/*", block_heavy)

            print_flush(f"[ACTION] Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            # Scroll and extract
            scroll_count = 0
            while len(posts_data) < target_count and scroll_count < max_scrolls:
                print_flush(f"[STATUS] Analyzing posts (Scroll {scroll_count+1})...")
                
                # Modern Facebook post selector
                articles = page.locator('div[role="article"]')
                count = articles.count()
                
                for i in range(count):
                    if len(posts_data) >= target_count: break
                    
                    article = articles.nth(i)
                    try:
                        # Extract text
                        msg_el = article.locator('div[data-ad-preview="message"]').first
                        caption = msg_el.inner_text().strip() if msg_el.count() > 0 else ""
                        if not caption: continue
                        
                        post_id = generate_caption_hash(caption)
                        if post_id in seen_ids: continue
                        seen_ids.add(post_id)

                        if post_id in existing:
                            print_flush(f"   -> [CACHED] {post_id}")
                            posts_data.append(existing[post_id])
                            continue

                        # Extract first relevant image link (even if blocked, the src exists in DOM)
                        photo_url = ""
                        imgs = article.locator("img").all()
                        for img in imgs:
                            src = img.get_attribute("src") or ""
                            # Ignore tracking/small icons
                            if "rsrc.php" in src or "emoji.php" in src: continue
                            
                            # Clean and upload fallback
                            clean_img = upload_to_imgbb(src, imgbb_api_key)
                            if clean_img:
                                photo_url = f"https://wsrv.nl/?url={clean_img}&maxage=1y"
                                break

                        posts_data.append({
                            "id": post_id,
                            "caption": caption,
                            "photos": [photo_url] if photo_url else [],
                            "scraped_at": datetime.now().isoformat()
                        })
                        print_flush(f"   -> [SUCCESS] Acquired post {len(posts_data)}")
                    except Exception: pass

                # Scroll down
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(3000)
                scroll_count += 1

        finally:
            browser.close()
    return posts_data

def save_news(posts: List[Dict[str, Any]]):
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=4, ensure_ascii=False)
        print_flush(f"[SAVED] Total: {len(posts)}")
    except Exception: pass

if __name__ == "__main__":
    existing = load_existing_news()
    results = scrape_facebook_page(FACEBOOK_PAGE_URL, IMGBB_API_KEY, existing=existing)
    save_news(results)
