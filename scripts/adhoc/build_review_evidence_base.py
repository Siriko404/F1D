"""
Phase 0 — Final review evidence base
Single-pass dumper of every per-cell coefficient + diagnostic for every suite cited in body.
Output: tmp/suite_spec_index.json
Schema variants handled: standard (coefs dict), DiD-style (coefs dict, no ivs), Lewbel (direct beta).
"""
import json
from pathlib import Path

BASE = Path('outputs/econometric')

SUITES = {
    'H1.ceo2.decomp':         'h1_cash_holdings_ceo2iv_decomp',
    'H1.ceo2.decomp.qtrexp':  'h1_cash_holdings_ceo2iv_decomp_qtrexp',
    'H1.2.ceo2.decomp':       'h1_2_cash_constraint_ceo2iv_decomp',
    'H1.2.ceo2.decomp.qtrexp':'h1_2_cash_constraint_ceo2iv_decomp_qtrexp',
    'H1.3.cfvol':             'h1_3_cfvol_moderation',
    'H11':                    'h11_prisk_uncertainty',
    'H11-Lag':                'h11_prisk_uncertainty_lag',
    'H23':                    'h23_competition_uncertainty',
    'H24':                    'h24_us_epu',
    'H24b':                   'h24b_global_epu',
    'H14c.ceo2.decomp':       'h14c_spread_bgt_level_ceo2iv_decomp',
    'H18.ceo2.decomp':        'h18_cccl_received_ceo2iv_decomp',
    'H.death.did':            'ceo_death_did_cash',
    'H.dwz.fd':               'h_dwz_fd_cash',
    'H.lewbel.iv':            'h_lewbel_iv_cash',
}


def latest_spec(dir_name):
    d = BASE / dir_name
    if not d.exists():
        return None
    specs = sorted(d.rglob('suite_spec_*.json'))
    return specs[-1] if specs else None


def dump_col_standard(c):
    """Standard schema: each col has coefs dict mapping iv_name → {beta, se, p_two, p_one}."""
    coefs = {}
    for iv, vals in c.get('coefs', {}).items():
        coefs[iv] = {
            'beta':  vals.get('beta'),
            'se':    vals.get('se'),
            'p_two': vals.get('p_two'),
            'p_one': vals.get('p_one'),
        }
    return {
        'col':         c.get('col'),
        'dv':          c.get('dv'),
        'fe_entity':   c.get('fe_entity'),
        'fe_time':     c.get('fe_time'),
        'fe_label':    c.get('fe_label'),
        'fe_type':     c.get('fe_type'),
        'control_vars':c.get('control_vars') or c.get('controls'),
        'n_obs':       c.get('n_obs'),
        'n_firms':     c.get('n_firms'),
        'r2':          c.get('r2'),
        'r2_within':   c.get('r2_within'),
        'coefs':       coefs,
        'diagnostics': c.get('diagnostics', {}),
    }


def dump_col_lewbel(c):
    """Lewbel schema: each col has direct beta/se/p (single endogenous coef per col)."""
    return {
        'col':    c.get('col'),
        'label':  c.get('label'),
        'spec':   c.get('spec'),
        'beta':   c.get('beta'),
        'se':     c.get('se'),
        't':      c.get('t'),
        'p_two':  c.get('p_two'),
        'p_one':  c.get('p_one'),
        'n_obs':  c.get('n_obs'),
        'n_firms':c.get('n_firms'),
        'r2':     c.get('r2'),
        'diagnostics': c.get('diagnostics', {}),
    }


def dump_suite(suite_id, dir_name):
    p = latest_spec(dir_name)
    if p is None:
        return {'suite_id': suite_id, 'spec_path': None, 'error': 'NO_SPEC_FOUND'}
    with open(p) as f:
        d = json.load(f)
    cols = d.get('columns', [])
    if cols and 'beta' in cols[0] and 'coefs' not in cols[0]:
        col_dumps = [dump_col_lewbel(c) for c in cols]
        schema = 'lewbel'
    else:
        col_dumps = [dump_col_standard(c) for c in cols]
        schema = 'standard'
    return {
        'suite_id':   suite_id,
        'spec_path':  str(p.relative_to('.')) if p.is_relative_to('.') else str(p),
        'schema':     schema,
        'title':      d.get('title') or d.get('suite_label'),
        'sample_label': d.get('sample_label'),
        'tail_direction': d.get('tail') or d.get('tail_direction'),
        'ivs':        [iv['name'] for iv in d.get('ivs', [])] if 'ivs' in d else None,
        'controls':   d.get('controls'),
        'n_cols':     len(cols),
        'columns':    col_dumps,
        # Endogeneity-suite specials
        'n_treated':       d.get('n_treated'),
        'n_matches':       d.get('n_matches'),
        'psm_covariates':  d.get('psm_covariates'),
        'window_pre':      d.get('window_pre'),
        'window_post':     d.get('window_post'),
        'ghafoor_2023_anchor_beta': d.get('ghafoor_2023_anchor_beta'),
        'ghafoor_2023_anchor_p':    d.get('ghafoor_2023_anchor_p'),
        'balance_table':   d.get('balance_table'),
        'parallel_trends_placebo': d.get('parallel_trends_placebo'),
        'pesaran_taylor_diagnostic': d.get('pesaran_taylor_diagnostic'),
    }


out = {sid: dump_suite(sid, dn) for sid, dn in SUITES.items()}
out_path = Path('tmp/suite_spec_index.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')

# Coverage summary
print('Suite coverage:')
for sid, payload in out.items():
    if payload.get('error'):
        print(f'  {sid:30s}: {payload["error"]}')
    else:
        ncols = payload['n_cols']
        ivs = payload.get('ivs')
        ivlbl = ','.join(ivs) if ivs else 'n/a'
        ns = [c.get('n_obs') for c in payload['columns'] if c.get('n_obs')]
        nrng = f'{min(ns):,}-{max(ns):,}' if ns else 'no_n'
        print(f'  {sid:30s}: cols={ncols} ivs=({ivlbl}) n={nrng}')
print()
print(f'Wrote: {out_path}')
