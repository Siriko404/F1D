import fitz
# Search paper + supp for DIVESTITURES definition
for path in [r"docs\papers\campello_etal_2022_brexit_jfqa.pdf",
             r"docs\papers\campello_etal_2022_brexit_supplementary.pdf"]:
    print(f"==== {path} ====")
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        text = page.get_text()
        if "DIVESTITURES" in text or "divestiture" in text.lower() or "sppe" in text.lower() or "sale of property" in text.lower():
            for para in text.split("\n\n"):
                if "DIVESTITURES" in para or "divestiture" in para.lower() or "sppe" in para.lower():
                    print(f"--- p{i+1} ---")
                    print(para.strip()[:800])
                    print()
