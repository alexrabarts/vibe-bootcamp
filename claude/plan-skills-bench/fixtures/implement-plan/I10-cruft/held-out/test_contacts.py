"""Authoritative acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from contacts import format_phone, normalize_email


def test_format_phone():
    assert format_phone("1234567890") == "(123) 456-7890"


def test_normalize_email_still_works():
    # Cleaning up the debug print must not change normalize_email's behavior.
    assert normalize_email("  Foo@Bar.COM ") == "foo@bar.com"
