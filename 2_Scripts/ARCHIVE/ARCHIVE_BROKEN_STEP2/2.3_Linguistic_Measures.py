"""
Step 2.3: Linguistic Measures (Vectorized - Fast)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import nltk
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import shutil
import os
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / '1_Sample'))
try:
    from step1_utils import update_latest_symlink
except ImportError:
    def update_latest_symlink(latest_dir, output_dir):
        if latest_dir.exists() or latest_dir.is_symlink():
            try:
                if latest_dir.is_symlink(): os.unlink(str(latest_dir))
                else: shutil.rmtree(str(latest_dir))
            except: pass
        try: os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        except: shutil.copytree(str(output_dir), str(latest_dir))

def setup_nltk():
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK WordNet...")
        nltk.download('wordnet')

def load_config():
    return Path(__file__).parent.parent.parent

def build_lemma_map(root):
    """Build a fast lookup map for all words in the LM Dictionary."""
    print("Building Fast Lemma Map...")
    lemmatizer = WordNetLemmatizer()
    
    dict_path = root / '1_Inputs' / 'Loughran-McDonald_MasterDictionary_1993-2024.csv'
    if not dict_path.exists():
        print(f"Error: Dictionary not found at {dict_path}")
        return {}
        
    df = pd.read_csv(dict_path)
    lemma_map = {}
    words = df['Word'].dropna().unique()
    
    for w in words:
        w_lower = str(w).lower()
        lemma_map[w_lower] = lemmatizer.lemmatize(w_lower)
        
    print(f"  Mapped {len(lemma_map):,} dictionary words to lemmas.")
    return lemma_map

def fast_entropy(tokens, lemma_map):
    """
    Calculate Normalized Shannon Entropy using only Python builtins + numpy.
    No pandas Series creation (which is slow).
    """
    if tokens is None or len(tokens) == 0:
        return 0.0
    
    # Lemmatize and count using Counter (pure Python, fast)
    lemmas = [lemma_map.get(t, t) for t in tokens]
    counts = Counter(lemmas)
    
    total = len(lemmas)
    unique = len(counts)
    
    if unique <= 1:
        return 0.0
    
    # Calculate entropy using numpy
    probs = np.array(list(counts.values())) / total
    entropy = -np.sum(probs * np.log(probs))
    max_entropy = np.log(unique)
    
    return entropy / max_entropy if max_entropy > 0 else 0.0

def process_year(year, root, lemma_map, out_dir):
    """Process a single year using vectorized operations."""
    print(f"\nProcessing {year}...")
    
    in_path = root / f"4_Outputs/2_Linguistic_Analysis/latest/linguistic_features_{year}.parquet"
    if not in_path.exists():
        print(f"  Warning: Input file not found: {in_path}")
        return
        
    df = pd.read_parquet(in_path)
    total_rows = len(df)
    print(f"  Loaded {total_rows:,} records")
    
    t0 = datetime.now()
    
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
    
    # Metadata columns to keep (all except speaker_text and token lists)
    # Order: identifiers first, then speaker info, then company metadata
    meta_cols_order = [
        'file_name', 'last_update', 'speaker_name', 'employer', 'role', 
        'speaker_number', 'context', 'section', 'total_tokens',
        'gvkey', 'conm', 'sic', 'call_desc', 'start_date', 'year'
    ]
    keep_meta = [c for c in meta_cols_order if c in df.columns]
    
    result = df[keep_meta].copy()
    
    for cat in categories:
        print(f"    {cat}...", end=' ')
        cat_t0 = datetime.now()
        
        tokens_col = f'{cat}_tokens'
        unique_col = f'{cat}_unique_tokens'
        count_col = f'{cat}_count'
        
        # VECTORIZED: _pct = count / total_tokens
        result[f'{cat}_pct'] = df[count_col] / df['total_tokens'].replace(0, np.nan)
        result[f'{cat}_pct'] = result[f'{cat}_pct'].fillna(0)
        
        # VECTORIZED: _unique_pct = unique_count / total_tokens  
        result[f'{cat}_unique_pct'] = df[tokens_col].apply(
            lambda x: len(set(x)) if isinstance(x, (list, np.ndarray)) and len(x) > 0 else 0
        ) / df['total_tokens'].replace(0, np.nan)
        result[f'{cat}_unique_pct'] = result[f'{cat}_unique_pct'].fillna(0)
        
        # APPLY (still needed for entropy, but uses fast function)
        result[f'{cat}_entropy'] = df[tokens_col].apply(lambda x: fast_entropy(x, lemma_map))
        
        # VECTORIZED: _interaction = pct * entropy
        result[f'{cat}_interaction'] = result[f'{cat}_pct'] * result[f'{cat}_entropy']
        
        print(f"{(datetime.now() - cat_t0).total_seconds():.1f}s")
    
    # Save
    out_path = out_dir / f"linguistic_measures_{year}.parquet"
    result.to_parquet(out_path)
    
    dt = (datetime.now() - t0).total_seconds()
    print(f"  Saved {out_path.name} ({len(result):,} rows in {dt:.1f}s)")

def generate_reports(out_dir):
    """Generate variable_reference.csv for the output."""
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
    
    rows = [
        # Metadata columns - sources match Step 2.1 variable_reference format
        ('file_name', 'Input (Unified-info)', 'Unique identifier for the earnings call'),
        ('last_update', 'Input (Unified-info)', 'Last update timestamp of the call data'),
        ('speaker_name', 'Input (Speaker Data)', 'Name of the speaker'),
        ('employer', 'Input (Speaker Data)', 'Employer of the speaker'),
        ('role', 'Input (Speaker Data)', 'Role/title of the speaker'),
        ('speaker_number', 'Input (Speaker Data)', 'Speaker sequence number in the call'),
        ('context', 'Input (Speaker Data)', 'Section of the call (pres/qa)'),
        ('section', 'Input (Speaker Data)', 'Detailed section identifier'),
        ('total_tokens', 'Calculated (Step 2.1)', 'Total alpha-only tokens in speaking turn'),
        ('gvkey', 'Merged (Manifest)', 'Global Company Key'),
        ('conm', 'Merged (Manifest)', 'Company Name'),
        ('sic', 'Merged (Manifest)', 'Standard Industrial Classification'),
        ('call_desc', 'Merged (Manifest)', 'Call description'),
        ('start_date', 'Merged (Manifest)', 'Call date'),
        ('year', 'Calculated (Step 2.1)', 'Year of the call'),
    ]
    
    # Add feature columns for each category
    for cat in categories:
        rows.extend([
            (f'{cat}_pct', 'Calculated (Step 2.3)', f'Proportion of {cat} tokens to total tokens'),
            (f'{cat}_unique_pct', 'Calculated (Step 2.3)', f'Proportion of unique {cat} tokens to total tokens'),
            (f'{cat}_entropy', 'Calculated (Step 2.3)', f'Normalized Shannon Entropy of {cat} tokens (0=focused, 1=diffuse)'),
            (f'{cat}_interaction', 'Calculated (Step 2.3)', f'{cat}_pct * {cat}_entropy'),
        ])
    
    df = pd.DataFrame(rows, columns=['Variable', 'Source', 'Description'])
    out_path = out_dir / 'variable_reference.csv'
    df.to_csv(out_path, index=False)
    print(f"\nSaved variable_reference.csv ({len(df)} variables)")

def main():
    print("=== Step 2.3: Linguistic Measures (Vectorized) ===")
    root = load_config()
    setup_nltk()
    
    lemma_map = build_lemma_map(root)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / '4_Outputs' / '2_Linguistic_Analysis' / f'extended_{timestamp}'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output Directory: {out_dir}")
    
    start_year = 2002
    end_year = 2018
    
    for year in range(start_year, end_year + 1):
        process_year(year, root, lemma_map, out_dir)
    
    # Generate reports
    generate_reports(out_dir)
            
    update_latest_symlink(root / '4_Outputs' / '2_Linguistic_Analysis' / 'extended_latest', out_dir)
    print("\n=== Processing Complete ===")

if __name__ == "__main__":
    main()

