# Deterministic, Auditable Paper → JSON Toolchain (OSS, componentized)

**Date:** 2026-06-02
**Goal:** Convert academic finance/economics journal PDFs into one auditable JSON document per paper — sections + paragraphs as fields, tables as structured cells (extremely accurate + deterministic), figures/images saved to disk with their paths stored in JSON. Whole paper captured.
**Constraints:** Windows 11, Python 3.13.5, NVIDIA RTX 3050 Ti (4 GB VRAM). Determinism + auditability paramount. Tools must be programmatic (Python API), community-battle-tested, primary-source-cited.
**Test file:** `campello_etal_2022_brexit_jfqa.pdf` (JFQA 2022, 13 regression tables, broken-font `−`/`×`).

> This document is the build-spec companion to `PDF_EXTRACTION_TOOL_EVALUATION.md` (which records *why markitdown and other single-shot tools fail*). Here we pick one battle-tested tool per pipeline stage.

---

## 0. The two cross-cutting decisions (everything depends on these)

### 0.1 Determinism is a spectrum — be honest about which parts are bit-reproducible

| Determinism class | Meaning | Pipeline stages that qualify |
|---|---|---|
| **Bit-reproducible** | pure rule/geometry, no ML; same input → identical bytes | triage, GROBID *fulltext* (CRF-only), table geometric reconstruction, figure raster dump, pdffigures2, schema/hashing |
| **Pinned-and-frozen** | neural; reproducible only with pinned weights+libs+hardware, NOT provably bit-identical; must be human-verified then frozen | math→LaTeX recognition (UniMERNet), *optional* Docling TableFormer cross-check |

**Rule for this project:** the deterministic core (text/tables/figures/triage) is bit-reproducible. Any neural step (only math recognition is unavoidable) goes through a **verify-once → freeze → hash** gate, and its output JSON carries `{model_sha, lib_versions, status: "verified"}`. No neural output is trusted unverified. This is auditable in the scientific sense even where it isn't bit-deterministic.

> **Bit-reproducible applies to the EXTRACTOR, not the verified artifact.** A human-verified-then-frozen table/equation is a separate ground-truth file; re-running the extractor reproduces the *extraction* hash, not the human edit. Track the two with distinct hashes (extractor output vs frozen ground-truth).

### 0.2 License map — prefer MIT/Apache/MPL/BSD; flag AGPL/GPL

| License | Tools | Implication for a replication package |
|---|---|---|
| MIT/Apache/BSD/MPL | pdfplumber, pdfminer.six, pikepdf(MPL), camelot, img2table, GROBID, pdffigures2, pypdfium2, docling/docling-core, pydantic, DVC, Snakemake, Luigi, UniMERNet | clean — use freely |
| **AGPL-3.0** | **PyMuPDF**, borb | fine for *internal/academic* use; if the package is **distributed as software/SaaS**, AGPL propagates to your code (Artifex sells a commercial license) |
| GPL-2.0/3.0 | Poppler (`pdffonts`/`pdfimages`), marker, surya | GPL CLI called via subprocess is generally OK; GPL *Python imports* propagate |

**The live tradeoff:** PyMuPDF (AGPL) decodes the broken `−` correctly to `0x2d` and is the most ergonomic engine; pdfplumber (MIT) emits `(cid:1)` and needs the frozen glyph map. → **If the package will be published/distributed, build on pdfplumber+remap; if internal-only, PyMuPDF is the better engine.** Decision pending (see end).

---

## 1. Stage 0 — File triage (classify before extracting)

Deterministically answer: digital-native vs scanned? which fonts lack `/ToUnicode` (the `(cid:N)`/broken-minus risk)? page count, encryption, image inventory? This gates routing and is the pre-flight detector for the exact failure that broke markitdown.

| Tool | Stars | License | Role | Det? | Win+Py3.13 |
|---|---|---|---|---|---|
| **pikepdf** | 2.6k | MPL-2.0 | **cause-level** `"/ToUnicode" in font_obj` (object traversal), encryption, linearization, page count | ✅ | ✅ pip wheels |
| **pdfplumber** | 10.4k | MIT | **symptom-level** `any("(cid:" in c["text"])`, font inventory, `page.images`, scanned heuristic | ✅ | ✅ pure-Py |
| Poppler `pdffonts` | — | GPL-2.0 | gold-standard `uni` yes/no column (optional subprocess cross-check) | ✅ | binary on PATH |

