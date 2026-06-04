# PDF → MD/JSON Extraction Tooling — Evaluation for the Replication Package

**Date:** 2026-06-02
**Test file:** `campello_etal_2022_brexit_jfqa.pdf` (JFQA Vol. 57 No. 8, pp. 3178–3222; 13 tables, regression output with coefficients/SE/significance stars, subscripted Greek β_UK)
**Environment:** Windows 11, Python 3.13.5, NVIDIA RTX 3050 Ti Laptop (4 GB VRAM, CUDA driver present)

---

## 1. Verdict on MarkItDown (the tool originally asked about)

**Not accurate enough for a replication package.** Prose (title, authors, abstract, body, footnotes, table captions) extracts correctly. **Table numeric data does not.**

Proven on this PDF (primary evidence, programmatic counts — not transcription):

| Failure | Count | Meaning |
|---|---|---|
| `(cid:1)` unmapped glyph | 188 | = the **minus sign**. Every negative coefficient + every "10‑K" corrupted |
| `(cid:6)` unmapped | 74 | = the **× interaction operator** (`POST(cid:6)βUK` = `POST × βUK`) |
| other `(cid:N)` | 86 | further lost symbols |
| orphaned subscript `i` lines | 393 | `β_UK` subscript scattered to stray lines |
| 10,244 output lines (vs ~992 for pymupdf4llm) | — | heavy fragmentation |

Worse than the glyph loss: **column de-interleaving**. In Table 1 all row labels are dumped in one block, then all numbers in a separate block — the row→value mapping is destroyed. In Table 3 the coefficient `0.361***` and its SE `(0.026)` survive but cannot be reliably tied to the right column (R&D vs DIVESTITURES) or row.

---

## 2. Root cause (proven, applies to ANY tool choice)

The PDF's embedded font has a **broken/missing ToUnicode CMap** for `−` (minus) and `×` (interaction). Confirmed across three independent text-layer extractors:

| Tool | Backend | Minus sign comes out as | Tables |
|---|---|---|---|
| MarkItDown | pdfminer.six | `(cid:1)` | de-interleaved, destroyed |
| pdfplumber (ruled-line strategy) | pdfminer.six | n/a | **0 tables found** (borderless three-line table) |
| pdfplumber (text strategy) | pdfminer.six | `(cid:1)` | shredded grid + rotated-margin junk mixed in |
| pymupdf4llm | MuPDF | `�` (U+FFFD, 224×) | real `\|` pipe tables, messy grid |

