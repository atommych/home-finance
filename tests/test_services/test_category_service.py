"""Tests for category service."""

import pandas as pd

from app.services.category_service import apply_category_rules, normalize_description


class TestNormalizeDescription:
    def test_removes_year_prefix(self):
        assert normalize_description("2024 MERCADONA PORTO") == "MERCADONA PORTO"

    def test_collapses_whitespace(self):
        assert normalize_description("MERCADONA   PORTO") == "MERCADONA PORTO"

    def test_strips_whitespace(self):
        assert normalize_description("  MERCADONA PORTO  ") == "MERCADONA PORTO"


class TestApplyCategoryRules:
    def test_applies_matching_rule(self):
        df = pd.DataFrame({"description": ["MERCADONA PORTO", "UBER TRIP"]})
        rules = [
            {"match_pattern": "mercadona", "category": "Alimentacao"},
            {"match_pattern": "uber", "category": "Transporte"},
        ]
        result = apply_category_rules(df, rules)
        assert result.iloc[0]["category"] == "Alimentacao"
        assert result.iloc[1]["category"] == "Transporte"

    def test_unmatched_gets_outros(self):
        df = pd.DataFrame({"description": ["UNKNOWN TRANSACTION"]})
        result = apply_category_rules(df, [])
        assert result.iloc[0]["category"] == "Outros"

    def test_case_insensitive_matching(self):
        df = pd.DataFrame({"description": ["Mercadona Porto"]})
        rules = [{"match_pattern": "MERCADONA", "category": "Alimentacao"}]
        result = apply_category_rules(df, rules)
        assert result.iloc[0]["category"] == "Alimentacao"

    def test_first_matching_rule_wins(self):
        df = pd.DataFrame({"description": ["FARMACIA MERCADONA"]})
        rules = [
            {"match_pattern": "farmacia", "category": "Saude"},
            {"match_pattern": "mercadona", "category": "Alimentacao"},
        ]
        result = apply_category_rules(df, rules)
        assert result.iloc[0]["category"] == "Saude"
