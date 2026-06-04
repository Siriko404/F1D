"""Grep paper for verbatim β^UK construction. Pages 13-20, fn 27."""
import fitz
p = fitz.open(r"docs/papers/campello_etal_2022_brexit_jfqa.pdf")
hits = []
for i, page in enumerate(p):
    txt = page.get_text()
    lows = txt.lower()
    if any(k in lows for k in ["beta", "β^uk", "vftse", "vol(", "eq. (", "equation (", "stock returns", "footnote 27", "fn. 27"]):
        hits.append((i+1, txt))
for pg, txt in hits[:15]:
    print(f"\n===== PAGE {pg} =====")
    print(txt[:3500])
