"""HTTP layer for the analytics service."""

from service import daily_active_users

ALLOWED_ROLES = ("admin", "analyst")


def handle_daily_active(request):
    """GET /metrics/daily-active?tenant_id=...

    Recent change: role validation was added here. (Suspected by the team.)
    """
    role = request.headers.get("X-Role")
    if role not in ALLOWED_ROLES:
        return 403, {"error": "forbidden"}

    tenant_id = request.args.get("tenant_id")
    count = daily_active_users(tenant_id)
    return 200, {"daily_active_users": count}
