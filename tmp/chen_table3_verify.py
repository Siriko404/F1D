"""Verify Chen Table 3 Panel A cell values via pdfplumber.extract_tables()
per /pdf SKILL tables.md.

Try multiple detection strategies because Table 3 spans pages 11-13 (PDF index)
which are journal pages 300-302. The Hennes/JAAF style uses borderless tables.
"""

import pdfplumber

PDF = 'docs/papers/chen_etal_2017_restatement_jaaf.pdf'

with pdfplumber.open(PDF) as pdf:
    for pdf_p in [11, 12, 13]:  # Table 3 spans these
        page = pdf.pages[pdf_p - 1]
        print(f'\n{"="*80}')
        print(f'PDF p.{pdf_p} (j.p.{pdf_p+289}) — TABLE 3 region')
        print('=' * 80)

        # Strategy 2 — text-based for borderless tables
        for strat_name, settings in [
            ('default', None),
            ('text-based', {'vertical_strategy': 'text', 'horizontal_strategy': 'text'}),
            ('text-tighter', {'vertical_strategy': 'text', 'horizontal_strategy': 'text',
                              'snap_tolerance': 5, 'join_tolerance': 5,
                              'min_words_vertical': 2}),
        ]:
            try:
                tables = page.extract_tables(table_settings=settings) if settings else page.extract_tables()
                print(f'\n--- Strategy: {strat_name} → {len(tables) if tables else 0} tables ---')
                if tables:
                    for ti, table in enumerate(tables):
                        # Look for "1,391" or "1391" in any cell
                        flat_cells = [str(c) for row in table for c in row if c is not None]
                        n_hit = any('1,391' in c or '1391' in c for c in flat_cells)
                        n_046_hit = any('0.046' in c for c in flat_cells)
                        n_034_hit = any('0.034' in c for c in flat_cells)
                        if n_hit or n_046_hit or n_034_hit:
                            print(f'  Table {ti}: HIT — n=1,391: {n_hit}, β=0.046: {n_046_hit}, DiD=0.034: {n_034_hit}')
                            # Print rows containing those values
                            for row in table:
                                if any(c and ('1,391' in str(c) or '1391' in str(c) or '0.046' in str(c) or '0.034' in str(c)) for c in row):
                                    print(f'    row: {row}')
            except Exception as e:
                print(f'  Strategy {strat_name} ERROR: {e}')


# Also try a brute-force string search of the page's words+positions
print('\n' + '=' * 80)
print('FALLBACK: brute string search via page.chars on p.11')
print('=' * 80)
with pdfplumber.open(PDF) as pdf:
    page = pdf.pages[10]  # PDF p.11 is index 10
    # Build text via chars (preserves positions)
    chars = page.chars
    full = ''.join(c.get('text', '') for c in chars)
    # Simple search
    for needle in ['1,391', '1391', '0.046', '4.84', '0.034', '.002']:
        if needle in full:
            idx = full.find(needle)
            print(f'  "{needle}" FOUND in chars stream at offset {idx}')
            print(f'    context: ...{full[max(0,idx-30):idx+40]}...')
        else:
            print(f'  "{needle}" NOT in chars stream')
