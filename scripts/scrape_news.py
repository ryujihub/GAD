"""
scrape_news.py — Facebook Scraper (Modern Touch Interface)
Targets m.facebook.com for stability and high-quality photo extraction.
"""

import time
import json
import hashlib
import os
import requests
import sys
from datetime import datetime
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

# Database Import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from database import supabase

# Config
FACEBOOK_PAGE_URL = "https://m.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_RUN_TIME = 240 # 4 minutes max

def print_flush(msg: str) -> None:
    print(msg, flush=True)

def generate_id(text: str) -> str:
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()[:12]

def upload_img(url: str, key: str) -> str:
    try:
        r = requests.post("https://api.imgbb.com/1/upload", data={"key": key, "image": url, "expiration": 604800}, timeout=10)
        if r.status_code == 200: return r.json()["data"]["url"]
    except: pass
    return ""

def scrape_facebook_page(url: str, imgbb_key: str, target: int = 7):
    posts = []
    seen = set()
    start_time = time.time()

    with sync_playwright() as p:
        print_flush("[STATUS] Launching Modern Mobile Scraper...")
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page(viewport={"width": 450, "height": 900})
        
        # Block heavy garbage
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["media", "font"] else r.continue_())

        print_flush(f"[ACTION] Opening {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(7000) # Give extra time for React
        
        # [DEBUG] TAKE SCREENSHOT TO SEE WHAT THE ROBOT SEES
        try:
            temp_path = "/tmp/debug_screen.png"
            page.screenshot(path=temp_path)
            screen_url = upload_img(temp_path, imgbb_key)
            if screen_url:
                print_flush(f"[DEBUG] Page Screenshot: {screen_url}")
        except Exception as e:
            print_flush(f"[DEBUG] Screenshot failed: {e}")

        # Close login popups
        try:
            page.click('div[role="button"]:has-text("Not Now"), div[role="button"]:has-text("Hindi muna"), i[class*="close"]', timeout=3000)
        except: pass

        while len(posts) < target and (time.time() - start_time) < MAX_RUN_TIME:
            # Broad selectors for Facebook Touch/Mobile
            articles = page.locator('div[data-sigil*="story"], div[data-sigil*="m-feed-story"], article, div[id^="u_0_"], div._5pcr').all()
            print_flush(f"[STATUS] Analyzing {len(articles)} nodes...")

            for art in articles:
                if len(posts) >= target: break
                try:
                    # Get caption
                    caption = art.inner_text().strip()
                    if len(caption) < 25: continue
                    
                    pid = generate_id(caption)
                    if pid in seen: continue
                    seen.add(pid)

                    # Extract Image
                    img_src = ""
                    img_el = art.locator('img').first
                    if img_el.count() > 0:
                        src = img_el.get_attribute("src") or ""
                        if "static" not in src and "emoji" not in src:
                            img_src = upload_img(src, imgbb_key)
                    
                    new_post = {
                        "id": pid,
                        "title": caption.split('\n')[0][:80],
                        "content": caption,
                        "date": datetime.now().strftime("%B %d, %Y"),
                        "image": img_src,
                        "photos": [img_src] if img_src else [],
                        "post_url": url, # Fallback to page URL
                        "scraped_at": datetime.now().isoformat()
                    }

                    # Push to DB
                    try:
                        supabase.table('news').upsert(new_post).execute()
                        posts.append(new_post)
                        print_flush(f"   -> [DB SYNC] Post {len(posts)}: {new_post['title']}")
                    except Exception as e:
                        if "photos" in str(e):
                            new_post.pop("photos", None)
                            supabase.table('news').upsert(new_post).execute()
                            posts.append(new_post)
                            print_flush(f"   -> [DB SYNC] Post {len(posts)} (No Gallery)")
                except: continue

            # Scroll and wait for React to render more
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(2000)

        browser.close()
    return posts

if __name__ == "__main__":
    scrape_facebook_page(FACEBOOK_PAGE_URL, IMGBB_API_KEY)
    print_flush("[FINISHED] News cycle complete.")
