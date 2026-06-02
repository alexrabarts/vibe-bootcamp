"""Tests the implementer wrote (captured alongside the change)."""

from pricing import apply_discount, cart_total


def test_apply_discount():
    assert apply_discount(100, 10) == 90.0
    assert apply_discount(50, 0) == 50.0


def test_cart_total():
    assert cart_total([10, 20, 30], 10) == 54.0
    assert cart_total([], 10) == 0.0
