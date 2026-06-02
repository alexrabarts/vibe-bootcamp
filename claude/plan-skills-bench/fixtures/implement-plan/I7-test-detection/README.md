# Scenario I7 — test-command detection matrix (implement-plan)

Tests that the Test Execution phase picks the **correct test command per the spec's priority order**.
The same trivial task (implement an `add`/sum function) lives in three repos with different build
tooling. Run the skill once per variant and assert the detected/run command.

## Variants

| variant dir              | build signal               | expected command  |
|--------------------------|----------------------------|-------------------|
| `variants/justfile-repo` | justfile with `test:` (+ a bare pytest config) | `just test`       |
| `variants/npm-repo`      | package.json `test` script | `npm test`        |
| `variants/go-repo`       | go.mod                     | `go test ./...`   |

The justfile variant deliberately also has pytest available, so detection must prefer the justfile
`test:` recipe (priority 1) over `pytest`.

## What it scores

- **L2 `test_cmd_correct`** (headline), per variant, against the table above.
- L2 `mode_correct` = SIMPLE_SEQUENTIAL each.
- (Optional) `acceptance_pass`: the trivial `add(2,3)==5` test passes — secondary to detection.

## How to run

For each variant: copy `variants/<v>/` to a sandbox, install Shane, feed the shared `plan.md` to
`/implement-plan`, and record the test command it detected/ran. Grade against `answer-key.md`.
