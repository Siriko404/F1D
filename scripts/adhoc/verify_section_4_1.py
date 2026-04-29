"""Cross-check §4.1 driver-prose claims vs latest suite_spec_*.json (per-cell).
Programmatic extraction only; no LLM transcription.
Output: pass/fail per claim with actual beta + p_one values.
"""
import json
from pathlib import Path

BASE = Path('outputs/econometric')

def latest(d):
    cands = sorted((BASE / d).rglob('suite_spec_*.json'))
    return cands[-1] if cands else None

def cells(p):
    """Return list of dicts: col, dv, fe_entity, beta, p_one for primary IV."""
    j = json.loads(p.read_text())
    iv_keys = [iv['name'] for iv in j.get('ivs', [])]
    primary = iv_keys[0]
    out = []
    for c in j.get('columns', []):
        cf = c.get('coefs', {}).get(primary, {})
        out.append(dict(
            col=c.get('col'),
            dv=c.get('dv'),
            fe_entity=c.get('fe_entity'),
            beta=cf.get('beta'),
            p_one=cf.get('p_one'),
        ))
    return primary, out

def fmt(v): return 'None' if v is None else f'{v:+.4f}' if isinstance(v, float) else str(v)

print('# §4.1 driver-prose vs suite_specs cross-check\n')

for tag, d in [
    ('H11 PRisk', 'h11_prisk_uncertainty'),
    ('H11-Lag', 'h11_prisk_uncertainty_lag'),
    ('H24 US-EPU', 'h24_us_epu'),
    ('H24b GEPU', 'h24b_global_epu'),
    ('H23 Competition', 'h23_competition_uncertainty'),
]:
    p = latest(d)
    if p is None:
        print(f'NO SPEC: {tag}\n')
        continue
    iv, cs = cells(p)
    print(f'## {tag}  (IV={iv})  spec={p.relative_to(BASE)}')
    for c in cs:
        sig = ''
        if c['p_one'] is not None:
            if c['p_one'] < 0.01: sig = '***'
            elif c['p_one'] < 0.05: sig = '**'
            elif c['p_one'] < 0.10: sig = '*'
            else: sig = ''
        print(f'  col {c["col"]} | dv={c["dv"]:>13} | fe={c["fe_entity"]:>8} | beta={fmt(c["beta"])} | p_one={fmt(c["p_one"])}  {sig}')
    print()
