# Fix: DAU under-counts the current day (timewindow clamp drops recent events)

**Created:** 2026-06-02
**Mode:** DEBUGGING (Root Cause Analysis)
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

The current-day Daily Active Users (DAU) count reads low because `timewindow.day_bounds()`
clamps the window's upper bound to `now_utc - TENANT_UTC_OFFSET_HOURS` (10h), dropping the most
recent 10 hours of events. The fix clamps to the real `now`, retires the dead offset constant, and
makes `now` injectable (one instant drives both the date and the clamp — fixing a latent
midnight-rollover race and making the morning/evening behaviour unit-testable). The team's two
suspects (role validation in `app.py`, `COUNT(DISTINCT)` in `db.py`) are confirmed **red herrings**.

## Context

### Original Request
> "Daily Active Users" reads lower than reality for the **current day**. Yesterday and older days
> check out against raw event counts. The gap is worst first thing in the morning and shrinks as the
> day goes on; by late evening it's almost right. UTC servers; staging (also UTC) reproduces it.
> Suspects: recently added role validation to the handler, and a "tightened" COUNT query. DAU
> endpoint files: `app.py`, `service.py`, `db.py`, `timewindow.py`.

### Investigation Summary
Execution path traced outer → inner:

```
app.py:handle_daily_active   role gate (403), parse tenant_id
  -> service.py:daily_active_users   validate tenant_id, call day_bounds()
       -> timewindow.py:day_bounds()   build [start, end) UTC window for "today"
       -> db.py:count_distinct_users   SELECT COUNT(DISTINCT user_id)
                                        WHERE tenant_id=? AND event_ts >= ? AND event_ts < ?
```

Root cause is at **`timewindow.py:30`**:

```python
end = min(end, now_utc - timedelta(hours=TENANT_UTC_OFFSET_HOURS))  # offset = 10
```

The current-day window becomes `[midnight_UTC, now − 10h)`. Effects, matched symptom-by-symptom:

| Symptom | Mechanism |
|---|---|
| Reads low | Users whose only events today are in the last 10h are excluded. |
| **Worst in the morning** | From 00:00–10:00 UTC, `now − 10h` lands in *yesterday*, so `end < start` → half-open window is empty → **DAU = 0**. |
| Shrinks through the day | After 10:00 UTC the window is valid but lags real-time by 10h; the missing 10h tail contributes progressively fewer *new* distinct users, so the gap narrows. |
| Past days correct | For a finished day, `end` (its midnight) is already < `now − 10h`, so `min()` keeps the full day — clamp is a no-op. |
| UTC servers / staging reproduce | Deterministic constant offset, not environment- or wall-clock-dependent. |

### Approach
Adopt **UTC calendar-day** semantics (see Resolved Decisions). The buggy clamp was a botched attempt
at tenant-*local*-day semantics (the `TENANT_UTC_OFFSET_HOURS = 10` / AEST constant): it subtracted
the tenant offset from a UTC instant instead of shifting the whole window. We delete that machinery
rather than "fix" the offset math, because (a) you validate "reality" against UTC raw event counts,
(b) past UTC days already read correct, and (c) a single **global** offset constant is incompatible
with a per-`tenant_id` endpoint.

## Resolved Decisions

The Phase 2.5 checkpoint was **dismissed without a selection**, so the two load-bearing decisions
default to their recommended answers and are recorded here as **explicit, overridable assumptions**.
Each names exactly where to revisit if wrong.

### Decision 1: Meaning of "today" — UTC day vs tenant-local day
**Question:** Should DAU buckets follow the UTC calendar day or the tenant's local calendar day?
**Default answer:** **UTC calendar day.**
**Why:** Validation basis is UTC raw event counts; past UTC days already correct; the single global
offset cannot be right for a multi-tenant endpoint.
**Impact on plan:** Phase 1 removes the offset clamp and the constant. **Under this option, only the
current-day read changes — every past day's number is bit-for-bit unchanged** (they are already
UTC-day windows).
**Revisit trigger:** If product defines DAU as a *tenant-local-day* metric, this fix is clean but
*wrong*. See "Alternative Approaches → Approach 2" for the local-day design (per-tenant IANA zone via
`zoneinfo`, shift both bounds, DST-aware). That option *would* change historical numbers.

