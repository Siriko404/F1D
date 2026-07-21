# REV22 change log

REV22 is the presentation deck. It is REV21 with four wording defects corrected,
plus one dash in the PDF title that no check had been looking at, and nothing
else changed.

REV21 is untouched and remains the provenance record.

Deck to present:
`production/thesis_defense_main_deck_slides_01-13_rev22.pdf`

## 1. What changed

Six string replacements in the deck source HTML. The first five close the items
the audit left open as `D-OPEN-1`; the sixth is explained in section 4.

| ID | Slide | Was | Is |
|---|---|---|---|
| R22-01 | 8 | `Leverage, size, ... capex, dividends, ...` | `Leverage, ln(assets), ... capex, dividend indicator, ...` |
| R22-02 | 11 | `cash acquisitions rather than stock` | `cash acquisitions rather than stock acquisitions` |
| R22-03 | 12 | `around disclosure - no more, and no less` | `around disclosure, no more and no less` |
| R22-04 | 12 | `What it does not show - and where it may not carry` | `What it does not show, and where it may not carry` |
| R22-05 | 13 | `Unscripted CEO Q&A carries a ...` | `These patterns suggest that unscripted CEO Q&A carries a ...` |
| R22-06 | all | `<title>Thesis Defense — ... Slides 1–13` | `<title>Thesis Defense: ... Slides 1 to 13` |

### Why each one

**R22-01.** Slide 8 named two controls informally while slides 9 and 10 named
the same two variables formally. Appendix II of the thesis defines exactly one
control set, `lnAssets = ln(atq)` described as firm size and
`DivDummy = 1[dvy>0]` described as dividend payer. All three slides already
listed the same seven controls in the same order, so this was a labelling
inconsistency and not a difference in specification. Checking this first
mattered: had the three analyses genuinely used different controls, harmonising
the labels would have introduced an error into a deck that was otherwise
faithful.

**R22-02.** The sentence compared acquisitions with a payment method. It now
compares acquisitions with acquisitions. Slide 13 already used `cash deals` and
`stock deals`, so the deck was inconsistent with itself as well.

**R22-03 and R22-04.** The only two dash-based sentence constructions anywhere
in the deck. Both violated a standing instruction. Both are on slide 12.

**R22-05.** The thesis hedges; the deck asserted. `_conclusion_body.tex` line 7
reads *"Taken together, these patterns suggest that the unscripted language of
earnings calls carries a readable, anticipatory trace of a deal's passage from
private to public"*. The closing line now carries that hedge.

The headline was re-broken from two lines into three. The `.closing` box runs
from 1.87in to the recap grid at 3.75in at 0.56in per line, so three lines fit
and a fourth would overflow. The rendered slide confirms it.

### What did not change

No coefficient, standard error, p-value, confidence interval, event-stage label,
Wald contrast, chart point, citation, or page geometry. No CSS. No font. Slides
1 to 7, 9 and 10 are identical to REV21, span for span.

## 2. How REV22 was rendered

REV21 was produced by WeasyPrint 69.0. The ledger records the renderer as
`/home/oai/skills/pdfs/scripts/render_pdf.py`, so the original environment was
a Linux sandbox, not this machine.

Rendering locally was initially judged impossible, because importing WeasyPrint
fails here with `cannot load library 'libgobject-2.0-0'`, no GTK runtime is
installed, and WSL2 is disabled at the BIOS level. That judgement was wrong, and
the reason is worth recording.

**Since Python 3.8, Windows DLL resolution for ctypes and cffi ignores `PATH`.**
Putting a directory of GLib and Pango DLLs on `PATH` looks correct and does
nothing at all. `os.add_dll_directory()` is what works, and it must run before
`weasyprint` is imported.

Tesseract-OCR bundles the complete stack that WeasyPrint needs: `libgobject`,
`libglib`, `libpango`, `libpangoft2`, `libharfbuzz`, `libfreetype`,
`libfontconfig`, `libfribidi`, `libcairo`. Pointing `add_dll_directory` at
`C:\Program Files\Tesseract-OCR` is sufficient. See `render.py`.

