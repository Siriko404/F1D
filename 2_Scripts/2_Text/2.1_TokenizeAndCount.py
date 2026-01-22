
import pandas as pd
import numpy as np
from pathlib import Path
import re
import yaml
import sys
import time
import shutil
import os
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer

# ==============================================================================
# Setup & Config
# ==============================================================================

def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / '3_Logs' / '2.1_TokenizeAndCount'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"
    
    class DualWriter:
        def __init__(self, path):
            self.file = open(path, 'w', encoding='utf-8')
            self.stdout = sys.stdout
        def write(self, msg):
            self.stdout.write(msg)
            self.file.write(msg)
            self.file.flush()
        def flush(self):
            self.stdout.flush()
            self.file.flush()
            
    sys.stdout = DualWriter(log_path)
    return log_path

def update_latest_symlink(latest_dir, output_dir):
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink(): os.unlink(str(latest_dir))
            else: shutil.rmtree(str(latest_dir))
        except Exception: pass
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print(f"\nUpdated 'latest' -> {output_dir.name}")
    except OSError:
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print(f"\nCopied outputs to 'latest'")
        except Exception: pass

def load_config():
    root = Path(__file__).parent.parent.parent
    with open(root / 'config' / 'project.yaml', 'r') as f:
        return yaml.safe_load(f)

# ==============================================================================
# Logic: Tokenization & Counting
# ==============================================================================

def load_lm_dictionary(dict_path):
    print(f"Loading LM Dictionary: {dict_path.name}")
    df_lm = pd.read_csv(dict_path)
    
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
    
    df_lm['Word'] = df_lm['Word'].str.upper()
    
    # Map words to categories
    # Only keep words that have at least one category > 0
    cat_sets = {cat: set() for cat in categories}
    vocab_set = set()
    
    for _, row in df_lm.iterrows():
        word = row['Word']
        if not isinstance(word, str): continue
        
        for cat in categories:
            if row[cat] > 0:
                cat_sets[cat].add(word)
                vocab_set.add(word)
            
    vocab_list = sorted(list(vocab_set))
    print(f"  Dictionary Loaded: {len(vocab_list):,} tracked words")
    return vocab_list, cat_sets

def process_year(year, root, config, valid_files, vocab_list, cat_sets, out_dir):
    input_path = root / f"1_Inputs/speaker_data_{year}.parquet"
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None
        
    print(f"\nProcessing {year}...")
    t0 = time.time()
    
    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    
    # Filter
    df = df[df['file_name'].isin(valid_files)].copy()
    print(f"  Loaded {initial_rows:,} -> {len(df):,} (Manifest match)")
    
    if len(df) == 0: return None
    
    # Vectorize
    print("  Vectorizing...")
    # Token pattern matches Legacy: Alpha only, splitting on anything else
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, 
        token_pattern=r'(?u)\b[a-zA-Z]+\b', 
        lowercase=False
    )
    
    raw_text = df['speaker_text'].astype(str).str.upper()
    X = vectorizer.transform(raw_text)
    
    # Aggregate counts per category
    features = vectorizer.get_feature_names_out()
    feat_map = {w: i for i, w in enumerate(features)}
    
    # Prepare result dataframe output columns
    # We want rows to align with df
    # Start with metadata
    meta_cols = ['file_name', 'speaker_number', 'context', 'role', 'speaker_name', 'employer']
    # Ensure they exist
    meta_cols = [c for c in meta_cols if c in df.columns]
    result = df[meta_cols].copy()
    
    for cat, wset in cat_sets.items():
        indices = [feat_map[w] for w in wset if w in feat_map]
        if indices:
            result[f'{cat}_count'] = np.array(X[:, indices].sum(axis=1)).flatten()
        else:
            result[f'{cat}_count'] = 0
            
    # Total Tokens (Alpha only)
    print("  Counting total tokens...")
    # Use same regex as vectorizer for consistency
    regex = re.compile(r'(?u)\b[a-zA-Z]+\b')
    result['total_tokens'] = raw_text.apply(lambda x: len(regex.findall(x)))
    
    # Save
    out_path = out_dir / f"linguistic_counts_{year}.parquet"
    result.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name} ({time.time()-t0:.1f}s)")
    return result

def main():
    print("=== Step 2.1: Tokenize & Count (Legacy Compatible) ===")
    root = Path(__file__).parent.parent.parent
    log_path = setup_logging()
    
    # Output Setup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_base = root / '4_Outputs' / '2_Textual_Analysis'
    out_dir = out_base / f'2.1_Tokenized' / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Manifest
    manifest_path = root / '4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet'
    manifest = pd.read_parquet(manifest_path, columns=['file_name'])
    valid_files = set(manifest['file_name'])
    print(f"Universe: {len(valid_files):,} files")
    
    # Load Dict
    lm_path = root / '1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv'
    vocab_list, cat_sets = load_lm_dictionary(lm_path)
    
    # Process
    config = load_config()
    for year in range(2002, 2019):
        process_year(year, root, config, valid_files, vocab_list, cat_sets, out_dir)
        
    update_latest_symlink(out_base / '2.1_Tokenized' / 'latest', out_dir)
    print("\n=== Complete ===")

if __name__ == "__main__":
    main()
