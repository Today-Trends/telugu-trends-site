#!/usr/bin/env python3
# scripts/daily_trends_telugu.py
# pip install feedparser

import os, datetime, re, html
from pathlib import Path
import feedparser

FEEDS_FILE = "feeds.txt"
OUTPUT_DIR = "_posts"
MAX_ITEMS = 12

def read_feeds():
    if not os.path.exists(FEEDS_FILE):
        raise SystemExit("Create feeds.txt with RSS feed URLs (one per line).")
    with open(FEEDS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def sanitize_text(text, max_len=600):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)           # strip HTML
    text = re.sub(r"\s+", " ", text).strip()     # collapse whitespace
    if max_len and len(text) > max_len:
        return text[:max_len].rsplit(" ",1)[0] + "..."
    return text

def fetch_items(feeds):
    items = []
    for url in feeds:
        try:
            d = feedparser.parse(url)
        except Exception as e:
            print("feed parse error:", url, e)
            continue
        for e in d.entries:
            title = e.get("title","").strip()
            link = e.get("link","").strip()
            published = e.get("published","") or e.get("updated","")
            summary = e.get("summary","") or e.get("description","")
            items.append({
                "title": sanitize_text(title, 300),
                "link": link,
                "published": published,
                "summary": sanitize_text(summary, 400)
            })
    # dedupe by link
    seen = set()
    dedup = []
    for it in items:
        if not it["link"]: continue
        if it["link"] in seen: continue
        seen.add(it["link"])
        dedup.append(it)
    return dedup[:MAX_ITEMS]

def make_markdown(items):
    today_dt = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    title = f"Telugu Cinema — Daily Trends ({today_dt})"
    front = ("---\n"
             f"title: \"{title}\"\n"
             f"date: {today_dt}T00:00:00Z\n"
             "categories: [telugu, trends]\n"
             "layout: post\n"
             "---\n\n")
    body = f"# {title}\n\n_Automatically generated list of top Telugu cinema stories._\n\n"
    if not items:
        body += "No items found from configured feeds today.\n"
        return front + body
    for it in items:
        body += f"## [{it['title']}]({it['link']})\n\n"
        if it['summary']:
            body += f"{it['summary']}\n\n"
        body += f"Source: [{it['link']}]({it['link']})\n\n---\n\n"
    body += f"\n*Generated on {today_dt} UTC.*\n"
    return front + body

def write_post(content):
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    today_dt = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{today_dt}-telugu-daily-trends.md"
    path = Path(OUTPUT_DIR) / filename
    if path.exists():
        print("Post already exists:", path)
        return str(path)
    path.write_text(content, encoding="utf-8")
    print("Wrote:", path)
    return str(path)

def main():
    feeds = read_feeds()
    items = fetch_items(feeds)
    md = make_markdown(items)
    out = write_post(md)
    print("Done:", out)

if __name__ == "__main__":
    main()
