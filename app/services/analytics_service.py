"""Service for dashboard analytics and aggregations."""

import pandas as pd


def monthly_expenses_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Group transactions by category and month, sum amounts.

    Args:
        df: DataFrame with 'date', 'category', and 'amount' columns.

    Returns:
        DataFrame with 'month', 'category', 'amount' columns.
    """
    if df.empty:
        return pd.DataFrame(columns=["month", "category", "amount"])

    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    return df.groupby(["category", "month"])["amount"].sum().reset_index()


def summary_stats(df: pd.DataFrame) -> dict:
    """Calculate summary statistics for a transactions DataFrame.

    Returns:
        Dict with total_expenses, total_income, savings, top_category, transaction_count.
    """
    if df.empty:
        return {
            "total_expenses": 0.0,
            "total_income": 0.0,
            "savings": 0.0,
            "top_category": "N/A",
            "transaction_count": 0,
        }

    amounts = df["amount"].astype(float)
    total_expenses = amounts.sum()
    # Income detection: credits are typically categorized differently or negative
    # For now, treat all parsed amounts as expenses
    top_category = (
        df.groupby("category")["amount"].sum().idxmax() if "category" in df.columns else "N/A"
    )

    return {
        "total_expenses": round(total_expenses, 2),
        "total_income": 0.0,
        "savings": 0.0,
        "top_category": top_category,
        "transaction_count": len(df),
    }
