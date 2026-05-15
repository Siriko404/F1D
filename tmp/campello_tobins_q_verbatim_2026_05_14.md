# Campello et al. 2022 JFQA — TOBIN_Q definition (verbatim)

**Source**: PDF programmatic extraction via `pdftotext -layout` per-page.
**Page**: PDF p.21 (journal p.3198), Table 1 footer.
**Extraction date**: 2026-05-14.
**Extractor**: pdftotext (Poppler 24.04 via MiKTeX) → `tmp/campello_pages/p21.txt`.
**Manipulation**: NONE.

---

## PDF p.21 (j.3198) — Table 1 variable-definition footer (verbatim)

> TOBIN_Q is defined as the market value of assets divided by the
> book value of assets, and is calculated as the market value of equity plus
> the book value of assets minus book value of equity plus deferred taxes,
> all divided by book value of assets.

---

## Literal enumeration

Numerator (verbatim): **market value of equity + book value of assets − book value of equity + deferred taxes**
Denominator (verbatim): **book value of assets**

Compustat-quarterly mapping (standard, undisputed):

| Term | Compustat |
|------|-----------|
| Market value of equity | `cshoq × prccq` |
| Book value of assets | `atq` |
| Book value of equity | `ceqq` |
| Deferred taxes | `txditcq` |

Resulting formula:

```
TOBIN_Q = (cshoq × prccq  +  atq  −  ceqq  +  txditcq) / atq
```

---

## F1D current implementation (cross-reference, NOT manipulation)

`src/f1d/shared/variables/brexit_tobins_q.py:72`:

```python
(atq + cshoq * prccq) / atq
```

Missing terms vs verbatim: `− ceqq + txditcq`.

---

## Source files

- PDF: `docs/papers/Campello_2022_Brexit_JFQA.pdf`
- Page extract: `tmp/campello_pages/p21.txt`
- Cross-references in main text:
  - p.20: "Firm-level controls include lagged stock returns, Tobin's Q, cash flow, logged assets, and sales growth"
  - p.23 fn 23: "These include Tobin's Q, Cash Flow, Sales Growth, Consensus Earnings Forecasts, and 1-year Stock Returns"
