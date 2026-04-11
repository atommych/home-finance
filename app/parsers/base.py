from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Transaction:
    date: date
    description: str
    trx_type: str
    amount: Decimal
    balance: Decimal

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "trx_type": self.trx_type,
            "amount": str(self.amount),
            "balance": str(self.balance),
        }


class BankParser(ABC):
    """Base class for bank statement parsers.

    Parsers are pure functions: text in, structured data out.
    No I/O, no database calls.
    """

    bank_name: str

    @abstractmethod
    def parse(self, text: str) -> list[Transaction]:
        """Parse extracted PDF text into a list of transactions."""
        ...

    @staticmethod
    def extract_pdf_text(pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using pypdf."""
        from io import BytesIO

        from pypdf import PdfReader

        reader = PdfReader(BytesIO(pdf_bytes))
        return "".join(page.extract_text() or "" for page in reader.pages)
