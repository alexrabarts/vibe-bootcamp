"""Day-window helper.

Event timestamps (`events.event_ts`) are stored in UTC.
"""

from datetime import datetime, timedelta, timezone

# Configured for the primary tenant (e.g. AEST, UTC+10).
TENANT_UTC_OFFSET_HOURS = 10


def day_bounds(day=None, clamp_to_now=True):
    """Return the half-open ``[start, end)`` window for a single day, in UTC.

    For past days the full day is returned. For the current day the window is
    clamped so we don't count into the future.
    """
    if day is None:
        day = datetime.now(timezone.utc).date()

    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    if clamp_to_now:
        # Intent: express "now" against the tenant's local day. But event_ts is
        # stored in UTC, and this subtracts the tenant offset from the current
        # UTC instant — so `end` lands TENANT_UTC_OFFSET_HOURS *before* the real
        # current instant, and the most recent events fall outside the window.
        now_utc = datetime.now(timezone.utc)
        end = min(end, now_utc - timedelta(hours=TENANT_UTC_OFFSET_HOURS))

    return start, end
