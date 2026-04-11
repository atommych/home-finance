"""Parser for CGD (Caixa Geral de Depósitos) bank statements.

Expected PDF text format:
- Header contains: EXTRATO...YYYY/MM
- Transaction area between "CONTA SIMPLES N." and "SALDO FINAL"
- Transaction rows: DD.MM DD.MM DESCRIPTION AMOUNT BALANCE
- European number format: spaces for thousands, period for decimals in dates
- Amounts use period for decimals (e.g., "1 234.56")
"""

import re
from datetime import date
from decimal import Decimal

from app.parsers.base import BankParser, Transaction


class CGDParser(BankParser):
    bank_name = "cgd"

    # Matches: EXTRATO...YYYY/MM to extract the year
    _YEAR_REGEX = re.compile(r"EXTRATO.*?(\d{4})/(\d{2})")

    # Amount pattern: handles "15.60", "1 234.56", "12 345.67"
    _AMT = r"((?:\d{1,3}(?:\s\d{3})*)\.\d{2})"

    # Primary pattern: DD.MM DD.MM DESCRIPTION AMOUNT BALANCE (anchored to start of line)
    _TRX_REGEX = re.compile(
        r"^(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\s+(.*?)\s+"
        r"((?:\d{1,3}(?:\s\d{3})*)\.\d{2})\s+"
        r"((?:\d{1,3}(?:\s\d{3})*)\.\d{2})$"
    )

    # Continuation line: DESCRIPTION AMOUNT BALANCE (no date prefix)
    _CONTINUATION_REGEX = re.compile(
        r"^(.*?)\s+((?:\d{1,3}(?:\s\d{3})*)\.\d{2})\s+((?:\d{1,3}(?:\s\d{3})*)\.\d{2})$"
    )

    # Date-only line: DD.MM DD.MM
    _DATE_ONLY_REGEX = re.compile(r"^(\d\d\.\d\d)\s+(\d\d\.\d\d)$")

    def parse(self, text: str) -> list[Transaction]:
        year = self._extract_year(text)
        cleaned = self._strip_headers_footers(text)
        return self._parse_transactions(cleaned, year)

    def _extract_year(self, text: str) -> int:
        match = self._YEAR_REGEX.search(text)
        if not match:
            raise ValueError("Could not find year in PDF text (expected EXTRATO...YYYY/MM)")
        return int(match.group(1))

    def _strip_headers_footers(self, text: str) -> str:
        text = re.sub(r"[\S\s]*?CONTA SIMPLES N\.", "", text)
        text = re.sub(r"SALDO FINAL[\S\s]*", "", text)
        return text

    def _parse_amount(self, raw: str) -> Decimal:
        """Parse amount like '1 234.56' or '234.56' into Decimal."""
        return Decimal(raw.replace(" ", ""))

    def _parse_date(self, raw: str, year: int) -> date:
        """Parse date like 'DD.MM' into a date object."""
        parts = raw.strip().split(".")
        day = int(parts[0])
        month = int(parts[1])
        return date(year, month, day)

    def _parse_transactions(self, text: str, year: int) -> list[Transaction]:
        transactions: list[Transaction] = []
        current_date: date | None = None

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Try primary pattern: full transaction line with date
            match = self._TRX_REGEX.search(line)
            if match:
                trx_date_raw = match.group(1)
                current_date = self._parse_date(trx_date_raw, year)
                description = match.group(3).strip()
                trx_type = description.split(" ")[0] if description else ""
                description = " ".join(description.split(" ")[1:]) if " " in description else ""
                amount = self._parse_amount(match.group(4))
                balance = self._parse_amount(match.group(5))

                transactions.append(
                    Transaction(
                        date=current_date,
                        description=description,
                        trx_type=trx_type,
                        amount=amount,
                        balance=balance,
                    )
                )
                continue

            # Try date-only line
            date_match = self._DATE_ONLY_REGEX.search(line)
            if date_match:
                current_date = self._parse_date(date_match.group(2), year)
                continue

            # Try continuation line (description + amount + balance, no date)
            cont_match = self._CONTINUATION_REGEX.search(line)
            if cont_match and current_date:
                description = cont_match.group(1).strip()
                trx_type = description.split(" ")[0] if description else ""
                description = " ".join(description.split(" ")[1:]) if " " in description else ""
                amount = self._parse_amount(cont_match.group(2))
                balance = self._parse_amount(cont_match.group(3))

                transactions.append(
                    Transaction(
                        date=current_date,
                        description=description,
                        trx_type=trx_type,
                        amount=amount,
                        balance=balance,
                    )
                )

        return transactions
