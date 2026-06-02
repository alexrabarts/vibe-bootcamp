"""Pricing helpers."""


def apply_discount(price, pct):
    """Return ``price`` with ``pct`` percent removed."""
    return round(price * (1 - pct / 100), 2)


def cart_total(items, discount_pct):
    """Sum the item prices, then apply ``discount_pct`` via ``apply_discount``."""
    return apply_discount(sum(items), discount_pct)
