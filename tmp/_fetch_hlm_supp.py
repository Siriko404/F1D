"""Fetch HLM (2008) supplementary data."""
import urllib.request, re

url = "https://publications.aaahq.org/accounting-review/article-abstract/83/6/1487/3028/The-Importance-of-Distinguishing-Errors-from?redirectedFrom=fulltext"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode("utf-8", errors="replace")

# Find link hrefs containing supplement terms
terms = ["supplement", "eSupplement", "Suppl", ".xlsx", ".xls", ".csv", ".zip", "Data_S", "doi.org/10.23", "doi/10.23", "Online_Append"]
for term in terms:
    pattern = re.compile(r'href[ ]*=[ ]*"([^"]*?%s[^"]*)"' % term, re.IGNORECASE)
    matches = pattern.findall(html)
    for m in matches:
        if not m.endswith(".css") and not m.endswith(".js"):
            print(f"[{term}]: {m}")

# Also look for "Supplementary Material" section in the HTML
print()
supp_div_match = re.search(r'<div[^>]*?supplementary.data[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
if supp_div_match:
    body = supp_div_match.group(1)
    hrefs = re.findall(r'href="([^"]*)"', body)
    print("Supplementary material div hrefs:")
    for h in hrefs:
        print(f"  {h}")
    if not hrefs:
        print(f"  (div body: {body[:500]})")
else:
    print("No supplementary-data div found.")
    # Look nearby
    near = re.search(r'.{0,500}supplementary.data.{0,500}', html, re.IGNORECASE | re.DOTALL)
    if near:
        print("Nearby context:", near.group()[:1000])
