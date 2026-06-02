"""Business logic: resolve the day window and ask the data layer for the count."""

from timewindow import day_bounds
from db import count_distinct_users


def daily_active_users(tenant_id):
    # Recent change: tightened input validation. (Suspected by the team.)
    if not tenant_id:
        raise ValueError("tenant_id is required")

    start, end = day_bounds()  # window for "today"
    return count_distinct_users(tenant_id, start, end)
