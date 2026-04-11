"""Tests for analytics service."""

import pandas as pd

from app.services.analytics_service import monthly_expenses_by_category, summary_stats


class TestMonthlyExpensesByCategory:
    def test_groups_by_category_and_month(self):
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-15", "2024-02-01"],
                "category": ["Alimentacao", "Alimentacao", "Transporte"],
                "amount": [100.0, 50.0, 30.0],
            }
        )
        result = monthly_expenses_by_category(df)
        assert len(result) == 2  # 2 unique (category, month) combos
        jan_food = result[(result["category"] == "Alimentacao") & (result["month"] == "2024-01")]
        assert jan_food["amount"].iloc[0] == 150.0

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["date", "category", "amount"])
        result = monthly_expenses_by_category(df)
        assert result.empty


class TestSummaryStats:
    def test_calculates_stats(self):
        df = pd.DataFrame(
            {
                "amount": [100.0, 50.0, 30.0],
                "category": ["Alimentacao", "Alimentacao", "Transporte"],
            }
        )
        stats = summary_stats(df)
        assert stats["total_expenses"] == 180.0
        assert stats["transaction_count"] == 3
        assert stats["top_category"] == "Alimentacao"

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["amount", "category"])
        stats = summary_stats(df)
        assert stats["total_expenses"] == 0.0
        assert stats["transaction_count"] == 0
        assert stats["top_category"] == "N/A"