### Decision 2: Is DAU persisted, or computed live?
**Question:** Are daily DAU values ever cached/snapshotted, or always computed live from `events`?
**Default answer:** **Computed live** (consistent with the on-demand query in `db.py`).
**Impact on plan:** No backfill/restatement needed — fixing the window retroactively corrects all
reads. Phase 3 includes a step to **confirm with the warehouse schema / DBA** that no snapshot or
rollup table exists. (A code grep cannot prove a warehouse table's absence.)
**Revisit trigger:** If a snapshot/rollup table exists, add an out-of-scope restatement job for the
affected days.

## Alternative Approaches Considered

### Approach 1: UTC calendar day — **SELECTED**
Clamp to `now_utc`; delete the offset constant. Simplest, lowest-risk, changes only current-day
reads. Selected for the reasons in Decision 1.

### Approach 2: Tenant-local calendar day (done correctly) — not selected
Shift **both** bounds to the tenant's local midnight, using a **per-tenant IANA timezone** resolved
via `zoneinfo` (not a fixed hour offset — a fixed +10 breaks at the AEDT/AEST DST transition).
Requires a per-tenant timezone source that may not exist yet, and **changes historical day buckets**.
Reserve for if product confirms local-day semantics. Do **not** ship the existing global-offset form:
it is wrong by construction the moment a second timezone is onboarded.

### Approach 3: Rolling 24-hour window — not selected
`[now − 24h, now)`. A different metric than calendar-day DAU; changes past-day numbers; not what
"DAU" conventionally means. Listed for completeness.

## Implementation Plan

### Phase 1: Fix the window + make `now` injectable

**Goal:** Current-day window ends at the real `now`; remove dead offset machinery; eliminate the
double-`datetime.now()` race; enable frozen-clock tests.

**Estimated Effort:** Small
**Dependencies:** None

**Files to Modify:**
- `timewindow.py`:
  - Replace the clamp `min(end, now_utc - timedelta(hours=TENANT_UTC_OFFSET_HOURS))` with
    `min(end, now)`.
  - Add an injectable `now=None` parameter; compute `now` **once** and use it for **both** the
    default `day` derivation **and** the clamp.
  - Guard tz-awareness: raise a clear error if an injected `now` is naive.
  - Update the module docstring + remove the misleading "tenant local day" comment block
    (lines 25–28); state the UTC-day decision.

**Code to Remove:**
- `timewindow.py`: delete the `TENANT_UTC_OFFSET_HOURS = 10` constant and the unused
  `timedelta`-offset arithmetic (only after the repo-wide grep in Phase 3 confirms no other
  importer).

**Target shape (`timewindow.py`):**
```python
"""Day-window helper.

`events.event_ts` is stored in UTC, and DAU is reported against the UTC
calendar day. (UTC-day chosen over tenant-local-day; revisit if product
requires local-day buckets — see plan.)
"""

from datetime import datetime, timedelta, timezone


def day_bounds(day=None, clamp_to_now=True, now=None):
    """Return the half-open ``[start, end)`` UTC window for a single day.

    Past days return the full day. The current day is clamped to ``now`` so we
    report a live "up to this instant" count and do not count future-dated
    events. ``now`` may be injected (must be tz-aware UTC) to freeze the clock
    in tests; the same instant drives the default ``day`` and the clamp, so
    there is no midnight-rollover race.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        raise ValueError("now must be timezone-aware (UTC)")

    if day is None:
        day = now.date()

    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    if clamp_to_now:
        end = min(end, now)

    return start, end
```

**Acceptance criteria (from review):**
- [ ] A single `now` value feeds **both** `day = now.date()` and `end = min(end, now)` (Wigsy C1).
- [ ] Injected naive `now` is rejected with a clear error (Wigsy W4).
- [ ] `clamp_to_now` retained as a **deliberate** rule: current-day count is "as of `now`" and
      excludes future-dated events (clock skew / scheduled). Documented, not cargo-culted (Eric).

**Verification:** new tests in Phase 2 pass; `day_bounds()` for the current day returns
`end == now`; for any current-day `now`, `start <= end` (never inverted).

---

### Phase 2: Regression tests

**Goal:** Lock in the fix so any re-introduced offset/clamp regression fails loudly.

**Estimated Effort:** Small
**Dependencies:** Phase 1

**Files to Create:**
- `test_timewindow.py` — frozen-clock unit tests against `day_bounds`:
  - **Morning regression (the key lock):** `now = 2026-06-02T03:00Z`, `day=None` →
    assert `start == 2026-06-02T00:00Z`, `end == now`, `start < end`, and window width ≈ 3h.
    *(Old code produced `end < start` here — this test fails loudly on any offset-subtraction
    regression.)* (Wigsy W2/W3 — note `day=None` exercises the default-date path.)
  - **Evening:** `now = 2026-06-02T23:00Z`, `day=None` → `end == now`.
  - **Half-open contract:** assert `end == now` exactly (not merely `start <= end`) (Wigsy W1).
  - **Past day full window:** `day = 2026-06-01`, `now = 2026-06-02T06:00Z` →
    `end == 2026-06-02T00:00Z` (full 24h; clamp is a no-op because `now` is strictly after the day
    end) (Wigsy S4).
  - **`clamp_to_now=False`:** `day = 2026-06-01` → full `[00:00, next-00:00)` regardless of `now`.
  - **Invariant:** for a range of current-day `now` values (00:00–23:59 UTC), `start <= end` always.
  - **tz contract:** passing a naive `now` raises `ValueError` (Wigsy W4).
- `test_service.py` (optional but recommended) — monkeypatch `db.count_distinct_users` to capture
  the bounds; assert `daily_active_users` passes a window whose `end` is `now` (not `now − 10h`),
  and that `tenant_id=""`/`None` still raises `ValueError` (no behaviour change there).

**Files to Modify:** none.

**Note on `db._execute_scalar`:** it is stubbed (`NotImplementedError`), so end-to-end count
assertions are not possible from unit tests; tests target `day_bounds` directly and the service via a
db mock. Real count validation happens in the Phase 3 manual warehouse check.

---

### Phase 3: Coupling-axis audit, cleanup, and scope confirmation

**Goal:** Ensure no sibling metric shares the bug, no dangling reference to the deleted constant, and
no hidden persistence — i.e. don't half-fix a timezone axis (Eric's coupling audit).

