"""Shared formatting helpers."""


def format_currency(amount, currency):
    """Format a monetary amount with its currency symbol.

    build_report in reports.py duplicates this logic inline instead of calling it.
    """
    symbol = "$" if currency == "USD" else currency + " "
    return f"{symbol}{amount:,.2f}"