**Pick:** `pikepdf` + `pdfplumber`. (poppler `pdffonts` optional.)
Scanned heuristic (no library exposes a flag): per page `len(chars)==0 AND a full-page image ≥90% of MediaBox`.

---

## 2. Stage 1 — Text + section/paragraph structure

Split body into section hierarchy + per-paragraph fields with source coordinates.

| Tool | Stars | License | Det? | Section+para? | Coords? | Notes |
|---|---|---|---|---|---|---|
| **GROBID** (CRF default) | 4.9k | Apache-2.0 | ✅ **fully** (fulltext model is CRF-only — devs confirm "no neural model for the fulltext models") | ✅ `<div>/<head>/<p>/<note>` | ✅ `teiCoordinates=p,head,note` | server=Docker; `grobid-client-python` is Py3.13. Battle-tested: S2ORC / Semantic Scholar (81M papers) |
| pdfminer.six | 7.0k | MIT | ✅ | ❌ geometry only | ✅ per-char | deterministic coordinate **backstop** |
| PyMuPDF blocks | 9.9k | AGPL | ✅ | ❌ geometry only | ✅ block/span | fast backstop; AGPL |
| Docling | 60.9k | MIT | ⚠️ neural ("pinned") | ✅ full hierarchy | ✅ per-element prov | easiest, but neural layout |
| marker / Unstructured hi_res | 35.7k / 14.8k | GPL / Apache | ⚠️ neural | ✅ | ✅ | GPL / detectron2-on-Windows pain |

**Pick:** **GROBID (CRF)** for deterministic semantic sections/paragraphs + coordinates → the only tool that is *both* fully deterministic *and* gives semantic structure at battle scale. Pair with **pdfminer.six** as an MIT, pure-Python coordinate backstop to verify each paragraph's bbox.
⚠️ *Determinism ≠ accuracy:* GROBID's paragraph boundaries are deterministic, but boundary **correctness** on this journal's two-column layout is not yet spot-checked. Verify one page's `<p>` splits against the PDF before treating "each paragraph as a field" as settled.
Workflow: `processFulltextDocument` + `teiCoordinates=p,head,note` → parse TEI (`lxml`) → each `<p>` becomes `{id, section_id, text, coords{page,x0,y0,x1,y1}}`.

---

## 3. Stage 2 — Tables (the hard requirement: accurate AND deterministic)

PoC already proven on Table 3 of the test file: PyMuPDF `rawdict` gives correct glyphs + coordinates; geometric row/col clustering reconstructs cells; two runs → identical SHA-256. The research confirms **no off-the-shelf tool does all three of {deterministic, glyph-fix, semantic cells}** — a custom geometric reconstruction is required.

| Tool | Stars | License | Approach | Det? | Borderless? | explicit (row,col)? |
|---|---|---|---|---|---|---|
| **pdfplumber** (text strategy) | 10.4k | MIT | geometric/rule | ✅ | ✅ | positional + **exposes `page.chars` for glyph remap** |
| **PyMuPDF** find_tables / rawdict | 9.9k | AGPL | geometric/rule | ✅ | ✅ | positional; rawdict gives clean glyphs |
| camelot (stream/network) | 3.7k | MIT | geometric/rule | ✅ | ✅ | positional |
| img2table | 0.9k | MIT | OpenCV (raster) | ✅ on same raster | ✅ | **explicit row/col idx** (no neural) |
| Docling **TableFormer** | 60.9k | MIT | neural | ⚠️ pinned | ✅ | ✅ **`start/end_row/col_offset_idx` + spans** (richest) |
| gmft / TATR / deepdoctection | — | MIT/Apache | neural | ⚠️ | ✅ | varies |

