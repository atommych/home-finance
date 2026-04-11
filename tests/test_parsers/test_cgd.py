"""Tests for CGD bank statement parser."""

from datetime import date
from decimal import Decimal

from app.parsers.cgd import CGDParser


class TestCGDParser:
    def setup_method(self):
        self.parser = CGDParser()

    def test_parse_extracts_year(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        assert all(t.date.year == 2024 for t in transactions)

    def test_parse_finds_all_transactions(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        assert len(transactions) == 6

    def test_parse_first_transaction(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        first = transactions[0]
        assert first.date == date(2024, 1, 1)
        assert first.trx_type == "COMPRA"
        assert "MERCADONA" in first.description
        assert first.amount == Decimal("15.60")
        assert first.balance == Decimal("12345.67")

    def test_parse_transfer_transaction(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        transfer = transactions[1]
        assert transfer.trx_type == "TRF"
        assert "JOAO SILVA" in transfer.description
        assert transfer.amount == Decimal("50.00")

    def test_parse_amount_with_thousands_separator(self, cgd_statement_text: str):
        """Test that amounts like '12 345.67' are parsed correctly."""
        transactions = self.parser.parse(cgd_statement_text)
        first = transactions[0]
        assert first.balance == Decimal("12345.67")

    def test_parse_rent_transaction(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        rent = transactions[4]
        assert rent.trx_type == "TRF"
        assert "RENDA" in rent.description
        assert rent.amount == Decimal("650.00")

    def test_parse_raises_on_missing_year(self):
        with_no_year = "CONTA SIMPLES N. 123\nsome data\nSALDO FINAL"
        import pytest

        with pytest.raises(ValueError, match="Could not find year"):
            self.parser.parse(with_no_year)

    def test_parse_empty_text_returns_empty_list(self):
        text = "EXTRATO COMBINADO 2024/01\nCONTA SIMPLES N. 123\nSALDO FINAL"
        transactions = self.parser.parse(text)
        assert transactions == []

    def test_extract_year(self):
        assert self.parser._extract_year("EXTRATO COMBINADO 2024/01") == 2024
        assert self.parser._extract_year("EXTRATO COMBINADO 2023/12") == 2023

    def test_parse_amount(self):
        assert self.parser._parse_amount("1 234.56") == Decimal("1234.56")
        assert self.parser._parse_amount("234.56") == Decimal("234.56")
        assert self.parser._parse_amount("12 345.67") == Decimal("12345.67")


class TestCGDParserEdgeCases:
    def setup_method(self):
        self.parser = CGDParser()

    def test_transaction_to_dict(self, cgd_statement_text: str):
        transactions = self.parser.parse(cgd_statement_text)
        d = transactions[0].to_dict()
        assert d["date"] == "2024-01-01"
        assert d["trx_type"] == "COMPRA"
        assert d["amount"] == "15.60"
