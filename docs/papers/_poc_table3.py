import sys, io, json, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

PDF = "campello_etal_2022_brexit_jfqa.pdf"
PAGE = 22

def extract_chars(page):
    """Deterministic: every glyph -> (unicode, x0, y_baseline, font). No ML."""
    out = []
    raw = page.get_text("rawdict")
    for b in raw["blocks"]:
        if b.get("type", 0) != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                for ch in s["chars"]:
                    ox, oy = ch["origin"]
                    out.append((ch["c"], round(ox, 2), round(oy, 2), s["font"]))
    return out

def cluster_rows(chars, ytol=2.5):
    rows = {}
    for c, x, y, f in chars:
        key = None
        for k in rows:
            if abs(k - y) <= ytol:
                key = k; break
        rows.setdefault(key if key is not None else y, []).append((c, x, y, f))
    return [sorted(v, key=lambda t: t[1]) for _, v in sorted(rows.items(), key=lambda kv: kv[0])]

def split_cells(rowchars, xgap=8.0):
    cells, cur, lastx = [], [], None
    for c, x, y, f in rowchars:
        if lastx is not None and (x - lastx) > xgap:
            cells.append("".join(cur)); cur = []
        cur.append(c); lastx = x
    if cur: cells.append("".join(cur))
    return cells

doc = pymupdf.open(PDF)
pg = doc[PAGE]

# 1) glyph inventory of special (non-alnum) chars in the table band -> the map to audit+freeze
chars = extract_chars(pg)
band = [t for t in chars if 350 <= t[2] <= 520]   # coefficient region (y baseline)
inv = {}
for c, x, y, f in band:
    if not (c.isalnum() or c.isspace()):
        inv[(c, hex(ord(c)), f)] = inv.get((c, hex(ord(c)), f), 0) + 1
print("=== special-glyph inventory in coefficient band (char, codepoint, font, count) ===")
for k, n in sorted(inv.items(), key=lambda x: -x[1]):
    print(f"  {k[0]!r:6} {k[1]:8} {k[2]:18} x{n}")

# 2) reconstruct rows in the band
print("\n=== reconstructed coefficient rows (label | cells...) ===")
for rc in cluster_rows(band):
    cells = split_cells(rc)
    txt = " | ".join(cells)
    if any(ch.isdigit() for ch in txt):
        print(" ", txt[:140])

# 3) DETERMINISM proof: run twice, hash the JSON
def run():
    return [split_cells(rc) for rc in cluster_rows(extract_chars(doc[PAGE]))]
h1 = hashlib.sha256(json.dumps(run(), ensure_ascii=False).encode()).hexdigest()
h2 = hashlib.sha256(json.dumps(run(), ensure_ascii=False).encode()).hexdigest()
print("\n=== determinism check ===")
print("run1 sha256:", h1[:24])
print("run2 sha256:", h2[:24])
print("IDENTICAL:", h1 == h2)
