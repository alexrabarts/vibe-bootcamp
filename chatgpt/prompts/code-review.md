# Code Review Prompt

Paste the following into ChatGPT when you want a code review before committing.

---

Please review the following code changes. I want a thorough review covering:

**CRITICAL** (must fix before committing):
- Security vulnerabilities (injection, auth bypass, secret exposure)
- Data loss risks
- Breaking bugs
- Test failures

**WARNING** (should fix):
- Missing error handling
- Missing input validation
- Code quality issues (duplication, complexity)
- Unused imports, dead code, orphaned functions
- Leftover debug logging
- Stale TODOs

**SUGGESTION** (nice to have):
- Style improvements
- Performance optimizations
- Better naming
- Documentation improvements

**POSITIVE** (things done well):
- Good patterns worth noting

For each issue, tell me:
- Category (CRITICAL/WARNING/SUGGESTION/POSITIVE)
- File and location
- What the issue is
- How to fix it

End with a clear verdict: "Ready to commit" or "Fix issues first".

Here are the changes:

```
[paste your git diff here, or describe/paste the files]
```
