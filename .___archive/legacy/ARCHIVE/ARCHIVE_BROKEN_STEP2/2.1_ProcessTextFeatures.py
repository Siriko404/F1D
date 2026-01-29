
import pandas as pd
import numpy as np
from pathlib import Path
import re
import yaml
import sys
import time
import shutil # Added for file ops
import os # Added for symlinks
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer

# ==============================================================================
# Setup & Config
# ==============================================================================

def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / '3_Logs' / '2.1_ProcessTextFeatures'
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

def update_latest_symlink(latest_dir, output_dir, print_fn=print):
    # Remove existing latest
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink():
                os.unlink(str(latest_dir))
            else:
                shutil.rmtree(str(latest_dir))
        except Exception as e:
            print_fn(f"  Warning: Could not remove old 'latest': {e}")
    # Create symlink
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print_fn(f"\nUpdated 'latest' -> {output_dir.name}")
    except OSError:
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print_fn(f"\nCopied outputs to 'latest' (symlink not available)")
        except Exception as e2:
            print_fn(f"\n  Warning: Could not create 'latest': {e2}")

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
    
    # Categories to track
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
    
    # Convert words to uppercase for matching
    df_lm['Word'] = df_lm['Word'].str.upper()
    
    # Create a vocabulary map: word -> {list of categories it belongs to}
    # This is for the "Exact Token Storage" requirement
    word_to_cats = {}
    
    # Also create specific sets for fast checking
    cat_sets = {cat: set() for cat in categories}
    
    for _, row in df_lm.iterrows():
        word = row['Word']
        if not isinstance(word, str): continue
        
        cats_for_word = []
        for cat in categories:
            if row[cat] > 0:
                cat_sets[cat].add(word)
                cats_for_word.append(cat)
        
        if cats_for_word:
            word_to_cats[word] = cats_for_word
            
    # Create master vocabulary list for CountVectorizer
    # We only care about words that are in at least one category
    vocab_list = sorted(list(word_to_cats.keys()))
    
    print(f"  Dictionary Loaded: {len(vocab_list):,} tracked words")
    return vocab_list, cat_sets

