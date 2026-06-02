"""Combined revenue-by-active-user report (to be implemented).

Depends on BOTH users_source and orders_source.
"""

from users_source import active_user_ids
from orders_source import order_totals_by_user


def active_user_revenue():
    """Return ``{active user_id -> total order amount}``.

    Only active users appear; a user with no orders contributes ``0.0``.
    """
    raise NotImplementedError