**Estimated Effort:** Small
**Dependencies:** Phase 1

**Steps:**
- [ ] Grep the **whole repo** for `TENANT_UTC_OFFSET_HOURS` and `OFFSET` before/after deleting the
      constant — a dangling import is a deploy-time crash. *(Current repo: only `timewindow.py`
      references it; confirm no `.agent/`, config, or env usage was added.)*
- [ ] Check for **sibling time-bucketed metrics** (WAU/MAU, retention, any other endpoint using
      `day_bounds` or its own clamp). If a sibling shares the offset/clamp pattern, fix it in the same
      pass or leave a dated TODO naming exactly what was deferred and why — otherwise analytics become
      internally inconsistent (DAU on UTC-day, WAU on offset-day). *(Current repo has no siblings; this
      is a guard for the real service.)*
- [ ] Update any stale docs/comments implying tenant-local DAU (module docstring handled in Phase 1;
      README is silent on tz semantics — confirm no `.agent/` doc contradicts UTC-day).
- [ ] **Confirm with the warehouse schema / DBA** that no DAU snapshot/rollup/cache table exists
      (Decision 2). If one does, file an out-of-scope restatement task for the bug-affected days.

**Files to Modify:** docs/comments only (if any stale references found).

---

## Out of Scope (separate tickets — do NOT scope-creep into this fix)

These were reviewed and confirmed **not** the cause of the under-count, but are worth tracking:

