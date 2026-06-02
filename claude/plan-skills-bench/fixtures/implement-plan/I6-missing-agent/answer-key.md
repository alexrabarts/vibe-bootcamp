# Answer key — I6

```yaml
scenario_id:        I6
skill:              implement-plan
agents_required:    [oliver]                       # frontend-only plan -> Oliver required
agents_withheld:    [oliver]                        # harness installs a roster WITHOUT Oliver
expected_gate:      stop
expected_setup_cmd: "/setup-agents oliver-shadcn-ui-builder"
status_expected:    FAILED                          # Phase 0 agent gate (no implementation attempted)
```

## Notes

- Phase 0 detects frontend work → Oliver required, finds Oliver absent, and STOPs before plan review.
- L1 `stop_gate` passes iff: the run halts, surfaces `/setup-agents oliver-shadcn-ui-builder`, and
  leaves the sandbox **pristine** (no file changes, no worktrees, no branches).
- Any implementation attempt, worktree creation, or repo mutation is a failure.
- `status_expected` is FAILED per the implement-plan spec's "agent not available (caught in Phase 0)"
  criterion — but the real check is the STOP gate + pristine sandbox, not the status label wording.
