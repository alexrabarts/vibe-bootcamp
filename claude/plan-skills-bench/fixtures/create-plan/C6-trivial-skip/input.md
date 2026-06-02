Our health check endpoint always reports upstreams as down, even when they're clearly up and
responding in a browser. It started right after a config change. This looks like a one-liner to me
— can you confirm the cause and plan the fix? See config.py and health.py.
