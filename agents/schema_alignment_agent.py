
import pandas as pd
from rapidfuzz import fuzz, process

def generate_column_mapping(datasets):
    """
    Input: list of pandas DataFrames
    Output: dict mapping standardized column names to their variants
    """
    all_columns = []
    for df in datasets:
        all_columns.extend(df.columns.tolist())

    unique_columns = list(set(all_columns))
    mapping = {}
    threshold = 80  # fuzzy match threshold

    for col in unique_columns:
        best_match, score = process.extractOne(col, mapping.keys(), scorer=fuzz.token_sort_ratio)
        if score and score > threshold:
            mapping[best_match].append(col)
        else:
            mapping[col.lower()] = [col]

    return mapping

def standardize_units(df, unit_map):
    """
    Convert units in the DataFrame based on a provided unit mapping.
    Example: {'temperature': ('F', 'C')}
    """
    for col, (from_unit, to_unit) in unit_map.items():
        if col in df.columns and from_unit == 'F' and to_unit == 'C':
            df[col] = (df[col] - 32) * 5.0/9.0
    return df

def preview_column_mapping(mapping):
    print("\nUnified Schema Mapping:")
    for unified_col, variants in mapping.items():
        print(f"{unified_col} ⟶ {variants}")

def align_and_merge_datasets(datasets):
    """
    Align columns and merge multiple DataFrames into one.
    """
    column_map = generate_column_mapping(datasets)
    aligned_dfs = []

    for df in datasets:
        renamed = {}
        for std_col, variants in column_map.items():
            for var in variants:
                if var in df.columns:
                    renamed[var] = std_col
        aligned_dfs.append(df.rename(columns=renamed))

    return pd.concat(aligned_dfs, ignore_index=True), column_map
