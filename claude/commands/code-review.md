---
description: Invoke Wigsy for comprehensive code review
---

You are helping the user get a comprehensive code review from Wigsy, the elite code reviewer agent. This command invokes Wigsy to review code changes, focusing on security, bugs, code quality, testing, and best practices.

## Command Modes

### 1. Review Recent Changes: `/code-review` (no arguments)
Review all uncommitted changes (both staged and unstaged).

### 2. Review Staged Changes: `/code-review staged`
Review only staged changes (what will be committed next).

### 3. Review Specific Files: `/code-review file1 file2 ...`
Review specific files by path (e.g., `/code-review bin/go-install dot_zshrc.tmpl`).

### 4. Review Last Commit: `/code-review last`
Review the most recent commit.

### 5. Review Commit Range: `/code-review <commit1>..<commit2>`
Review changes between two commits or branches.

## Your Task

### Step 1: Parse Command Arguments

Determine which mode the user is requesting:
- No arguments → Review all uncommitted changes (staged + unstaged)
- `staged` → Review only staged changes
- `last` → Review last commit
- `<commit>..<commit>` or `<branch>..<branch>` → Review commit range
- File paths → Review specific files

### Step 2: Gather Code to Review

Use parallel Bash calls to efficiently gather information:

#### For Uncommitted Changes (default mode)
```bash
# Run these in parallel
git status
git diff HEAD  # All changes (staged + unstaged)
```

#### For Staged Changes
```bash
# Run these in parallel
git status
git diff --staged
```

#### For Specific Files
```bash
# For each file, run in parallel
git diff HEAD -- <file-path>
cat <file-path>  # If file is new/untracked
```

#### For Last Commit
```bash
# Run these in parallel
git log -1 --stat
git show HEAD
```

#### For Commit Range
```bash
# Run these in parallel
git log <range> --oneline
git diff <range>
```

### Step 3: Context Gathering

Before invoking Wigsy, gather relevant context:

1. **Read project CLAUDE.md** (if exists) to understand project-specific guidelines
2. **Check for recent commit messages** (git log -5 --oneline) to understand commit style
3. **Identify file types** being reviewed to inform Wigsy of domain-specific considerations

### Step 4: Run Tests

Before invoking Wigsy, attempt to run the project's test suite. Detect the test command based on what exists in the project:

1. **Check for test commands** (in order of preference):
   - `justfile` with `test` recipe → `just test`
   - `Makefile` with `test` target → `make test`
   - `package.json` with `test` script → `npm test`
   - `go.mod` file → `go test ./...`
   - `pytest.ini`, `pyproject.toml`, or `tests/` dir → `pytest`
   - `Cargo.toml` → `cargo test`

2. **Run the test command** if detected. Capture both stdout and stderr.

3. **Note the test result** (pass/fail) to include in Wigsy's context.

If no test command is detected or the project doesn't have tests, note "No test suite detected" for Wigsy.

### Step 5: Invoke Wigsy Agent

Use the Task tool to invoke the wigsy-code-reviewer agent with comprehensive context:

```
Please review the following code changes:

**Context:**
- Project: [project name from git repo or cwd]
- File types: [shell scripts, Go code, configuration files, etc.]
- Change type: [new feature, bug fix, refactor, etc.]

**Test Results:**
[If tests were run, include result: "✓ All tests passed" or "✗ Tests failed" with failure summary]
[If no tests detected, state: "No test suite detected"]

**Changes to review:**

[Include the diff or file contents here]

**Files changed:**
- path/to/file1.ext
- path/to/file2.ext

**Additional context:**
[Any relevant information from CLAUDE.md or project patterns]

Please provide a comprehensive code review covering:
1. **CRITICAL**: Test failures (if tests failed, this is a blocking issue that must be addressed)
2. Security vulnerabilities and concerns
3. Potential bugs and logic errors
4. Code quality and maintainability issues
5. Testing considerations (coverage, missing tests, test quality)
6. Documentation needs (especially .agent/ placement)
7. Best practices for the specific file types
8. Final recommendation on commit readiness

If tests failed, the code is NOT ready to commit until failures are resolved.
```

### Step 6: Present Review Results

