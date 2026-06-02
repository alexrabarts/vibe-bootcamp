"""Service configuration."""

# Timeout for upstream health probes, in seconds.
# BUG: 1 ms is far too short — every probe times out before any upstream can
# respond. Should be a few seconds (e.g. 5).
HEALTHCHECK_TIMEOUT_SECONDS = 0.001
