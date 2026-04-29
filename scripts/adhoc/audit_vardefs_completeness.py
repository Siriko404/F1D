"""Audit variable_definitions.tex completeness vs latest thesis-body suite_specs.
Output: list of (a) IVs cited in body but missing from vardefs (CRITICAL),
        (b) variables in vardefs not cited in any body suite (STALE).
"""
import json
import re
from pathlib import Path

THESIS_SUITES = [
    'h1_cash_holdings_ceo2iv_decomp',
    'h1_cash_holdings_ceo2iv_decomp_qtrexp',
    'h1_2_cash_constraint_ceo2iv_decomp',
    'h1_2_cash_constraint_ceo2iv_decomp_qtrexp',
    'h1_3_cfvol_moderation',
    'h11_prisk_uncertainty',
    'h11_prisk_uncertainty_lag',
    'h23_competition_uncertainty',
    'h24_us_epu',
    'h24b_global_epu',
    'h14c_spread_bgt_level_ceo2iv_decomp',
    'h18_cccl_received_ceo2iv_decomp',
    'ceo_death_did_cash',
    'h_dwz_fd_cash',
    'h_lewbel_iv_cash',
]

BASE = Path('outputs/econometric')
all_ivs = set()
all_dvs = set()
all_controls = set()

for s in THESIS_SUITES:
    cands = sorted((BASE / s).rglob('suite_spec_*.json'))
    if not cands:
        print(f'WARN: no spec for {s}')
        continue
    j = json.loads(cands[-1].read_text())
    for iv in j.get('ivs', []):
        all_ivs.add(iv['name'])
    for c in j.get('columns', []):
        if c.get('dv'):
            all_dvs.add(c['dv'])
        for cf_name in c.get('coefs', {}).keys():
            all_ivs.add(cf_name)
    ctls = j.get('controls', [])
    if isinstance(ctls, dict): ctls = ctls.get('vars', [])
    for ctl in ctls:
        if isinstance(ctl, dict): all_controls.add(ctl.get('name', ctl.get('var', '')))
        elif isinstance(ctl, str): all_controls.add(ctl)

# Read current vardefs
vd = Path('docs/Draft/variable_definitions.tex').read_text(encoding='utf-8')
defined = set()
for m in re.finditer(r'^([A-Za-z][A-Za-z0-9_\\]*?)\s*&', vd, re.MULTILINE):
    defined.add(m.group(1).replace('\\_', '_').replace('\\', ''))

print('=== ALL IVs in 15 thesis suites ===')
for v in sorted(all_ivs):
    status = 'OK' if v in defined else 'MISSING'
    print(f'  {status}: {v}')
print()
print('=== ALL DVs in 15 thesis suites ===')
for v in sorted(all_dvs):
    status = 'OK' if v in defined else 'MISSING'
    print(f'  {status}: {v}')
print()
print(f'=== CONTROLS in 15 thesis suites ({len(all_controls)} vars) ===')
for v in sorted(all_controls):
    if v:
        status = 'OK' if v in defined else 'MISSING'
        print(f'  {status}: {v}')
print()
print('=== STALE: defined but not used in body tables ===')
used = all_ivs | all_dvs | all_controls
v5_iv_patterns = ('UncAnsMgr', 'UncAnsCEO', 'UncAnsNoCEO', 'UncPreMgr', 'UncPreNoCEO')
for v in sorted(defined):
    if v not in used:
        flag = 'STALE-V5-IV' if any(v.startswith(p) for p in v5_iv_patterns) else 'STALE-OTHER'
        if flag == 'STALE-V5-IV':
            print(f'  {flag}: {v}')
