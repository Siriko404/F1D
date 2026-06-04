import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

PDF = "campello_etal_2022_brexit_jfqa.pdf"
PAGE = 22
GLYPH_FIX = {"\x01": "−", "\x06": "×"}  # frozen audited map for font AdvP4C4E74

def chars(page):
    out = []
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type", 0) != 0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for ch in s["chars"]:
                    c = GLYPH_FIX.get(ch["c"], ch["c"])
                    x0, y0, x1, y1 = ch["bbox"]
                    out.append((c, x0, x1, round(ch["origin"][1], 1)))
    return out

def rows(cs, ytol=2.0):
    R = {}
    for c, x0, x1, y in cs:
        k = next((k for k in R if abs(k - y) <= ytol), y)
        R.setdefault(k, []).append((c, x0, x1))
    return {k: sorted(v, key=lambda t: t[1]) for k, v in sorted(R.items())}

def tokens(rowchars, xgap=4.0):
    toks, cur, lx = [], [], None
    for c, x0, x1 in rowchars:
        if lx is not None and (x0 - lx) > xgap:
            toks.append(("".join(t[0] for t in cur), cur[0][1], cur[-1][2])); cur = []
        cur.append((c, x0, x1)); lx = x1
    if cur: toks.append(("".join(t[0] for t in cur), cur[0][1], cur[-1][2]))
    return toks  # (text, x0, x1)

doc = pymupdf.open(PDF)
R = rows(chars(doc[PAGE]))

# 1) find the "obs" row -> build 6-column model from its right edges (numbers are right-aligned)
obs_y = None
for y, rc in R.items():
    line = "".join(c for c, _, _ in rc)
    if "ofobs" in line.replace(" ", ""):
        obs_y = y; break
obs_toks = [t for t in tokens(R[obs_y]) if any(ch.isdigit() for ch in t[0])]
col_right = [t[2] for t in obs_toks]      # right edges = column anchors (right-aligned numbers)
print("obs row tokens:", [t[0] for t in obs_toks])
print("column right-edges:", [round(x,1) for x in col_right])

def assign(tok_x1):
    # nearest column by right edge (right-aligned numbers)
    return min(range(len(col_right)), key=lambda i: abs(col_right[i] - tok_x1))

def reconstruct(label_substr):
    """find row whose leading label matches, map its numeric tokens to the 6 columns."""
    for y, rc in R.items():
        toks = tokens(rc)
        if not toks: continue
        lead = toks[0][0]
        if label_substr in lead:
            cells = [""] * len(col_right)
            for txt, x0, x1 in toks[1:]:
                if any(ch.isdigit() for ch in txt):
                    j = assign(x1)
                    cells[j] = (cells[j] + " " + txt).strip()
            return lead, cells, y
    return None

print("\n=== ALL table rows in y∈[235,365], column-anchored ===")
for y, rc in R.items():
    if not (235 <= y <= 365): continue
    toks = tokens(rc)
    if not toks: continue
    label = toks[0][0]
    cells = [""] * len(col_right)
    has_num = False
    for txt, x0, x1 in toks[1:] if len(toks) > 1 else []:
        if any(ch.isdigit() for ch in txt) or txt.strip("()*.−-") == "":
            if any(ch.isdigit() for ch in txt):
                has_num = True
                j = assign(x1); cells[j] = (cells[j] + " " + txt).strip()
    if has_num:
        print(f"y={y:6} {label[:16]:16} | " + " | ".join(f"{c:>10}" for c in cells))