**Pick:** **Custom geometric reconstruction** on **PyMuPDF `rawdict`** (or pdfplumber `page.chars` if MIT-only) char coordinates, using a **GLOBAL COLUMN MODEL** (critical — per-row gap clustering shifts values into wrong columns on empty cells; a global model assigns by x to fixed column anchors and preserves empties). Pipeline:
1. extract chars `(unicode, x0, x1, top, font)`;
2. apply **frozen, audited glyph map** (font `AdvP4C4E74`: `0x01→−`, `0x06→×`) — deterministic fix for residual broken glyphs;
3. derive column anchors from the densest row (e.g. obs/header right-edges); cluster top→rows;
4. assign each token to the nearest column anchor (empties stay empty);
5. domain post-process: pair stacked SE-line to the coefficient above, attach `***` stars, parse subscripts, fix `R²` superscript;
6. emit `{row_idx, col_idx, value, stars, se, bbox}`.

> **VERIFIED on the test file (Table 2, `_poc_colmodel.py`):** every coefficient placed in the correct column — diagonal structure (col1/4 → col2/5 → col3/6), all minus signs recovered, all `***`/`**` stars attached, **all empty cells preserved**, obs row exact. Determinism re-confirmed (identical SHA-256 across runs). This proves pure-geometric is *both accurate and bit-deterministic* on the hard regression-table case → it is the **primary** table path; the empty-cell column-shift risk is resolved by the global column model. Remaining work (SE-line pairing, `R²` superscript, multi-line labels) is deterministic post-processing, not an accuracy blocker.

**Optional neural cross-check (NOT primary):** Docling TableFormer; if its grid disagrees with the geometric grid, flag for human review. **Human verify-once-then-freeze gate** still applies to every table — but the extractor is now demonstrably high-accuracy, so the gate is *verification*, not heavy correction.

---

## 4. Stage 3 — Figures / images (save to disk, path in JSON)

| Tool | Stars | License | Role | Det? |
|---|---|---|---|---|
| **PyMuPDF** `get_images`/`extract_image` | 9.9k | AGPL | embedded raster dump (lossless) + `get_pixmap(clip=bbox)` to render vector-figure regions | ✅ |
| **pypdfium2** | 0.8k | BSD/Apache | permissive raster-dump alternative (avoids AGPL) | ✅ |
| `pdfimages` (poppler) | — | GPL-2.0 | batch lossless raster dump (subprocess) | ✅ |
| **pdffigures2** (AllenAI) | 0.7k | Apache-2.0 | **deterministic, rule-based figure-region + caption linking**; battle-tested at Semantic Scholar (1M+; 94%P/90%R) | ✅ |
| deepfigures / layoutparser / Docling-layout | — | various | neural; dead/Windows-hostile/non-det | ❌ reject |

**Pick:** **PyMuPDF** (or **pypdfium2** for permissive) for embedded rasters + region rendering; **pdffigures2** for robust caption→figure association (it *reasons about page structure*, beating a pure proximity heuristic). Coordinates align cleanly (both 72-DPI top-left). **Validate pdffigures2 recall on ~30 econ PDFs first** — it's CS-trained. 4 GB GPU **not needed** (all CPU).
Output per figure: `{figure_id, caption, page, bbox, file_path}`; render at 300 DPI to `figures/<paper>/fig_<n>.png`.

---

## 5. Stage 4 — Math / equations (honest determinism limits)

No neural math-OCR is bit-deterministic. Two-stage, determinism-respecting design:

| Tool | Stars | License | Role | Det? | 4GB? |
|---|---|---|---|---|---|
| **PyMuPDF coords** (rule) | — | AGPL | **deterministic numbered-equation detection**: text block matching `(\d+)` at x > 85% page width → equation band bbox | ✅ | ✅ |
| **UniMERNet** | 0.4k | Apache-2.0 | best OSS formula image→LaTeX (≈Mathpix/GPT-4o CDM); used in MinerU | ⚠️ pinned | ✅ ~2GB |
| pix2tex | 16k | MIT | older baseline | ⚠️ | ✅ |
| Nougat / texify / im2latex | — | MIT/CC | abandoned / archived / outdated — **skip** | — | Nougat needs 8GB+ |

**Pick:** deterministic numbered-equation **detection** (PyMuPDF coords) → crop → **UniMERNet** **recognition** (pinned weights, greedy decode) → **human verify-and-freeze** gate. ⚠️ **UniMERNet/MinerU need Python 3.12 on Windows** (the `ray` dep blocks 3.13) → isolate in a separate Py3.12 venv invoked as a subprocess; keep the main pipeline on 3.13. Store `{equation_id, page, bbox, latex, model_sha, status}`.

