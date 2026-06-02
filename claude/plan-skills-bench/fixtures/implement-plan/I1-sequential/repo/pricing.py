"""Pricing helpers (to be implemented)."""


def apply_discount(price, pct):
    """Return ``price`` with ``pct`` percent removed.

    e.g. ``apply_discount(100, 10) == 90.0``.
    """
    raise NotImplementedError


def cart_total(items, discount_pct):
    """Sum the item prices, then apply ``discount_pct`` via ``apply_discount``.

    ``items`` is a list of numeric prices.
    """
    raise NotImplementedError
