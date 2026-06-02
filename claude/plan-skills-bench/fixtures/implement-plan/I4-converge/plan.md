# Implement `parse_duration`

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Implement `parse_duration(text)` in `duration.py` so the provided test suite passes.

## Implementation Plan

### Phase 1: `parse_duration(text)`

**Goal:** Parse a duration string into total **seconds** (int). Supports `h` (hours), `m` (minutes),
and `s` (seconds), which may appear **in combination** (e.g. `2h15m30s`).

**Files to Modify:** `duration.py`
**Dependencies:** None

**Implementation Details:** Handle any combination of the three units. Make the existing tests in
`tests/test_duration.py` pass — note they include combined-unit cases, not just single units.

## Testing Strategy

`tests/test_duration.py` (provided) must pass.

## Success Criteria

- [ ] `pytest` is green, including the combined-unit cases (`1h30m`, `2h15m30s`).
- [ ] No dead code or unused imports remain.

## Assumptions

- Input is well-formed (units in descending order, each unit at most once). The provided tests are
  authoritative and must not be modified.
