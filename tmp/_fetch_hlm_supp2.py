"""Fetch HLM supplementary via AAA API."""
import urllib.request, json, re

# Try multiple API patterns
urls = [
    "https://publications.aaahq.org/accounting-review/article/83/6/1487/3028/The-Importance-of-Distinguishing-Errors-from?resourceType=3",
    "https://meridian.allenpress.com/tar/article/83/6/1487",
    "https://publications.aaahq.org/Resource/Download?resourceId=3028&resourceType=3&isSupplement=true",
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        print(f"URL: {url}")
        print(f"Status: {resp.status}")
        print(f"Content-Type: {resp.headers.get('Content-Type','?')}")
        content = resp.read()
        if b'<html' not in content[:100].lower():
            print(f"Content preview: {content[:200]}")
        print()
    except Exception as e:
        print(f"URL: {url} -> ERROR: {e}")
        print()
