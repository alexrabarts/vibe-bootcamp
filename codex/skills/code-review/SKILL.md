# Code Review

Perform a comprehensive code review of recent changes, including running the test suite.

## When to Use

Use this skill before committing code. It reviews all uncommitted changes (or a specific set of files) for security, bugs, code quality, and best practices.

## Process

### Step 1: Gather Changes

Determine what to review:

- Default: All uncommitted changes (`git diff HEAD`)
- If the user specifies files: Review only those files
- If the user says "staged": Review only staged changes (`git diff --staged`)
- If the user says "last": Review the last commit (`git show HEAD`)

Run `git status` to understand the current state.

### Step 2: Run Tests

Before reviewing code, run the project's test suite:

1. Detect the test command:
   - `justfile` with `test:` recipe -> `just test`
   - `package.json` with test script -> `npm test`
   - `go.mod` -> `go test ./...`
   - `pytest.ini` or `pyproject.toml` -> `pytest`
   - `Cargo.toml` -> `cargo test`
2. Run the test command and capture results
3. Note pass/fail status for inclusion in the review

### Step 3: Review the Code

Examine all changes across these categories:

**CRITICAL** (must fix before committing):
- Test failures
- Security vulnerabilities (SQL injection, XSS, auth bypass, secret exposure)
- Data loss risks
- Breaking bugs

**WARNING** (should fix):
- Code quality issues (duplicated logic, overly complex functions)
- Missing error handling
- Missing input validation
- Unused imports, dead code, orphaned functions
- Leftover debug logging (console.log, fmt.Println, etc.)
- Stale TODOs or commented-out code

**SUGGESTION** (nice to have):
- Style improvements
- Performance optimizations
- Better naming
- Documentation improvements

**POSITIVE** (things done well):
- Good patterns, clean code, thorough testing

### Step 4: Present Results

For each issue, provide:
- Category (CRITICAL / WARNING / SUGGESTION / POSITIVE)
- File and approximate location
- Description of the issue
- Recommended fix

End with a clear recommendation:
- "Ready to commit" (no critical or warning issues, tests pass)
- "Fix issues first" (critical or warning issues exist, or tests fail)

**Do NOT modify any code or git state. This is read-only analysis.**
