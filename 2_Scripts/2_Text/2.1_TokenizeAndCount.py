import pandas as pd
import numpy as np
from pathlib import Path
import re
import yaml
import sys
import time
import shutil
import os
import json
import hashlib
from datetime import datetime
from typing import Tuple
from sklearn.feature_extraction.text import CountVectorizer
from concurrent.futures import ProcessPoolExecutor, as_completed

# ==============================================================================
# Setup & Config
# ==============================================================================


def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / "3_Logs" / "2.1_TokenizeAndCount"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"

    class DualWriter:
        def __init__(self, path):
            self.file = open(path, "w", encoding="utf-8")
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
            if latest_dir.is_symlink():
                os.unlink(str(latest_dir))
            else:
                shutil.rmtree(str(latest_dir))
        except Exception:
            pass
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print(f"\nUpdated 'latest' -> {output_dir.name}")
    except OSError:
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print(f"\nCopied outputs to 'latest'")
        except Exception:
            pass


def load_config():
    root = Path(__file__).parent.parent.parent
    with open(root / "config" / "project.yaml", "r") as f:
        return yaml.safe_load(f)


# ==============================================================================
# Stats Helpers
# ==============================================================================


def compute_file_checksum(filepath, algorithm="sha256"):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting."""
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        if isinstance(v, float):
            print(f"{prefix}{label}: {v:,.2f}")
        elif isinstance(v, int):
            print(f"{prefix}{label}: {v:,}")
        else:
            print(f"{prefix}{label}: {v}")


def analyze_missing_values(df):
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    inp = stats["input"]
    out = stats["output"]
    delta = inp["total_rows"] - out["final_rows"]
    delta_pct = (delta / inp["total_rows"] * 100) if inp["total_rows"] > 0 else 0

    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")

    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Value':>15}")
        print("-" * 48)
        for step, count in stats["processing"].items():
            if isinstance(count, (int, float)):
                print(f"{step:<30} {count:>15,}")
            elif not isinstance(count, list):
                print(f"{step:<30} {count}")

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Logic: Tokenization & Counting
# ==============================================================================
# Logic: Tokenization & Counting
# ==============================================================================


def load_lm_dictionary(dict_path):
    print(f"Loading LM Dictionary: {dict_path.name}")
    df_lm = pd.read_csv(dict_path)

    categories = [
        "Negative",
        "Positive",
        "Uncertainty",
        "Litigious",
        "Strong_Modal",
        "Weak_Modal",
        "Constraining",
    ]

    df_lm["Word"] = df_lm["Word"].str.upper()

    # Map words to categories
    # Only keep words that have at least one category > 0
    cat_sets = {cat: set() for cat in categories}
    vocab_set = set()

    # OPTIMIZATION: Vectorized melt replaces .iterrows()
    # Expected speedup: 10-100x for LM dictionary (10K rows)
    # Ref: 10-RESEARCH.md Pattern 1, Example 1
    df_valid = df_lm[df_lm["Word"].notna()].copy()

    # Melt to long format for vectorization
    df_melted = df_valid.melt(
        id_vars=["Word"], value_vars=categories, var_name="category", value_name="count"
    )

    # Filter rows where count > 0
    filtered = df_melted[df_melted["count"] > 0]

    # Collect words per category
    for cat in categories:
        cat_words = filtered[filtered["category"] == cat]["Word"].unique()
        cat_sets[cat].update(cat_words)

    # Update vocabulary set
    vocab_set.update(filtered["Word"].unique())

    vocab_list = sorted(list(vocab_set))
    print(f"  Dictionary Loaded: {len(vocab_list):,} tracked words")
    return vocab_list, cat_sets


# OPTIMIZATION: Parallel year processing with ProcessPoolExecutor
# thread_count from config/project.yaml controls parallelism
# Expected speedup: near-linear for CPU-bound operations
# Determinism: Results sorted by year before aggregation
# Ref: 10-RESEARCH.md Pattern 3, Example 2


def process_year_worker(
    year: int,
    root: Path,
    config: dict,
    valid_files: set,
    vocab_list: list,
    cat_sets: dict,
    out_dir: Path,
) -> Tuple[int, dict]:
    """
    Process a single year - must be picklable for ProcessPoolExecutor.

    Returns:
        Tuple of (year, year_stats_dict)
    """
    input_path = root / f"1_Inputs/speaker_data_{year}.parquet"
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return year, {"year": year, "skipped": True}

    print(f"\nProcessing {year}...")
    t0 = time.time()

    year_stats = {
        "year": year,
        "input_rows": 0,
        "output_rows": 0,
        "filtered_rows": 0,
        "total_tokens": 0,
        "vocab_hits": 0,
        "avg_tokens_per_doc": 0.0,
        "vocabulary_size": len(vocab_list),
    }

    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    year_stats["input_rows"] = initial_rows

    # Filter
    df = df[df["file_name"].isin(valid_files)].copy()
    year_stats["filtered_rows"] = initial_rows - len(df)
    print(f"  Loaded {initial_rows:,} -> {len(df):,} (Manifest match)")

    if len(df) == 0:
        return year, year_stats

    # Vectorize
    print("  Vectorizing...")
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, token_pattern=r"(?u)\b[a-zA-Z]+\b", lowercase=False
    )

    raw_text = df["speaker_text"].astype(str).str.upper()
    X = vectorizer.transform(raw_text)

    year_stats["vocab_hits"] = int(X.sum())

    # Aggregate counts per category
    features = vectorizer.get_feature_names_out()
    feat_map = {w: i for i, w in enumerate(features)}

    # Prepare result dataframe output columns
    meta_cols = [
        "file_name",
        "speaker_number",
        "context",
        "role",
        "speaker_name",
        "employer",
    ]
    meta_cols = [c for c in meta_cols if c in df.columns]
    result = df[meta_cols].copy()

    for cat, wset in cat_sets.items():
        indices = [feat_map[w] for w in wset if w in feat_map]
        if indices:
            result[f"{cat}_count"] = np.array(X[:, indices].sum(axis=1)).flatten()
        else:
            result[f"{cat}_count"] = 0

    # Total Tokens (Alpha only)
    print("  Counting total tokens...")
    regex = re.compile(r"(?u)\b[a-zA-Z]+\b")
    result["total_tokens"] = raw_text.apply(lambda x: len(regex.findall(x)))

    year_stats["total_tokens"] = int(result["total_tokens"].sum())
    year_stats["avg_tokens_per_doc"] = round(result["total_tokens"].mean(), 2)
    year_stats["output_rows"] = len(result)

    # Save
    out_path = out_dir / f"linguistic_counts_{year}.parquet"
    result.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name} ({time.time() - t0:.1f}s)")
    return year, year_stats


def process_year(year, root, config, valid_files, vocab_list, cat_sets, out_dir):
    input_path = root / f"1_Inputs/speaker_data_{year}.parquet"
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None, None

    print(f"\nProcessing {year}...")
    t0 = time.time()

    year_stats = {
        "year": year,
        "input_rows": 0,
        "output_rows": 0,
        "filtered_rows": 0,
        "total_tokens": 0,
        "vocab_hits": 0,
        "avg_tokens_per_doc": 0.0,
        "vocabulary_size": len(vocab_list),
    }

    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    year_stats["input_rows"] = initial_rows

    # Filter
    df = df[df["file_name"].isin(valid_files)].copy()
    year_stats["filtered_rows"] = initial_rows - len(df)
    print(f"  Loaded {initial_rows:,} -> {len(df):,} (Manifest match)")

    if len(df) == 0:
        return None, year_stats

    # Vectorize
    print("  Vectorizing...")
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, token_pattern=r"(?u)\b[a-zA-Z]+\b", lowercase=False
    )

    raw_text = df["speaker_text"].astype(str).str.upper()
    X = vectorizer.transform(raw_text)

    year_stats["vocab_hits"] = int(X.sum())

    # Aggregate counts per category
    features = vectorizer.get_feature_names_out()
    feat_map = {w: i for i, w in enumerate(features)}

    # Prepare result dataframe output columns
    meta_cols = [
        "file_name",
        "speaker_number",
        "context",
        "role",
        "speaker_name",
        "employer",
    ]
    meta_cols = [c for c in meta_cols if c in df.columns]
    result = df[meta_cols].copy()

    for cat, wset in cat_sets.items():
        indices = [feat_map[w] for w in wset if w in feat_map]
        if indices:
            result[f"{cat}_count"] = np.array(X[:, indices].sum(axis=1)).flatten()
        else:
            result[f"{cat}_count"] = 0

    # Total Tokens (Alpha only)
    print("  Counting total tokens...")
    regex = re.compile(r"(?u)\b[a-zA-Z]+\b")
    result["total_tokens"] = raw_text.apply(lambda x: len(regex.findall(x)))

    year_stats["total_tokens"] = int(result["total_tokens"].sum())
    year_stats["avg_tokens_per_doc"] = round(result["total_tokens"].mean(), 2)
    year_stats["output_rows"] = len(result)

    # Save
    out_path = out_dir / f"linguistic_counts_{year}.parquet"
    result.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name} ({time.time() - t0:.1f}s)")
    return result, year_stats


def main():
    print("=== Step 2.1: Tokenize & Count (Legacy Compatible) ===")
    root = Path(__file__).parent.parent.parent
    log_path = setup_logging()

    # Output Setup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_base = root / "4_Outputs" / "2_Textual_Analysis"
    out_dir = out_base / f"2.1_Tokenized" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Stats
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    stats = {
        "step_id": "2.1_TokenizeAndCount",
        "timestamp": timestamp,
        "git_sha": None,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {
            "vocabulary_size": 0,
            "total_vocab_hits": 0,
            "total_tokens": 0,
            "years_processed": 0,
            "years_skipped": 0,
            "per_year": [],
        },
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Load Manifest
    manifest_path = (
        root
        / "4_Outputs"
        / "1.4_AssembleManifest"
        / "latest"
        / "master_sample_manifest.parquet"
    )
    manifest = pd.read_parquet(manifest_path, columns=["file_name"])
    valid_files = set(manifest["file_name"])
    print(f"Universe: {len(valid_files):,} files")

    stats["input"]["files"].append(str(manifest_path))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_path)
    )

    # Load Dict
    lm_path = root / "1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv"
    vocab_list, cat_sets = load_lm_dictionary(lm_path)

    stats["input"]["files"].append(str(lm_path))
    stats["input"]["checksums"]["Loughran-McDonald_MasterDictionary.csv"] = (
        compute_file_checksum(lm_path)
    )
    stats["processing"]["vocabulary_size"] = len(vocab_list)

    # Process
    config = load_config()
    years = range(2002, 2019)
    thread_count = config.get("determinism", {}).get("thread_count", 1)

    print(f"\nProcessing {len(years)} years with {thread_count} worker(s)...")

    results = {}
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        # Submit all years
        futures = {
            executor.submit(
                process_year_worker,
                year,
                root,
                config,
                valid_files,
                vocab_list,
                cat_sets,
                out_dir,
            ): year
            for year in years
        }

        # Collect results as they complete
        for future in as_completed(futures):
            year = futures[future]
            try:
                _, year_stats = future.result()
                results[year] = year_stats
            except Exception as e:
                print(f"  ERROR: Year {year} failed: {e}")
                raise

    # Combine stats in year order for determinism
    stats["processing"]["per_year"] = [
        results[y] for y in sorted(results.keys()) if results[y].get("skipped") is None
    ]

    total_input_rows = sum(
        s.get("input_rows", 0) for s in stats["processing"]["per_year"]
    )
    total_output_rows = sum(
        s.get("output_rows", 0) for s in stats["processing"]["per_year"]
    )
    total_tokens = sum(
        s.get("total_tokens", 0) for s in stats["processing"]["per_year"]
    )
    total_vocab_hits = sum(
        s.get("vocab_hits", 0) for s in stats["processing"]["per_year"]
    )

    stats["input"]["total_rows"] = total_input_rows
    stats["output"]["final_rows"] = total_output_rows
    stats["processing"]["total_tokens"] = total_tokens
    stats["processing"]["total_vocab_hits"] = total_vocab_hits
    stats["processing"]["years_processed"] = len(stats["processing"]["per_year"])
    stats["processing"]["years_skipped"] = (
        len(years) - stats["processing"]["years_processed"]
    )

    # Output files
    output_files = list(out_dir.glob("linguistic_counts_*.parquet"))
    stats["output"]["files"] = [f.name for f in output_files]
    stats["output"]["final_columns"] = 14 if output_files else 0

    # Summary Stats
    print_stat("Years Processed", value=stats["processing"]["years_processed"])
    print_stat("Years Skipped", value=stats["processing"]["years_skipped"])
    print_stat("Total Input Rows", value=stats["input"]["total_rows"])
    print_stat("Total Output Rows", value=stats["output"]["final_rows"])
    print_stat("Total Tokens", value=stats["processing"]["total_tokens"])
    print_stat("Vocabulary Hits", value=stats["processing"]["total_vocab_hits"])

    # Timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Optimization metrics
    stats["optimization"] = {
        "method": "vectorized_melt",
        "description": "Replaced .iterrows() loop with vectorized .melt() operation",
        "runtime_seconds": stats["timing"]["duration_seconds"],
        "expected_speedup": "10-100x for LM dictionary (10K rows)",
    }

    # Save Stats
    print_stats_summary(stats)
    save_stats(stats, out_dir)

    update_latest_symlink(out_base / "2.1_Tokenized" / "latest", out_dir)
    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
