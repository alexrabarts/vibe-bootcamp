# analytics-service (fixture)

Tiny slice of an analytics service exposing Daily Active Users (DAU).

## Reported bug

DAU for the **current day** reads lower than reality. Yesterday and older days check out against
raw event counts. The gap is **worst in the morning and shrinks through the day** — by late evening
it's nearly right. Runs on **UTC servers**; staging (also UTC) reproduces it.

Two changes landed around when reports started:
- role validation added to the HTTP handler (`app.py`)
- the `COUNT` query was "tightened" (`db.py`)

## Layers (entry point -> data)

- `app.py`       — HTTP handler (auth, request parsing)
- `service.py`   — business logic; computes the day window, calls the data layer
- `timewindow.py`— helper that builds the `[start, end)` window for a day
- `db.py`        — the SQL query; `events.event_ts` is stored in **UTC**
