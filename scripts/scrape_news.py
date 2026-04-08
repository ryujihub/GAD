"""
scrape_news.py — Bulletproof Universal Scraper
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

# Database Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
try:
    from database import supabase
except ImportError:
    supabase = None

# Config
FACEBOOK_PAGE_URL = "https://m.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_TIME = 240

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

def push_to_db(post_data: dict):
    """Recursively attempts to upsert by removing problematic columns."""
    if not supabase: return False
    
    current_data = post_data.copy()
    while True:
        try:
            supabase.table('news').upsert(current_data).execute()
            return True
        except Exception as e:
            err_str = str(e)
            # Find the column name in the error message
            # PostgREST errors usually say "Could not find the 'column' column"
            import re
            match = re.search(r"Could not find the '(.+?)' column", err_str)
            if match:
                col = match.group(1)
                print_flush(f"   -> [DB AUTO-FIX] Removing missing column '{col}'")
                current_data.pop(col, None)
                if not current_data: return False # Nothing left to push
            else:
                print_flush(f"   -> [DB ERROR] {err_str}")
                return False

def scrape_facebook_page(url: str, imgbb_key: str, target: int = 7):
    posts_data = []
    seen = set()
    start_time = time.time()

    with sync_playwright() as p:
        print_flush("[STATUS] Launching Universal Scraper...")
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        context = browser.new_context(viewport={"width": 450, "height": 900})
        page = context.new_page()
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["media", "font"] else r.continue_())

        print_flush(f"[ACTION] Navigating to {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(7000) 

        while len(posts_data) < target and (time.time() - start_time) < MAX_TIME:
            print_flush("[STATUS] Scanning for post content...")
            
            candidates = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('div, article, p'))
                    .filter(el => el.innerText && el.innerText.trim().length > 70 && el.children.length < 15)
                    .map(el => el.innerText.trim());
            }''')

            print_flush(f"   -> Found {len(candidates)} potential blocks.")

            for caption in candidates:
                if len(posts_data) >= target: break
                
                pid = generate_id(caption)
                if pid in seen: continue
                seen.add(pid)

                # Try to find an image
                img_src = ""
                try:
                    img_el = page.locator('img[src*="scontent"]').first
                    if img_el.count() > 0:
                        src = img_el.get_attribute("src") or ""
                        img_src = upload_img(src, imgbb_key)
                except: pass

                new_post = {
                    "id": pid,
                    "title": caption.split('\n')[0][:80],
                    "content": caption,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "image": img_src,
                    "post_url": url,
                    "scraped_at": datetime.now().isoformat()
                }

                if push_to_db(new_post):
                    posts_data.append(new_post)
                    print_flush(f"   -> [DB SYNCED] {new_post['title']}")

            print_flush("[ACTION] Scrolling...")
            page.evaluate("window.scrollBy(0, 1000)")
            page.wait_for_timeout(4000)

        browser.close()
    return posts_data

if __name__ == "__main__":
    scrape_facebook_page(FACEBOOK_PAGE_URL, IMGBB_API_KEY)
    print_flush("[COMPLETE] News update cycle finished.")
