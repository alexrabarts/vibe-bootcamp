# Implement two independent utilities

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Implement two small, independent utilities in separate packages. They share no code and can be built
separately.

## Implementation Plan

### Item A: `geo/distance.py`

- Implement `manhattan(a, b)` returning the Manhattan distance between two `(x, y)` points.

### Item B: `text/slugify.py`

- Implement `slugify(text)`: lowercase, replace runs of non-alphanumeric characters with single
  hyphens, and strip leading/trailing hyphens.

These two items are independent — different directories, no shared code.

## Testing Strategy

Unit tests for each utility.

## Success Criteria

- [ ] `pytest` is green.
- [ ] `manhattan((0, 0), (3, 4)) == 7`.
- [ ] `slugify("Hello, World!") == "hello-world"`.
- [ ] No dead code or unused imports remain.

## Assumptions

- Points are 2-tuples of numbers.