def process_year(year, root, config, valid_manifest_df, vocab_list, cat_sets):
    input_path = root / f"1_Inputs/speaker_data_{year}.parquet"
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None
        
    print(f"\nProcessing {year}...")
    start_time = time.time()
    
    # 1. Load Data
    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    
    # 2. Filter by Manifest matches (use file_name set for speed, merge later)
    valid_files = set(valid_manifest_df['file_name'].unique())
    df = df[df['file_name'].isin(valid_files)].copy()
    filtered_rows = len(df)
    print(f"  Loaded {initial_rows:,} rows -> Filtered to {filtered_rows:,} (Manifest match)")
    
    if filtered_rows == 0:
        return None
        
    # 3. Clean Text using Scikit-Learn logic (C-optimized)
    # Regex: Alpha only (no digits/punctuation), >= 2 chars usually? 
    # Blueprint says: r'[a-zA-Z]+'
    print("  Vectorizing text...")
    
    # To support detailed "Top Matches" storage, we need to do a bit more work than just counting.
    # But first, let's get the counts efficiently.
    
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, 
        token_pattern=r'(?u)\b[a-zA-Z]+\b', 
        lowercase=False # We will uppercase input first
    )
    
    # Normalize input: Upper + Collapse Spaces (optional, vectorizer handles spaces)
    # The blueprint required: remove special chars, upper.
    # Vectorizer token_pattern handles the "remove special chars" implicitly.
    # We just need to uppercase.
    raw_text = df['speaker_text'].str.upper()
    
    # Transform -> Sparse Matrix
    # This counts ONLY words in our vocab
    X = vectorizer.transform(raw_text.fillna(""))
    
    # 4. Aggregate Counts per Category
    # Get feature names (should match vocab_list)
    features = vectorizer.get_feature_names_out()
    feature_index_map = {word: i for i, word in enumerate(features)}
    
    results = {}
    for cat, word_set in cat_sets.items():
        # Find indices for this category
        indices = [feature_index_map[w] for w in word_set if w in feature_index_map]
        if indices:
            # Sum columns corresponding to this category
            results[f"{cat}_count"] = np.array(X[:, indices].sum(axis=1)).flatten()
        else:
            results[f"{cat}_count"] = np.zeros(filtered_rows, dtype=int)
            
    # 5. Total Token Count (All words, not just dictionary)
    # We need a separate vectorizer or logic for "Total Words"
    # To be fast: use a simple regex count independently
    print("  Counting total tokens...")
    df['total_tokens'] = raw_text.apply(lambda x: len(re.findall(r'[a-zA-Z]+', str(x))) if pd.notna(x) else 0)
    
    # 6. Detailed Token Lists (Exact & Unique)
    # This is the "expensive" part the user requested.
    # We can optimize this: Only do it for rows with non-zero hits?
    # Or strict implementation: Do it for everyone.
    # To do this efficiently:
    #   We Iterate over the sparse matrix rows? No, sparse matrix loses order.
    #   We MUST re-tokenize to get Exact Matches IN ORDER.
    #   We can filter the token stream against the set.
    
    # 6. Detailed Token Lists (Exact & Unique) PER CATEGORY
    print("  Extracting precise token lists per category (this takes time)...")
    
    # Optimization: Pre-compile regex
    tokenizer = re.compile(r'[a-zA-Z]+')
    
    # We need a fast word -> [cats] lookup within the function scope
    word_to_cats_local = {}
    for cat, wset in cat_sets.items():
        for w in wset:
            if w not in word_to_cats_local: word_to_cats_local[w] = []
            word_to_cats_local[w].append(cat)
            
    def get_matches_row(text):
        if not isinstance(text, str):
            # Return dict of empty lists
            return {cat: [] for cat in cat_sets}
            
        tokens = tokenizer.findall(text)
        cat_matches = {cat: [] for cat in cat_sets}
        
        for t in tokens:
            if t in word_to_cats_local:
                for c in word_to_cats_local[t]:
                    cat_matches[c].append(t)
        return cat_matches

    # Apply row-wise
    # Result is a Series of Dicts: { 'Positive': ['GOOD', 'GREAT'], 'Negative': [] ... }
    match_series = raw_text.apply(get_matches_row)
    
    # Expand into columns
    for cat in cat_sets:
        # Access the list for this category
        
        # 1. Exact Tokens (List)
        df[f'{cat}_tokens'] = match_series.apply(lambda d: d[cat])
        
        # 2. Unique Tokens (List)
        df[f'{cat}_unique_tokens'] = match_series.apply(lambda d: sorted(list(set(d[cat]))))
        
        # 3. Unique Count (Int)
        df[f'{cat}_unique_count'] = df[f'{cat}_unique_tokens'].apply(len)
    
    # 7. Add Count columns
    for cat, counts in results.items():
        df[cat] = counts

    # 8. Merge Company Metadata
    print("  Merging company metadata...")
    # Select available metadata columns from manifest
    # Note: 'tic', 'cik', 'naics', 'cusip' might be missing in manifest, using core identifiers
    meta_cols = ['file_name', 'gvkey', 'conm', 'sic', 'call_desc', 'start_date']
    
    # Ensure columns exist
    available_cols = [c for c in meta_cols if c in valid_manifest_df.columns]
    
    df_meta = valid_manifest_df[available_cols].copy()
    
    # Merge left onto df
    df = pd.merge(df, df_meta, on='file_name', how='left')
    
    # Add Year from start_date if not present
    if 'start_date' in df.columns and 'year' not in df.columns:
         df['year'] = pd.to_datetime(df['start_date']).dt.year
        
    print(f"  Processed {filtered_rows:,} records in {time.time()-start_time:.1f}s")
    return df