- **`app.py` X-Role trust model:** `X-Role` is a client-supplied header trusted verbatim — any caller
  can send `X-Role: admin`. This is authorization-by-self-assertion and is only safe if a trusted
  upstream gateway injects/overwrites the header and the app is not directly reachable. File a ticket:
  *"verify X-Role is gateway-injected and unspoofable."* (Does not affect counts — a 403 returns no
  number.)
- **Role check case-sensitivity:** `"Admin"` → 403 (fail-closed, so not a security hole; a UX footgun
  only if clients vary casing). Leave as-is.
- **`COUNT(DISTINCT user_id)`** (`db.py`): correct DAU semantics and parameterized/injection-safe.
  **No change.**

## Testing Strategy

### Unit Tests
- `test_timewindow.py`: morning regression, evening, half-open `end == now`, past-day full window,
  `clamp_to_now=False`, `start <= end` invariant sweep, naive-`now` rejection.
- `test_service.py` (optional): bounds passed through with `end == now`; `tenant_id` validation
  unchanged.

### Manual Testing
1. Freeze/simulate `now = today 06:00 UTC`: endpoint/`day_bounds` returns `end == 06:00`, window not
   inverted, DAU > 0 (was 0).
2. Compare current-day endpoint output against a raw `COUNT(DISTINCT user_id)` over
   `[00:00 UTC, now)` from the warehouse — should now match.
3. Confirm a past day (e.g. yesterday) returns the **same** number as before the fix (no regression).

## Risks & Mitigations

### Risk 1: UTC-day is the wrong metric (product wanted tenant-local-day)
**Likelihood:** Low–Medium · **Impact:** High
**Mitigation:** Recorded as Decision 1 with a concrete revisit trigger and a fully-specified local-day
fallback (Approach 2). This is precisely what the dismissed Phase 2.5 checkpoint would have settled —
confirm with product before/at implementation if there's any doubt.
**Rollback:** Single-function change; revert `timewindow.py` and switch to Approach 2.

### Risk 2: Hidden DAU persistence needs backfill
**Likelihood:** Low · **Impact:** Medium
**Mitigation:** Phase 3 warehouse/DBA confirmation step before declaring "no backfill."

### Risk 3: Visible jump in current-day DAU after deploy
**Likelihood:** High (expected) · **Impact:** Low
**Mitigation:** Communicate to stakeholders that the morning `0`→real and the +10h-tail correction are
*the fix*, not a new anomaly.

### Risk 4: Partial refactor reintroduces the midnight race
**Likelihood:** Low · **Impact:** Medium
**Mitigation:** Acceptance criterion + test that one `now` feeds both `day` and the clamp (Wigsy C1/W3).

### Risk 5: Future-dated events silently dropped by the clamp
**Likelihood:** Low · **Impact:** Low
**Mitigation:** Documented as an intentional "as-of-now" rule. If future-dated events should count,
drop the clamp (then `event_ts < midnight_tomorrow` bounds the current day naturally).

## Verification Steps

1. **Run tests:** `python -m pytest test_timewindow.py test_service.py` → all pass; the morning case
   asserts `end == now` and `start < end`.
2. **Manual window check:** `day_bounds(now=<06:00 UTC>)` → `(00:00, 06:00)`, not inverted, not
   `now − 10h`.
3. **Count parity:** current-day endpoint vs raw warehouse `COUNT(DISTINCT user_id)` over
   `[00:00 UTC, now)` — match.
4. **Regression:** past-day numbers unchanged vs pre-fix.
5. **Grep:** no remaining references to `TENANT_UTC_OFFSET_HOURS`.

## Success Criteria

- [ ] All unit tests pass (incl. the morning `end == now` regression lock).
- [ ] Current-day DAU matches raw UTC `[00:00, now)` distinct-user count.
- [ ] Past-day DAU numbers are unchanged.
- [ ] `day_bounds` never returns an inverted window for any current-day `now`.
- [ ] A single `now` instant drives both the date and the clamp (no midnight race).
- [ ] `TENANT_UTC_OFFSET_HOURS` and its arithmetic fully removed; no dangling references.
- [ ] Warehouse/DBA confirmed no DAU snapshot table (or backfill task filed).
- [ ] No dead code, unused imports, or stale tenant-local-day comments remain.
- [ ] Out-of-scope X-Role ticket filed.

