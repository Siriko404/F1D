import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf, pdfplumber

PDF = "campello_etal_2022_brexit_jfqa.pdf"
md = open("campello_pymupdf4llm_out.md",encoding="utf-8").read()

# codepoints of the suspect chars around a coefficient
i = md.find("0.077***")
ctx = md[i-3:i+9]
print("context around 0.077:", repr(ctx))
print("codepoints:", [hex(ord(c)) for c in ctx])

# count replacement-char artifacts
print("U+FFFD (replacement) count:", md.count("�"))

# pdfplumber with TEXT strategy on Table 3 page (22)
print("\n=== pdfplumber TEXT strategy, page 22 ===")
with pdfplumber.open(PDF) as pdf:
    pg = pdf.pages[22]
    ts = {"vertical_strategy":"text","horizontal_strategy":"text","snap_tolerance":4}
    tbls = pg.extract_tables(ts)
    print("tables found:", len(tbls))
    if tbls:
        for row in tbls[0][:14]:
            print([ (c[:18] if c else c) for c in row])