Fontconfig prints `Cannot load default config file` on every run. It is
harmless here: every font in the deck is embedded in the HTML as a base64
`@font-face` data URI, so no system font is ever consulted. The control render
below proves this empirically rather than by argument.

Versions used: WeasyPrint 69.0, Pango 1.52.2, Python 3.13.5, Windows.

A GptWebCall exchange was prepared to have the ChatGPT sandbox render the deck
instead, on the assumption that local rendering was impossible. It was never
sent, and it was deleted once local rendering was shown to work, so that a later
session does not find a stale prepared call and fire it. Nothing about REV22
depends on a web call.

## 3. How REV22 was proved correct

Two separate questions, deliberately not merged. Both are re-runnable:

```
python docs/Defense/REV22/verify_rev22.py
```

### Question 1: is this rendering environment faithful?

`rev22_control.html` is a byte-identical copy of the REV21 source, sha256
`52b47bf58dfb491cc1d3cbe0be41c8b46e21b7b63648da183ba2e0461e39cc7b`, matching the
value recorded in REV21's own standardization audit. Rendering it here and
comparing against the locked REV21 PDF isolates the environment: any difference
is the renderer talking, not the edit.

Result: **all 13 slides, 538 text spans, maximum positional drift 0.0000 pt,
zero text mismatches.** The environment reproduces the locked deck exactly.

Note that the PDFs are not byte-identical, and successive renders of the same
input are not byte-identical to each other either. WeasyPrint output is not
bit-reproducible. Hash equality was therefore never the right test; span
geometry is.

### Question 2: did the edit do only what it was supposed to do?

The edited render is compared against the control render, all 13 slides, span
by span. Exactly slides 8, 11, 12 and 13 differ. Drawing counts are unchanged on
every slide, so no chart moved. Every span sits inside its page.

The four changed slides were then rasterised and inspected by eye. Clipped text
still extracts cleanly from a PDF, so no automated check can catch clipping;
only looking can. Nothing is clipped. Slide 11's second column grew from two
lines to three, which happens to balance it against the first column.

Full check list, all passing: REV21 unchanged, control page count and size,
13-slide span reproduction, edited page count and size, renders distinct, edit
scope, the approved strings landed, no em or en dash on any slide, no em or en
dash in the PDF metadata, containment. Seventeen in all.

## 4. R22-06, the dash the checks could not see

The four fixes above came from the audit. This sixth one came from noticing that
the check which said there were no dashes had never looked at the whole file.

The HTML `<title>` read `Thesis Defense — Standardized Main Deck, Slides 1–13`,
one em dash and one en dash. WeasyPrint copies `<title>` into the PDF's `/Title`,
so the shipped deck carried both in its metadata, visible in a viewer's title bar
and properties panel. It now reads
`Thesis Defense: Standardized Main Deck, Slides 1 to 13`.

The part worth remembering is why it survived. Both verifiers built their dash
scan from `page.get_text()`, which is rendered page text and nothing else. A
check named "no em dash or en dash anywhere" was passing while the deliverable
violated the rule, because metadata was never in its field of view. A green light
on an unexamined surface is worse than no check at all, since it actively
discourages looking.

`verify_rev22.py` now scans `document.metadata` as well, so the word "anywhere"
is true. This is also the reason the title was changed rather than filed as
accepted: the standing instruction is that no em dash appears in anything
audience-facing, and a PDF title is reachable by the audience.

The edit was made in `rev22_edited.html` only. `rev22_control.html` still carries
both dashes, because it must stay byte-identical to the REV21 source or it stops
being a fidelity control. The title is not page text, so the edit-scope check is
unaffected: exactly slides 8, 11, 12 and 13 still differ.

## 5. What REV22 does not address

The audit's single most important finding is not a deck defect and no wording
change can fix it. An examiner can ask what evidence there is that the CEO knew
about the acquisition at the pre-announcement call. The event clock is anchored
on the announcement date and the thesis observes neither the start of
negotiations nor the chief executive's knowledge. The only sound response is a
clean concession, prepared in advance. It belongs in the speaker notes and the
question preparation, not on a slide.
