"""Data access layer. ``events.event_ts`` is stored in UTC."""


def count_distinct_users(tenant_id, start, end):
    """Count distinct users with at least one event in the half-open window.

    Recent change: the team "tightened" this to DISTINCT. (Suspected.) The range
    is half-open ``[start, end)`` and the bounds are passed straight through; this
    layer does no timezone normalization of its own.
    """
    sql = (
        "SELECT COUNT(DISTINCT user_id) FROM events "
        "WHERE tenant_id = ? AND event_ts >= ? AND event_ts < ?"
    )
    return _execute_scalar(sql, [tenant_id, start, end])


def _execute_scalar(sql, params):
    # Stubbed for the fixture; a real connection/cursor lives here in production.
    raise NotImplementedError("wired to the warehouse in production")
