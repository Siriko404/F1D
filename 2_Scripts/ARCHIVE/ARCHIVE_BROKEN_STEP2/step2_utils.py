
import pandas as pd
import numpy as np
from nltk.stem import WordNetLemmatizer

def calculate_entropy(tokens, lemma_map):
    """
    Calculate Normalized Shannon Entropy for a list of tokens.
    H_norm = -Sum(p_i * ln(p_i)) / ln(N_unique)
    """
    if tokens is None or len(tokens) == 0:
        return 0.0
        
    # 1. Lemmatize (Fast Lookup)
    # The tokens in the parquet are likely lowercase if from CountVectorizer(lowercase=True), 
    # but the lemma_map keys will be pre-processed to match.
    # We default to the token itself if not found.
    lemmas = [lemma_map.get(t, t) for t in tokens]
    
    # 2. Frequency Distribution
    series = pd.Series(lemmas)
    counts = series.value_counts()
    total = len(lemmas)
    unique = len(counts)
    
    if unique <= 1:
        return 0.0
        
    # 3. Probabilities
    probs = counts / total
    
    # 4. Shannon Entropy
    entropy = -np.sum(probs * np.log(probs))
    
    # 5. Normalize
    max_entropy = np.log(unique)
    
    if max_entropy == 0:
        return 0.0
        
    return entropy / max_entropy

def process_row(row, categories, lemma_map=None):
    """Calculate metrics for a single row with fast lookup."""
    if lemma_map is None:
        lemma_map = {}
        
    total_doc_tokens = row['total_tokens']
    
    metrics = {}
    
    for cat in categories:
        tokens = row.get(f'{cat}_tokens', [])
        unique_tokens = row.get(f'{cat}_unique_tokens', [])
        
        # 1. Pct (Intensity)
        n_tokens = len(tokens) if isinstance(tokens, (list, np.ndarray)) else 0
        metrics[f'{cat}_pct'] = n_tokens / total_doc_tokens if total_doc_tokens > 0 else 0.0
            
        # 2. Unique Pct (Breadth)
        n_unique = len(unique_tokens) if isinstance(unique_tokens, (list, np.ndarray)) else 0
        metrics[f'{cat}_unique_pct'] = n_unique / total_doc_tokens if total_doc_tokens > 0 else 0.0
            
        # 3. Entropy
        metrics[f'{cat}_entropy'] = calculate_entropy(tokens, lemma_map)
        
        # 4. Interaction
        metrics[f'{cat}_interaction'] = metrics[f'{cat}_pct'] * metrics[f'{cat}_entropy']
        
    return pd.Series(metrics)
