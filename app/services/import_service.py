"""Service for handling file uploads and PDF parsing."""

import pandas as pd

from app.parsers import get_parser
from app.parsers.base import BankParser, Transaction


def parse_uploaded_pdf(pdf_bytes: bytes, bank_name: str) -> list[Transaction]:
    """Parse an uploaded PDF file into transactions.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF file.
        bank_name: Bank identifier (e.g., 'cgd').

    Returns:
        List of parsed transactions.
    """
    parser = get_parser(bank_name)
    text = BankParser.extract_pdf_text(pdf_bytes)
    return parser.parse(text)


def transactions_to_dataframe(transactions: list[Transaction]) -> pd.DataFrame:
    """Convert a list of Transaction objects to a pandas DataFrame."""
    if not transactions:
        return pd.DataFrame(columns=["date", "description", "trx_type", "amount", "balance"])

    return pd.DataFrame([t.to_dict() for t in transactions]).assign(
        date=lambda df: pd.to_datetime(df["date"]),
        amount=lambda df: df["amount"].astype(float),
        balance=lambda df: df["balance"].astype(float),
    )