def generate_reports(root, processed_data, out_dir):
    # 1. Variable Reference
    var_ref = [
        {'Variable': 'file_name', 'Source': 'Input (Unified-info)', 'Description': 'Unique identifier for the earnings call'},
        {'Variable': 'speaker_name', 'Source': 'Input (Speaker Data)', 'Description': 'Name of the speaker'},
        {'Variable': 'context', 'Source': 'Input (Speaker Data)', 'Description': 'Section of the call (pres=Presentation, qa=Q&A)'},
        {'Variable': 'total_tokens', 'Source': 'Calculated', 'Description': 'Total number of alpha-only tokens in the speaking turn'},
        # New Metadata Cols
        {'Variable': 'gvkey', 'Source': 'Merged (Manifest)', 'Description': 'Global Company Key'},
        {'Variable': 'conm', 'Source': 'Merged (Manifest)', 'Description': 'Company Name'},
        {'Variable': 'sic', 'Source': 'Merged (Manifest)', 'Description': 'Standard Industrial Classification'},
        {'Variable': 'year', 'Source': 'Calculated', 'Description': 'Year of the call'}
    ]
    
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
                  
    for cat in categories:
        var_ref.append({'Variable': f'{cat}_tokens', 'Source': 'Calculated', 'Description': f'List of exact {cat} tokens found'})
        var_ref.append({'Variable': f'{cat}_unique_tokens', 'Source': 'Calculated', 'Description': f'List of unique {cat} tokens found'})
        var_ref.append({'Variable': f'{cat}_count', 'Source': 'LM Dictionary', 'Description': f'Total count of {cat} words (Non-Deduplicated)'})
        var_ref.append({'Variable': f'{cat}_unique_count', 'Source': 'Calculated', 'Description': f'Count of unique {cat} words (Deduplicated)'})

    pd.DataFrame(var_ref).to_csv(out_dir / 'variable_reference.csv', index=False)
    
    # 2. Report MD
    report_lines = ["# Step 2: Text Processing Report", "", f"Generated: {datetime.now()}", ""]
    report_lines.append(f"Total Rows Processed: {sum(len(d) for d in processed_data):,}")
    
    with open(out_dir / 'report_step2.md', 'w') as f:
        f.write("\n".join(report_lines))

def main():
    log_path = setup_logging()
    root = Path(__file__).parent.parent.parent
    config = load_config()
    
    print("=== Step 2: Text Processing (Pure Python) ===")
    
    # 1. Load Manifest
    manifest_path = root / '4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet'
    print(f"Loading Manifest: {manifest_path}")
    manifest = pd.read_parquet(manifest_path)
    # Pass entire manifest DF now
    print(f"Target Universe: {manifest.shape[0]:,} unique calls")
    
    # 2. Load Dictionary
    lm_path = root / '1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv'
    vocab_list, cat_sets = load_lm_dictionary(lm_path)
    
    # 3. Process Years
    processed_dfs = []
    
    # Create Timestamped Output Directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / '4_Outputs' / '2_Linguistic_Analysis' / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output Directory: {out_dir}")
    
    start_year = 2002
    end_year = 2018 
    
    for year in range(start_year, end_year + 1):
        df_year = process_year(year, root, config, manifest, vocab_list, cat_sets)
        if df_year is not None:
            processed_dfs.append(df_year)
            
            # Save Year Output
            out_path = out_dir / f"linguistic_features_{year}.parquet"
            df_year.to_parquet(out_path)
            print(f"  Saved {out_path.name}")
            
    # 4. Reports
    generate_reports(root, processed_dfs, out_dir)
    
    # 5. Update Symlink
    update_latest_symlink(root / '4_Outputs' / '2_Linguistic_Analysis' / 'latest', out_dir)
    
    print("\n=== Processing Complete ===")

if __name__ == "__main__":
    main()
