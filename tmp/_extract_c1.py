"""Extract Table C1 from supplementary PDF."""
import fitz
doc = fitz.open("docs/papers/campello_etal_2022_brexit_supplementary.pdf")
for i, page in enumerate(doc):
    text = page.get_text()
    if "Table C1" in text or "Sample" in text or "Filters" in text or "2010" in text:
        print(f"=== PAGE {i+1} ===")
        # strip non-cp1252 chars for Windows console
        clean = text.encode("cp1252", errors="replace").decode("cp1252")
        print(clean[:3000])
