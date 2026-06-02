"""Harness for the /create-plan and /implement-plan eval set.

See ../SPEC.md for the contract and ../RUNNER.md for the mechanics this implements.

Modules:
  contracts  - ScenarioKey / RunArtifacts / TrialRecord; loads answer keys from fixtures
  sandbox    - materialize a fixture repo into a temp git sandbox; git-state assertions
  suites     - run acceptance suites (pytest in prod, dependency-free fallback) + anti-tamper hashing
  checks     - deterministic L1 gates + L2 structural checks for both skills
  drivers    - SkillDriver interface + MockDriver (selftest) / ReplayDriver / CliDriver (seam)
  aggregate  - per-scenario/version aggregation, scoring, A/B deltas
  run        - CLI entrypoint
  selftest   - end-to-end self-test of the deterministic machinery
"""
