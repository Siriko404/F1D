import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf4llm, pymupdf, pdfplumber

PDF = "campello_etal_2022_brexit_jfqa.pdf"

# 1) pymupdf4llm full markdown
md = pymupdf4llm.to_markdown(PDF)
open("campello_pymupdf4llm_out.md","w",encoding="utf-8").write(md)
cid = len(re.findall(r"\(cid:\d+\)", md))
print("=== pymupdf4llm ===")
print("CHARS", len(md), "LINES", md.count("\n"), "CID_ARTIFACTS", cid)

# 2) locate Table 3 page (caption text)
doc = pymupdf.open(PDF)
t3page = None
for i in range(len(doc)):
    t = doc[i].get_text()
    if "reports output from equation (14)" in t:
        t3page = i
        break
print("Table3 page index (0-based):", t3page)

# minus-sign sanity: does pymupdf4llm preserve unicode minus / hyphen near coefficients?
seg = md[md.find("reports output from equation (14)"): md.find("reports output from equation (14)")+1800] if "reports output from equation (14)" in md else ""
print("--- pymupdf4llm Table3 region (first 1800 chars) ---")
print(seg)

# 3) pdfplumber structured table extraction on Table 3 page
print("\n=== pdfplumber extract_tables on Table 3 page ===")
with pdfplumber.open(PDF) as pdf:
    if t3page is not None:
        pg = pdf.pages[t3page]
        tbls = pg.extract_tables()
        print("num tables found by pdfplumber:", len(tbls))
        for ti,tb in enumerate(tbls):
            print(f"--- table {ti}: {len(tb)} rows ---")
            for row in tb[:18]:
                print(row)
