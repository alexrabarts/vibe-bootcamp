"""Contact formatting helpers."""

import json  # unused import (cruft)


def normalize_email(email):
    print("DEBUG normalize_email:", email)  # leftover debug logging (cruft)
    return email.strip().lower()


def _legacy_format_phone(number):
    # Dead code: superseded old format, not called anywhere.
    return number[:3] + "-" + number[3:]


def format_phone(number):
    """Format a 10-digit string as ``(XXX) XXX-XXXX``. (To be implemented.)"""
    # old approach, kept for reference:
    # return _legacy_format_phone(number)
    raise NotImplementedError
