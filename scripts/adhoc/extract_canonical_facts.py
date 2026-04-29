"""
Phase 1.5 — Empirical Audit
Extract canonical facts from all suite_specs needed for v6 thesis rewrite.
Output: docs/Draft/CANONICAL_FACT_SHEET.md
Locked memory framings to be cross-checked against this output.
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path('outputs/econometric')

SUITES = {
  'H1.ceo2.decomp':         ('h1_cash_holdings_ceo2iv_decomp',      'HC Full method (3-IV decomp)'),
  'H1.ceo2.decomp.qtrexp':  ('h1_cash_holdings_ceo2iv_decomp_qtrexp','HC QtrExp method (within-tenure expanding)'),
  'H1.2.ceo2.decomp':       ('h1_2_cash_constraint_ceo2iv_decomp',  'HFC Full method (3-IV decomp + Unrated interaction)'),
  'H1.2.ceo2.decomp.qtrexp':('h1_2_cash_constraint_ceo2iv_decomp_qtrexp','HFC QtrExp method'),
  'H1.3.cfvol':             ('h1_3_cfvol_moderation',               'CFvol moderator (Han-Qiu 2007)'),
  'H11':                    ('h11_prisk_uncertainty',               'PRisk driver (Hassan 2020)'),
  'H11-Lag':                ('h11_prisk_uncertainty_lag',           'PRisk lagged driver'),
  'H23':                    ('h23_competition_uncertainty',         'TSIMM competition driver (Hoberg-Phillips)'),
  'H24':                    ('h24_us_epu',                          'US EPU driver (BBD 2016)'),
  'H24b':                   ('h24b_global_epu',                     'Global EPU driver (Davis 2016)'),
  'H14c.ceo2.decomp':       ('h14c_spread_bgt_level_ceo2iv_decomp', 'Bid-ask spread 25-day post-call (3-IV decomp)'),
  'H18.ceo2.decomp':        ('h18_cccl_received_ceo2iv_decomp',     'SEC comment letter receipt (3-IV decomp)'),
  'H.death.did':            ('ceo_death_did_cash',                  'CEO sudden-death DiD (Phase E)'),
  'H.dwz.fd':               ('h_dwz_fd_cash',                       'DWZ §6 first-difference (turnover replication)'),
  'H.lewbel.iv':            ('h_lewbel_iv_cash',                    'Lewbel 2012 heteroskedasticity-based IV'),
}

def latest_spec(dir_name):
    d = BASE / dir_name
    if not d.exists():
        return None
    specs = sorted(d.rglob('suite_spec_*.json'))
    return specs[-1] if specs else None

def summarize_iv(d, iv_key):
    """Return sig counts + beta range + min p for one IV across columns."""
    sig = {'p10':0, 'p05':0, 'p01':0}
    betas, ps = [], []
    n_cols = 0
    for c in d.get('columns', []):
        ivd = c.get('coefs', {}).get(iv_key)
        if ivd is None: continue
        p = ivd.get('p_one')
        b = ivd.get('beta')
        if p is None: continue
        n_cols += 1
        betas.append(b); ps.append(p)
        if p < 0.10: sig['p10'] += 1
        if p < 0.05: sig['p05'] += 1
        if p < 0.01: sig['p01'] += 1
    if n_cols == 0:
        return None
    return {
        'n_cols': n_cols,
        'sig_p10': sig['p10'], 'sig_p05': sig['p05'], 'sig_p01': sig['p01'],
        'beta_min': min(betas), 'beta_max': max(betas),
        'p_min': min(ps), 'p_max': max(ps),
    }

def iv_row(name, label, iv_key, summary):
    if summary is None:
        return f'| `{iv_key}` | {label} | NO DATA |'
    s = summary
    return (f'| `{iv_key}` | {label} | '
            f'{s["sig_p10"]}/{s["n_cols"]}@.10 | '
            f'{s["sig_p05"]}/{s["n_cols"]}@.05 | '
            f'{s["sig_p01"]}/{s["n_cols"]}@.01 | '
            f'{s["beta_min"]:+.4f} to {s["beta_max"]:+.4f} | '
            f'{s["p_min"]:.4f} |')

OUT = ['# CANONICAL FACT SHEET — v6 thesis rewrite empirical audit',
       '', f'Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} via `scripts/adhoc/extract_canonical_facts.py`.',
       '',
       'All numbers programmatically extracted from latest `suite_spec_*.json`.',
       'AUTHORITY: this file. NOT memory docs. Memory locks are LLM-written and may contain hallucinated counts.',
       '',
       '## Suite spec source files', '']

for suite_id, (dir_name, _label) in SUITES.items():
    p = latest_spec(dir_name)
    if p is None:
        OUT.append(f'- **{suite_id}**: NO SPEC FOUND')
    else:
        OUT.append(f'- **{suite_id}**: `{p.relative_to("outputs/econometric")}`')

OUT.append('')

for suite_id, (dir_name, descr) in SUITES.items():
    p = latest_spec(dir_name)
    if p is None: continue
    with open(p) as f:
        d = json.load(f)
    OUT.append(f'## {suite_id} — {descr}')
    OUT.append('')
    n_cols_total = len(d.get('columns', []))
    ns = [c.get('n_obs', 0) for c in d.get('columns', []) if c.get('n_obs') is not None]
    if ns:
        OUT.append(f'**Cols**: {n_cols_total}  |  **n range**: {min(ns):,} to {max(ns):,}')
    OUT.append('')
    OUT.append('| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |')
    OUT.append('|---|---|---|---|---|---|---|')
    for iv in d.get('ivs', []):
        ivkey = iv['name']; lbl = iv.get('label', '')
        OUT.append(iv_row(suite_id, lbl, ivkey, summarize_iv(d, ivkey)))
    OUT.append('')
    # Per-column sample-size detail
    OUT.append('**Per-column n + DV + FE**:')
    OUT.append('')
    OUT.append('| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |')
    OUT.append('|---|---|---|---|---|---|---|')
    for c in d.get('columns', []):
        OUT.append(f'| {c.get("col","?")} | {c.get("dv","?")[:12]} | {c.get("fe_entity","?")[:9]} | {c.get("fe_time","?")[:9]} | {c.get("n_obs","?"):,} | {c.get("n_firms","?")} | {c.get("r2","?")} |')
    OUT.append('')
    OUT.append('---')
    OUT.append('')

out_path = Path('docs/Draft/CANONICAL_FACT_SHEET.md')
out_path.write_text('\n'.join(OUT), encoding='utf-8')
print(f'WROTE: {out_path}')
print(f'Suites audited: {len(SUITES)}')
