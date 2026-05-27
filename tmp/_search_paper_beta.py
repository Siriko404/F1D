"""Search Campello paper + supplementary for β^UK estimation window/sample/freq."""
import fitz
import re

for path in [r"docs\papers\campello_etal_2022_brexit_jfqa.pdf",
             r"docs\papers\campello_etal_2022_brexit_supplementary.pdf"]:
    print(f"\n========================================")
    print(f"== {path}")
    print(f"========================================\n")
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        text = page.get_text()
        # Find paragraphs mentioning beta/VFTSE/vol/equation 13
        if any(kw in text.lower() for kw in [
            "vol(r", "vol(ftse", "beta^uk", "βuk", "βi", "equation (13)",
            "implied volatility", "30-day", "vftse",
        ]):
            # Extract relevant snippets — paragraphs containing keywords
            paras = text.split("\n\n")
            for para in paras:
                if any(kw in para.lower() for kw in [
                    "vol(r", "vol(ftse", "beta^uk", "equation (13)",
                    "implied vol", "30-day", "vftse", "daily ret",
                    "monthly", "estimation window", "rolling"
                ]):
                    if len(para.strip()) > 10:
                        print(f"--- p{i+1} ---")
                        print(para.strip()[:500])
                        print()
