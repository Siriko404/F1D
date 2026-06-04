import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber

PDF = "campello_etal_2022_brexit_jfqa.pdf"
PAGE = 22

with pdfplumber.open(PDF) as pdf:
    p = pdf.pages[PAGE]
    chars = [(c["text"], c["x0"], c["x1"], round(c["top"],1), c["fontname"]) for c in p.chars]

# rows by top
def rows(cs, ytol=2.0):
    R = {}
    for t,x0,x1,top,fn in cs:
        k = next((k for k in R if abs(k-top)<=ytol), top)
        R.setdefault(k, []).append((t,x0,x1,fn))
    return {k: sorted(v,key=lambda z:z[1]) for k,v in sorted(R.items())}

R = rows(chars)

# 1) RAW inspection: what does pdfplumber give for the POST coefficient row?
print("=== RAW pdfplumber chars in POST row region (top 243-247) ===")
for k,rc in R.items():
    if 243<=k<=247:
        print(f"top={k}: ", "".join(t for t,_,_,_ in rc))
        # show fontnames of non-alnum glyphs
        for t,x0,x1,fn in rc:
            if t.startswith("(cid:") or (len(t)==1 and not (t.isalnum() or t.isspace())):
                print(f"    glyph {t!r:10} font={fn} x0={round(x0,1)}")

# 2) distinct cid glyphs + fonts in the whole table band (243-365)
print("\n=== distinct (cid:) / special glyphs in table band, by font ===")
inv={}
for k,rc in R.items():
    if 243<=k<=365:
        for t,x0,x1,fn in rc:
            if t.startswith("(cid:") or (len(t)==1 and not (t.isalnum() or t.isspace())):
                inv[(t,fn)] = inv.get((t,fn),0)+1
for (t,fn),n in sorted(inv.items(), key=lambda z:-z[1]):
    print(f"  {t!r:10} {fn:34} x{n}")

# 3) column model from obs row + reconstruct POST row (with cid remap if needed)
def toks(rc, xgap=4.0):
    out,cur,lx=[],[],None
    for t,x0,x1,fn in rc:
        if lx is not None and (x0-lx)>xgap:
            out.append(("".join(z[0] for z in cur), cur[0][1], cur[-1][2])); cur=[]
        cur.append((t,x0,x1)); lx=x1
    if cur: out.append(("".join(z[0] for z in cur), cur[0][1], cur[-1][2]))
    return out

CID_MAP = {"(cid:1)":"−","(cid:6)":"×"}  # candidate; will confirm from raw
def remap(s):
    for k,v in CID_MAP.items(): s=s.replace(k,v)
    return s

obs=[t for t in (next((toks(rc) for k,rc in R.items() if "obs" in "".join(z[0] for z in rc).lower() and any(ch.isdigit() for z in rc for ch in z[0])), [])) if any(ch.isdigit() for ch in t[0])]
print("\nobs tokens:", [remap(t[0]) for t in obs])
col_right=[t[2] for t in obs]
def assign(x1): return min(range(len(col_right)), key=lambda i:abs(col_right[i]-x1))

print("\n=== reconstruct all coefficient rows (label by leading token), pdfplumber+cid-remap ===")
GT = {
 "POST":      ["−0.022","","","1.055","",""],
}
for k,rc in R.items():
    T=toks(rc)
    if not T: continue
    lead = remap(T[0][0])
    if not lead.startswith("POST"): continue
    cells=[""]*len(col_right)
    for txt,x0,x1 in T[1:]:
        rt = remap(txt)
        if any(ch.isdigit() for ch in rt):
            cells[assign(x1)] = rt
    if any(cells):
        print(f"top={k:6} {lead[:14]:14} | " + " | ".join(f"{c:>10}" for c in cells))
