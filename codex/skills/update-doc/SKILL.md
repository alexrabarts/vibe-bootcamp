# Update Documentation

Add learnings, issues, SOPs, or feature ideas to the project's `.agent/` documentation directory.

## When to Use

Use this skill to capture knowledge as you work: things you learned, issues you encountered, ideas for improvements, or architectural decisions.

## Process

### Step 1: Identify Documentation Type

Based on the user's input, determine where the content belongs:

| Content Type | File | Example |
|-------------|------|---------|
| Lesson learned | `.agent/sop/learnings.md` | "I learned that X requires Y" |
| Known issue | `.agent/sop/issues.md` | "Issue: Z breaks when W happens" |
| Feature idea | `.agent/tasks/backlog.md` | "Feature idea: add auto-sync" |
| Architectural decision | `.agent/system/architecture.md` | "We chose X over Y because..." |

### Step 2: Initialize if Needed

If `.agent/` doesn't exist, create the directory structure:

```
.agent/
  README.md
  sop/
    learnings.md
    issues.md
  system/
    (created on demand)
  tasks/
    (created on demand)
```

### Step 3: Format and Append

Read the target file to understand the existing format, then append the new content in a matching style:

- Use appropriate markdown headings
- Include dates
- For issues: note status (IN PROGRESS / BLOCKED / COMPLETED)
- For learnings: include context about what worked and what didn't
- Keep it concise and technical

### Step 4: Confirm

Briefly describe what was added and where.

**Never remove or modify existing content unless specifically asked.**
