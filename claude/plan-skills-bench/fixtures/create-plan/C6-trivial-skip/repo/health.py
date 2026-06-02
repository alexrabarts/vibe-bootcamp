"""Upstream health checks."""

import requests

from config import HEALTHCHECK_TIMEOUT_SECONDS


def check_upstream(url):
    """Return True if the upstream responds 200 within the configured timeout."""
    try:
        resp = requests.get(url, timeout=HEALTHCHECK_TIMEOUT_SECONDS)
        return resp.status_code == 200
    except requests.Timeout:
        return False
