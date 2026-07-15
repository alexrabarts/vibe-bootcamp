# Add a seasonal-sale discount to the cart

**Created:** 2026-02-04T09:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Add a seasonal sale on top of the existing flat-percentage discount, by extending the
`apply_discount` helper that every discount path already funnels through.

## Context

### Original Request

We want a seasonal sale percentage applied to the cart, stacking with the existing discount.

### Approach

`pricing.apply_discount(price, pct)` is the single choke point for every percentage discount
in the codebase — `cart_total` calls it, and nothing else computes a percentage inline. Adding
the seasonal rate there means one change site and every caller inherits it.

## Implementation Plan

### Phase 1: Extend the discount helper

**Goal:** Apply the seasonal rate inside the existing helper.

**Rests on:** **A1**

**Files to Modify:**
- `pricing.py`: extend `apply_discount(price, pct)` to take an optional `seasonal_pct`
  and subtract it after the base percentage.

**Verification:** `python -c "import pricing; print(pricing.apply_discount(100, 10, seasonal_pct=10))"`
must print `81.0` (100 less 10%, then less a further 10%).

---

### Phase 2: Thread the rate through the cart

**Goal:** `cart_total` passes the seasonal rate down.

**Rests on:** **A1**

**Files to Modify:**
- `pricing.py`: `cart_total(items, discount_pct, seasonal_pct=0)` forwards `seasonal_pct`
  to `apply_discount`.

**Verification:** `python -c "import pricing; print(pricing.cart_total([100], 10, seasonal_pct=10))"`
must print `81.0`.

## Premises

What this plan rests on about the code as it is today. Each was verified when the plan was
written; `/implement-plan` re-checks them before writing any code, because a plan can go stale.

### A1 — `apply_discount(price, pct)` is the single choke point for percentage discounts
**Why load-bearing:** the entire approach is "one change site, every caller inherits it". If the
percentage path does not funnel through `apply_discount`, Phase 1 has nothing to extend and
Phase 2 threads a parameter into a function that does not exist — the plan does not merely need
adjusting, it needs redesigning around whatever replaced it.
**Class:** MECHANICAL
**Method:** `grep -n "def apply_discount" pricing.py`
**Expected:** `pricing.py` defines `apply_discount(price, pct)`, and `cart_total` calls it.
**Evidence:** `4:def apply_discount(price, pct):`
**Verdict:** VERIFIED

## Success Criteria

- [ ] A seasonal rate stacks on top of the base discount — proven by **P1**
- [ ] Existing callers are unaffected when no seasonal rate is passed — proven by **P2**

## Proof Obligations

### P1 — A seasonal rate stacks on top of the base discount
**Criterion:** first criterion above
**Class:** MECHANICAL
**Method:** `python -c "import pricing; print(pricing.cart_total([100], 10, seasonal_pct=10))"`
**Expected:** prints `81.0`

### P2 — Existing callers are unaffected when no seasonal rate is passed
**Criterion:** second criterion above
**Class:** MECHANICAL
**Method:** `python -c "import pricing; print(pricing.cart_total([100], 10))"`
**Expected:** prints `90.0`

## Assumptions

- Seasonal rates stay a simple percentage; no per-item or per-category rules are in scope.
