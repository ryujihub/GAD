"""
scrape_news.py — Facebook Page Scraper with Supabase Persistence
"""

import time
import random
import json
import hashlib
import os
import requests
import sys
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Set
from playwright.sync_api import sync_playwright, Route

# ---------------------------------------------------------------------------
# Configuration & Database
# ---------------------------------------------------------------------------
# Add project root to path for database import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from database import supabase

FACEBOOK_PAGE_URL = "https://www.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_SCROLLS = 18

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_flush(msg: str) -> None:
    print(msg, flush=True)

def generate_caption_hash(caption: str) -> str:
    return hashlib.md5(caption.strip().encode("utf-8")).hexdigest()[:12]

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
def scrape_facebook_page(url: str, imgbb_api_key: str, target_count: int = 7, max_scrolls: int = 18):
    posts_data = []
    seen_ids = set()

    with sync_playwright() as p:
        try:
            print_flush("[STATUS] Launching Scraper (Supabase Mode)...")
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"]
            )
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # Extreme Blocking for RAM
            page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())

            print_flush(f"[ACTION] Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            scroll_count = 0
            while len(posts_data) < target_count and scroll_count < max_scrolls:
                print_flush(f"[STATUS] Scan {scroll_count+1}/{max_scrolls} - Found {len(posts_data)}/{target_count}")
                
                articles = page.locator('div[role="article"]')
                count = articles.count()
                
                for i in range(count):
                    if len(posts_data) >= target_count: break
                    
                    article = articles.nth(i)
                    try:
                        msg_el = article.locator('div[data-ad-preview="message"]').first
                        caption = msg_el.inner_text().strip() if msg_el.count() > 0 else ""
                        if not caption or len(caption) < 20: continue
                        
                        post_id = generate_caption_hash(caption)
                        if post_id in seen_ids: continue
                        seen_ids.add(post_id)

                        # Extract post URL & photos
                        post_url = ""
                        try:
                            link = article.locator('a[href*="/posts/"], a[href*="pfbid"], a[href*="/permalink/"]').first
                            if link.count() > 0:
                                href = link.get_attribute("href") or ""
                                post_url = f"https://www.facebook.com{href.split('?')[0]}" if href.startswith("/") else href.split('?')[0]
                        except: pass

                        processed_photos = []
                        imgs = article.locator("img").all()
                        for img in imgs:
                            src = img.get_attribute("src") or ""
                            if "rsrc.php" in src or "emoji.php" in src: continue
                            
                            clean_img = upload_to_imgbb(src, imgbb_api_key)
                            if clean_img:
                                processed_photos.append(f"https://wsrv.nl/?url={clean_img}&maxage=1y")
                                if len(processed_photos) >= 3: break # Limit gallery size

                        new_post = {
                            "id": post_id,
                            "title": caption.split('\n')[0][:100],
                            "content": caption,
                            "date": datetime.now().strftime("%B %d, %Y"),
                            "image": processed_photos[0] if processed_photos else "",
                            "post_url": post_url,
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        # Add 'photos' only if the scraper found them
                        if processed_photos:
                            new_post["photos"] = processed_photos

                        # UPSERT TO SUPABASE
                        try:
                            # Try a test fetch to see if 'photos' exists or if we should use 'image' only
                            supabase.table('news').upsert(new_post).execute()
                            print_flush(f"   -> [DB SUCCESS] Post {post_id} synced.")
                            posts_data.append(new_post)
                        except Exception as db_err:
                            # Fallback: If 'photos' column is missing, try without it
                            if "photos" in str(db_err):
                                print_flush("   -> [DB RECOVERY] 'photos' column missing, retrying with 'image' only.")
                                new_post.pop("photos", None)
                                supabase.table('news').upsert(new_post).execute()
                                posts_data.append(new_post)
                            else:
                                print_flush(f"   -> [DB ERROR] {db_err}")

                    except Exception: pass

                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(3500)
                scroll_count += 1

        finally:
            browser.close()
    return posts_data

if __name__ == "__main__":
    scrape_facebook_page(FACEBOOK_PAGE_URL, IMGBB_API_KEY)
    print_flush("[COMPLETE] All new posts synced to Supabase.")
