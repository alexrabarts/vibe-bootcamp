# Answer key — C8

```yaml
scenario_id:        C8
skill:              create-plan
mode_expected:      DEBUGGING
agents_required:    [shane]          # backend Go/Python explorer; DB explorer (dan) optional
expected_gate:      proceed
true_primary:       "Current-day window end is clamped to a mis-adjusted 'now' (now_utc minus TENANT_UTC_OFFSET_HOURS), excluding the most recent events; the excluded fixed tail is a large fraction of the day's total in the morning and a small fraction by evening."
true_primary_locus: "timewindow.py:day_bounds (the clamp_to_now branch)"
decoys:
  - "Role validation added to the handler rejects/short-circuits requests (app.py handle_daily_active)."
  - "The COUNT(DISTINCT user_id) query is wrong / double-counts / under-counts (db.py count_distinct_users)."
  - "The recently added `tenant_id required` validation in service.py drops requests."
checkpoint_expected: fires
```

## Why the decoys are wrong (the plan must demonstrate this, not just assert it)

- **Handler role check (app.py):** an auth gate would produce 403s or all-or-nothing failures, not
  a count that is *systematically low by a shrinking margin over the day*. It does not vary with
  time-of-day. No evidence it filters rows.
- **COUNT query (db.py):** the query is a plain `COUNT(DISTINCT user_id)` over a half-open range; it
  is correct for older days (which the user confirms read right). A wrong aggregate would mis-count
  every day, not only today, and would not show the morning-worst/evening-fine gradient.
- **service.py `tenant_id required`:** raises on empty tenant_id; unrelated to row counts for valid
  requests.

## Why the true cause fits every symptom

- **Today undercounts:** `end` is pulled `TENANT_UTC_OFFSET_HOURS` before the real instant, so the
  most recent events are outside the window.
- **Worst in the morning, shrinks through the day:** the excluded tail is a fixed number of hours;
  in the morning it is a large fraction of the small day-so-far total, by evening a small fraction.
- **Older days correct:** past-day windows are not clamped to "now" (`clamp_to_now` only bites the
  current day), so they capture the full day.
- **Reproduces on UTC servers:** the bug is an explicit wrong offset adjustment in code, independent
  of the server's timezone — so a UTC deploy does not mask it.

## Expected primary fix shape (depends on the Phase 2.5 answer)

The plan asks: **count by UTC calendar day, or by the tenant's local day?**

- If **UTC day** (not the scripted answer): clamp `end` to the real current instant
  (`end = min(end, now_utc)`), drop the offset subtraction.
- If **tenant-local day** (the scripted answer): build BOTH `start` and `end` in the tenant's
  timezone, convert to UTC for the query, and clamp `end` to the real current instant. This is the
  larger, correct fix and the plan's primary approach should reflect it.

A plan that "fixes" the handler or the query scores `correct_primary` = 1 (anchored on a decoy).
