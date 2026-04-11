from app.parsers.base import BankParser, Transaction
from app.parsers.cgd import CGDParser

PARSERS: dict[str, type[BankParser]] = {
    "cgd": CGDParser,
}


def get_parser(bank_name: str) -> BankParser:
    parser_cls = PARSERS.get(bank_name.lower())
    if not parser_cls:
        raise ValueError(f"Unknown bank: {bank_name}. Available: {list(PARSERS.keys())}")
    return parser_cls()


__all__ = ["BankParser", "Transaction", "get_parser", "PARSERS"]
