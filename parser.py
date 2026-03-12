"""
Parse amount and optional currency from user message.
Examples: "12", "12.50", "50 EUR", "100 USD"
"""
import re
from typing import Optional, Tuple

# Default currency if not specified
DEFAULT_CURRENCY = "EUR"

# Common currency codes (case-insensitive)
CURRENCY_PATTERN = re.compile(
    r"^\s*([\d\s.,]+)\s*(EUR|USD|GBP|PLN|CHF)?\s*$",
    re.IGNORECASE,
)


def parse_amount(message_text: str) -> Optional[Tuple[float, str]]:
    """
    Parse amount and currency from message.
    Returns (amount, currency) or None if invalid.
    """
    if not message_text or not message_text.strip():
        return None

    text = message_text.strip()
    # Try "50 EUR" / "100 USD" style first
    m = CURRENCY_PATTERN.match(text)
    if m:
        amount_str = m.group(1).replace(" ", "").replace(",", ".")
        currency = (m.group(2) or DEFAULT_CURRENCY).upper()
        try:
            amount = float(amount_str)
            if amount > 0:
                return (amount, currency)
        except ValueError:
            pass

    # Try plain number
    amount_str = text.replace(",", ".").strip()
    try:
        amount = float(amount_str)
        if amount > 0:
            return (amount, DEFAULT_CURRENCY)
    except ValueError:
        pass

    return None