After Wigsy completes the review, summarize the key findings and recommendations for the user. If tests failed, prominently highlight this as a blocking issue.

## Important Guidelines

1. **Always gather context first** before invoking Wigsy
   - Understand what changed
   - Know the project structure
   - Identify relevant coding standards

2. **Use parallel Bash calls** when gathering independent information
   - git status, git diff, git log can all run in parallel
   - Reading multiple files can happen concurrently

3. **Provide complete context to Wigsy**
   - Full diffs, not just file names
   - Project-specific guidelines from CLAUDE.md
   - File types and change purpose

4. **Handle edge cases gracefully**
   - No changes to review → Inform user "No changes to review. Working directory is clean."
   - File not found → Report which files couldn't be found
   - Not a git repo → Inform user this command requires a git repository

5. **Respect git state**
   - Never modify git state (no commits, no staging)
   - Only read and analyze
   - Inform user of current git status

6. **Be specific about what's being reviewed**
   - List files included in review
   - Show change statistics (insertions/deletions)
   - Indicate if reviewing staged vs unstaged changes

## Example Invocations

### Example 1: Review uncommitted changes
```
user: /code-review
assistant: I'll gather your uncommitted changes and have Wigsy review them.

[Runs git status and git diff HEAD in parallel]

Found changes in 3 files:
- bin/go-install (modified)
- dot_zshrc.tmpl (modified)
- .chezmoi.toml.tmpl (new)

Total: +47 -12 lines

[Detects justfile, runs: just test]

✓ All tests passed (12 passed in 2.3s)

Invoking Wigsy for code review...

[Uses Task tool to invoke wigsy-code-reviewer with full context including test results]
```

### Example 2: Review specific file
```
user: /code-review bin/pg
assistant: I'll have Wigsy review the bin/pg script.

[Reads file and gets diff if modified]

Reviewing bin/pg (PostgreSQL connection utility)
Type: Shell script
Status: Modified (+15 -3)

Invoking Wigsy for code review...

[Uses Task tool to invoke wigsy-code-reviewer]
```

### Example 3: Review staged changes before commit
```
user: /code-review staged
assistant: I'll review your staged changes that are ready to commit.

[Runs git status and git diff --staged in parallel]

Staged changes in 2 files:
- lua/plugins/telescope.lua (+23 -5)
- lua/keymaps.lua (+8 -2)

Invoking Wigsy for code review...

[Uses Task tool to invoke wigsy-code-reviewer]
```

### Example 4: No changes
```
user: /code-review
assistant: [Runs git status]

No changes to review. Your working directory is clean.

To review the last commit: /code-review last
To review specific files: /code-review <file-path>
```

## Domain-Specific Considerations

Based on file types being reviewed, include relevant context for Wigsy:

- **Shell scripts** (.sh, bin/ scripts): Remind about quoting, error handling, POSIX compliance
- **Chezmoi templates** (.tmpl): Note Go template syntax, whitespace control
- **Dotfiles** (dot_*): Check for cross-platform compatibility, syntax correctness
- **Makefiles**: Validate PHONY declarations, target dependencies
- **Neovim config** (lua/): Check plugin configurations, key binding conflicts
- **Go code**: Standard library usage, error handling, testing
- **Configuration files** (.toml, .yaml, .json): Syntax validation, schema adherence

## Integration with Git Workflow

This command fits into the development workflow:

1. **Make changes** to code
2. **Run /code-review** before committing (tests run automatically as part of review)
3. **Address Wigsy's feedback** including any test failures
4. **Commit** when review passes
5. **Push** when explicitly requested

The /code-review command automatically runs the test suite if detected, so you don't need to run tests separately. However, you may still want to run specific tests during development before running the full review.

Never automatically commit or push - that's the user's decision after reviewing Wigsy's feedback.

## Error Handling

- **Not in git repo**: "This directory is not a git repository. The /code-review command requires git."
- **Invalid commit range**: "Invalid commit range '<range>'. Please use format: commit1..commit2"
- **File not found**: "File '<file>' not found in repository."
- **No Wigsy agent**: "Wigsy agent not found. The wigsy-code-reviewer agent should be in ~/.claude/agents/"

Now execute the user's requested code review mode!