## Assumptions

- **UTC calendar-day** is the desired DAU semantic (Decision 1).
- DAU is **computed live**; no persisted snapshots need restatement (Decision 2).
- Excluding future-dated events from the current day (the retained clamp) is acceptable.
- The `events` warehouse table stores `event_ts` in UTC (per `db.py` / README).

**If any assumption is invalid, revisit this plan before implementation.**

## Review Feedback Addressed

### Critical
- **Eric — UTC-day vs local-day is a product decision answered by default.** Elevated to Risk 1 /
  Decision 1 with a concrete revisit trigger and a fully-specified local-day fallback (Approach 2:
  per-tenant IANA zone, both bounds shifted, DST-aware). Corrected his note: under the **chosen
  UTC-day** option, past-day numbers are unchanged (only the local-day option redefines history).
- **Wigsy C1 — single `now` must feed both `day` and the clamp.** Added as a Phase 1 acceptance
  criterion + a `day=None` frozen-clock test (W3).

### Concerns / Warnings
- **Clamp drops future-dated events (Eric / Wigsy W1):** made a deliberate, documented "as-of-now"
  rule; Risk 5 records the alternative.
- **Tests must lock the regression (Wigsy W2):** morning case asserts `end == now` and width ≈ 3h —
  fails loudly on the old code.
- **tz-awareness (Wigsy W4):** naive `now` rejected with a clear error + test.
- **Snapshot verification (Eric / Wigsy S3):** reworded to warehouse/DBA confirmation, not a grep.

### Suggestions Incorporated
- Repo-wide grep for the constant + dangling imports (Eric / Wigsy S1) → Phase 3.
- Sibling-metric coupling audit (Eric) → Phase 3.
- Past-day test uses `now` strictly after day end (Wigsy S4) → Phase 2.
- X-Role trust-model + case-sensitivity tracked as out-of-scope tickets (Wigsy).

---

## APPENDIX: Detailed Exploration Findings

### Files Investigated
- `app.py` — HTTP handler. Role gate: `X-Role` header must be in `("admin","analyst")` else 403;
  parses `tenant_id`; calls `daily_active_users`. (Suspect #1 — red herring.)
- `service.py` — validates `tenant_id` (raises `ValueError` if falsy), calls `day_bounds()`, then
  `count_distinct_users`.
- `timewindow.py` — **root cause.** Builds `[start, end)` UTC window; clamps current-day `end` to
  `now − TENANT_UTC_OFFSET_HOURS` (10h).
- `db.py` — parameterized `SELECT COUNT(DISTINCT user_id) ... event_ts >= ? AND event_ts < ?`;
  `_execute_scalar` stubbed. (Suspect #2 — red herring; DISTINCT is correct.)

### Repo State
Only these 4 files + README; no tests, no other callers, no snapshot table, no config/env for the
offset (verified via `ls`/`glob`). Single commit `57327dd baseline`.

### Current Behaviour
Current-day window `[midnight_UTC, now − 10h)` → drops last 10h of events; inverts (empty) before
10:00 UTC. Past days return the full UTC day (clamp is a no-op).

---

## APPENDIX: Root Cause Analysis

### Primary Hypothesis (SELECTED) — HIGH
Tenant-offset clamp at `timewindow.py:30` truncates the current-day window's upper bound to
`now − 10h`. Explains every symptom (see Investigation Summary table). Verified by direct code trace.

### Secondary Hypothesis — LOW (refuted)
`COUNT(DISTINCT user_id)` "tightening" in `db.py`. DISTINCT is the correct DAU semantic; a prior
`COUNT(*)` would have read *high*, not low. No time dependency → cannot produce the morning/evening
gradient or leave past days correct. Bounds are passed through unchanged.

### Tertiary Hypothesis — LOW (refuted)
Role validation in `app.py`. All-or-nothing 403 auth gate on *access*, not the count value; zero time
dependency; cannot produce a gradient or selectively affect the current day.

---

**To implement this plan:**
```
/implement-plan
```