**Two distinct failure modes — they matter for the fix:**
- pdfminer-based tools (markitdown, pdfplumber) emit **distinct, deterministic** codes: `(cid:1)`→`−`, `(cid:6)`→`×`. These are **recoverable by find/replace, zero ML.**
- pymupdf4llm collapses every unmapped glyph to the **same** `U+FFFD` → **lossy, unrecoverable** (you can't tell a lost `−` from a lost anything-else).

So the glyph problem alone is *not* what forces OCR. The real blocker is **table structure**: text extractors de-interleave the borderless multi-column regression tables, and no find/replace fixes that. To get cells mapped correctly you need a tool with a **trained table-structure / layout model**, and to be safe against the broken font you want one that **rasterizes the page** (reads glyph shapes) rather than trusting the lying text layer.

---

## 3. Tool landscape (OSS, 2024–2026) — filtered to this machine

Benchmarks: **OmniDocBench v1.6/1.7** (CVPR 2025; *built by OpenDataLab = MinerU's own team* — self-grading caveat) and **olmOCR-Bench** (AllenAI, independent).

| Tool | License | Win + Py3.13 | Rasterizes? (beats broken font) | Table cell JSON | Math→LaTeX | OmniDocBench Table TEDS | Fits 4 GB GPU? |
|---|---|---|---|---|---|---|---|
| **MinerU** | Apache-ish (permissive ≥v3.1) | yes (3.10–3.13) | yes (OCR+VLM) | HTML | ✅ best (UniMERNet) | 87.9 (VLM) | pipeline yes; VLM tight |
| **Marker** | **GPL-3.0** | yes (CPU/GPU) | **yes, always (Surya OCR)** | flat MD; cell-JSON needs LLM | ✅ `$$`; `use_llm`→0.907 FinTabNet | 65.8 | yes |
| **Docling** | **MIT** | yes, first-class | **partial — defaults to text layer; must FORCE OCR** | ✅ **only one w/ row/col idx** (TableFormer) | ❌ weak | (below MinerU) | yes (CPU fine) |
| **Surya** | Apache-2.0 | yes | yes | ✅ row/col | ❌ | 83.3 (olmOCR-Bench) | yes |
| olmOCR | Apache-2.0 | **no (Linux+≥12 GB GPU)** | yes | ❌ | ✅ | 83.0 | **no (4 GB ≪ 12 GB)** |
| Nougat | MIT | **no (abandoned 2023, dep conflicts)** | yes | ❌ | ✅ but hallucinates/loops | dropped | — |
| pdfplumber | MIT | yes | **no** (CID problem) | ✅ simple grids only | ❌ | — | n/a |
| pymupdf4llm | **AGPL-3.0** | yes | **no** (U+FFFD, lossy) | ❌ | ❌ | — | n/a |
| GROBID | Apache-2.0 | Docker/Java | partial | ❌ (metadata only) | ❌ | — | n/a |
| Unstructured | Apache-2.0 | harder (poppler/libmagic) | hi_res only | partial | ❌ | — | yes |

Independent cross-check (olmOCR-Bench, *not* MinerU's benchmark): **Marker 76.1 overall edges MinerU 75.2** — so MinerU is not unambiguously #1; the two are close.

---

## 4. Recommendation for THIS replication pipeline

**Constraints that drive it:** Windows + Py3.13, 4 GB VRAM, borderless finance regression tables, broken font, need correct signs **and** correct row/col mapping, output to MD + JSON.

**Ruled out:** olmOCR (4 GB ≪ 12 GB, Linux-only), Nougat (abandoned), pure text extractors (markitdown/pdfplumber/pymupdf4llm — can't beat the broken font + de-interleaving).

**Recommended stack:**
1. **Marker** — primary extractor. Always rasterizes (bypasses the broken font for free), good math LaTeX, installs cleanly on Windows/Py3.13 (Surya backend, CPU or your 4 GB GPU). *License: GPL-3.0 — fine for a publicly-shared open replication package; a blocker only if the pipeline must stay closed-source.*
2. **Docling** — secondary, for the **structured cell-grid JSON** (`start_row_offset_idx`/`start_col_offset_idx` per cell — the only OSS tool that emits this natively), and clean MIT license. **Must be run in forced-OCR mode** on this file, or it will trust the broken text layer and reproduce the `�`/cid garbage.
3. **MinerU** — best benchmark table+formula quality and emits reading-order JSON, *but* pipeline mode pulls **detectron2**, which is genuinely painful to install on Windows + Py3.13. Worth it if Marker/Docling tables aren't clean enough; try last.

**Avoid as a "fix":** pymupdf4llm + find/replace — the U+FFFD collapse is lossy, you cannot recover the minus signs.

## 5. Replication reality (headline, not footnote)

**No OSS tool ships trustworthy coefficients unverified.** OCR/VLM fixes the broken glyph but introduces *transcription* risk — a misread digit or VLM hallucination lands on exactly the coefficient you care about. Every benchmark above tops out well short of cell-perfect, and *none* test the finance-regression-table format specifically. **Plan: tool gets you ~90%; eyeball every extracted number against the source PDF.** For a replication package that human check is the deliverable, not optional polish.

---

## Appendix — scratch artifacts in this directory
- `campello_markitdown_out.md` — MarkItDown output (the corrupted one)
- `campello_pymupdf4llm_out.md` — pymupdf4llm output (0 cid, U+FFFD minus, pipe tables)
- `_extract_test.py`, `_diag2.py` — test scripts
