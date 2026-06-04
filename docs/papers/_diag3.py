import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf, pdfplumber

PDF = "campello_etal_2022_brexit_jfqa.pdf"
PAGE = 22  # Table 3

# --- A) PyMuPDF rawdict: what does the minus-sign char carry? unicode + glyph id ---
doc = pymupdf.open(PDF)
pg = doc[PAGE]
raw = pg.get_text("rawdict")
print("=== PyMuPDF rawdict: chars near a coefficient (looking for U+FFFD / minus) ===")
hits = 0
for b in raw["blocks"]:
    if b.get("type", 0) != 0:
        continue
    for l in b["lines"]:
        for s in l["spans"]:
            for ch in s["chars"]:
                c = ch["c"]
                if ord(c) == 0xFFFD or c in "−-−":
                    print(f"char={c!r} cp={hex(ord(c))} font={s['font']!r} glyph_origin={tuple(round(v,1) for v in ch['origin'])}")
                    hits += 1
                    if hits >= 8:
                        break
            if hits >= 8: break
        if hits >= 8: break
    if hits >= 8: break

# does the span dict expose a glyph id? print keys once
print("\nspan keys:", list(raw["blocks"][0]["lines"][0]["spans"][0].keys()))
print("char keys:", list(raw["blocks"][0]["lines"][0]["spans"][0]["chars"][0].keys()))

# --- B) pdfplumber: the broken char's text + fontname; is the cid deterministic & font-tagged? ---
print("\n=== pdfplumber chars: cid/broken glyphs on Table 3 page ===")
with pdfplumber.open(PDF) as pdf:
    p = pdf.pages[PAGE]
    seen = {}
    for ch in p.chars:
        t = ch["text"]
        if t.startswith("(cid:") or (len(t)==1 and ord(t)==0xFFFD):
            key = (t, ch["fontname"])
            seen[key] = seen.get(key, 0) + 1
    for (t, fn), n in sorted(seen.items(), key=lambda x:-x[1])[:12]:
        print(f"text={t!r:14} font={fn!r:32} count={n}")

    # --- C) coordinate separation: can x-position split columns in one coefficient row? ---
    print("\n=== one numeric row: chars with x-coords (column separability) ===")
    # find chars on the line containing first '0.022' style coeff; just dump a y-band
    rows = {}
    for ch in p.chars:
        top = round(ch["top"])
        rows.setdefault(top, []).append(ch)
    # pick a y-band that has many numeric chars
    cand = sorted(rows.items(), key=lambda kv: -sum(c["text"].isdigit() or c["text"]=="." for c in kv[1]))
    top, chars = cand[0]
    chars.sort(key=lambda c: c["x0"])
    line = "".join(c["text"] for c in chars)
    xs = [(round(c["x0"],1), c["text"]) for c in chars]
    print("y-band top=", top, "text=", line[:120])
    print("x0 of each char:", xs[:40])