---

## 6. Stage 5 — Schema, assembly, validation, reproducibility, orchestration

| Concern | Pick | Stars | License | Why |
|---|---|---|---|---|
| Target schema/data-model | **docling-core `DoclingDocument`** | 2.8k | MIT | Pydantic-v2, **zero-ML** (`pip install docling-core` = schema only), per-element `prov.page_no+bbox` built in; extend with `figure.file_path`, `math`, table-cell `(row,col)` |
| Validation | **Pydantic v2** (+ jsonschema gate) | 27k | MIT | Rust-backed, Py3.13; `model_json_schema()` exports a published contract |
| Bit-repro output | **canonical JSON + SHA-256** | stdlib | — | round bbox floats to 6dp, `sort_keys=True`, tight separators → hash per doc = your determinism check (`rfc8785` only if external JCS needed) |
| Artifact lineage | **DVC** | 15.5k | Apache-2.0 | `dvc repro` hashes inputs+extractor versions → reproducible artifact chain |
| Pipeline runner | **Snakemake** (`snakemake-minimal` on Win) | 2.8k | MIT | content-hash DAG = only re-runs changed inputs; the reproducible-science standard (Luigi = fallback; Prefect/Dagster = overkill) |

papermage (AllenAI): borrow the layered-document *idea*, **don't depend** (stale, no Py3.13).

**The float landmine:** bbox floats are the deepest non-determinism source — round to fixed precision *before* serialization or hashes diverge across platforms.

---

## 7. Reference architecture (per paper)

```
raw/<paper>.pdf
   │
   ▼  Stage 0  triage          pikepdf + pdfplumber        → triage/<paper>.json   (fonts, cid-risk, scanned?, pages)
   ▼  Stage 1  text/structure  GROBID(CRF) + pdfminer.six  → text/<paper>.json     (sections[], paragraphs[]+coords)
   ▼  Stage 2  tables          PyMuPDF rawdict + glyph-map  → tables/<paper>.json   (cells[row,col,value,se,stars,bbox])  [HUMAN-VERIFY]
   ▼  Stage 3  figures         PyMuPDF + pdffigures2        → figures/<paper>/*.png + figures/<paper>.json (path+caption+bbox)
   ▼  Stage 4  math            PyMuPDF detect + UniMERNet   → math/<paper>.json     (latex, model_sha, status)  [HUMAN-VERIFY, Py3.12 subproc]
   ▼  Stage 5  assemble        docling-core schema + Pydantic → out/<paper>.json    (validated)
              + canonical-json + SHA-256 + DVC track
   orchestrated by Snakemake (content-hash DAG)
```

Determinism guarantee: Stages 0–3,5 are **bit-reproducible** (same PDF → same SHA-256). Stages 2 (table values) and 4 (math) carry a **human-verify-freeze** gate; their neural assists are pinned + hashed, never trusted unverified.

---

## 8. Open decisions (need your call)

1. **Engine license:** PyMuPDF (AGPL, best glyph decode) vs pdfplumber (MIT, needs frozen remap) — depends on whether this package is distributed or internal.
2. ~~**Tables:** pure-geometric vs neural~~ — **RESOLVED by verification**: pure custom-geometric + global column model is primary (accurate + bit-deterministic, proven on Table 2). Docling TableFormer = optional cross-check only.
3. **Figures:** add pdffigures2 (JVM dep, best caption-linking) vs pure-PyMuPDF proximity heuristic (no JVM).
4. **Math scope:** include equation→LaTeX now (adds Py3.12 subprocess + UniMERNet) or defer.

---

## Appendix — verified evidence used
- PoC `_poc_table3.py`: deterministic geometric Table-3 reconstruction; run1==run2 SHA-256; `No. of obs. | 43,025 | 17,199 | 21,253 | 9,143 | 3,540 | 4,173`; minus recovered as `0x2d`.
- `_diag3.py`: PyMuPDF rawdict decodes `−`=0x2d (font AdvTT5843c571); residual broken glyphs only `0x01`/`0x06` in font `AdvP4C4E74` (frozen-map fixable).
- Star counts / licenses / Py3.13 support: GitHub API + PyPI, 2026-06-02 (citations in research transcripts).
