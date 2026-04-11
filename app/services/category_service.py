"""Service for transaction categorization."""

import re

import pandas as pd

# Default categories with colors for charts
DEFAULT_CATEGORIES = [
    {"name": "Alimentacao", "color": "#FF6B6B"},
    {"name": "Transporte", "color": "#4ECDC4"},
    {"name": "Lazer", "color": "#45B7D1"},
    {"name": "Arrendamento", "color": "#96CEB4"},
    {"name": "Saude", "color": "#FFEAA7"},
    {"name": "Educacao", "color": "#DDA0DD"},
    {"name": "Outros", "color": "#95A5A6"},
]


def normalize_description(description: str) -> str:
    """Normalize transaction description for matching.

    Removes 4-digit year prefixes and collapses whitespace.
    """
    cleaned = re.sub(r"\d{4}\s", "", description)
    return re.sub(r"\s+", " ", cleaned).strip()


def apply_category_rules(df: pd.DataFrame, rules: list[dict[str, str]]) -> pd.DataFrame:
    """Apply category rules to a transactions DataFrame.

    Args:
        df: DataFrame with a 'description' column.
        rules: List of dicts with 'match_pattern' and 'category' keys.

    Returns:
        DataFrame with a 'category' column added.
    """
    df = df.copy()
    df["normalized_desc"] = df["description"].apply(normalize_description)
    df["category"] = "Outros"

    for rule in rules:
        pattern = rule["match_pattern"].lower()
        mask = df["normalized_desc"].str.lower().str.contains(pattern, regex=False)
        df.loc[mask & (df["category"] == "Outros"), "category"] = rule["category"]

    df = df.drop(columns=["normalized_desc"])
    return df
