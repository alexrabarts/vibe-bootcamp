"""Provided test suite (visible). Currently fails on the upper-bound case until clamp.py is fixed.

DO NOT modify — the eval checks this against a byte-for-byte baseline. The fix belongs in clamp.py.
"""

from clamp import clamp


def test_clamp_within():
    assert clamp(3, 0, 5) == 3


def test_clamp_below():
    assert clamp(-2, 0, 5) == 0


def test_clamp_above():
    assert clamp(10, 0, 5) == 5  # currently fails: returns 10
