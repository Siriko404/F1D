"""Append the 2 logit-table pages to rob_ALL.pdf (no recompile of the existing 6 tables).
Reads the BACKUP of the original + the new logit pages; writes the merged PDF to BOTH
the F1D path (where Sina opens it) and the fork path (Phase-3 deliverable)."""
from pathlib import Path
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfReader, PdfWriter

FORK = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3")
F1D  = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
ORIG  = FORK / "tmp" / "rob_ALL_BEFORE.pdf"          # backup of the original (6 tables)
LOGIT = FORK / "tmp" / "logit_tables_final.pdf"      # the 2 new tables
TARGETS = [F1D / "docs" / "Thesis" / "rob_ALL.pdf", FORK / "docs" / "Thesis" / "rob_ALL.pdf"]

n_orig = len(PdfReader(str(ORIG)).pages)
n_logit = len(PdfReader(str(LOGIT)).pages)
w = PdfWriter()
for f in (ORIG, LOGIT):
    for pg in PdfReader(str(f)).pages:
        w.add_page(pg)
import io
buf = io.BytesIO(); w.write(buf); data = buf.getvalue()
for t in TARGETS:
    try:
        t.write_bytes(data)
        print(f"wrote {t}  ({n_orig}+{n_logit} = {n_orig+n_logit} pages)")
    except PermissionError:
        print(f"LOCKED (close it in your PDF viewer, then re-run): {t}")
