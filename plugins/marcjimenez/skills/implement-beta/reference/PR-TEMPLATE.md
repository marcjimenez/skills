# PR body template

```markdown
## Summary
- {what changed and why — bullet 1}
- {bullet 2}

## Tasks
{the completed task file, copied from runs/<slug>/todo.md with its `[x]` marks intact}
- [x] {task} — {exact check that passed}
- [x] {task} — {exact check that passed}

## End-to-end verification
Environment: {prod | dev}
- [x] {scenario} — {what the response and the database rows showed}
- [x] Every mutation undone, proven by re-query

{or, when there is no runtime surface to exercise:}
No end-to-end surface: {reason}

## Ponytail debt ledger
- {any `ponytail:` shortcuts, each with its ceiling + upgrade trigger — or "none"}

## Known limitations
- {anything the review surfaced but deferred, with reason — or "none"}
```

The Tasks section is the task file, not a retelling of it. Copy the boxes across rather than writing a
fresh summary, so the PR shows exactly what was verified and how.

Create with `gh pr create --base "$BASE"` (`$BASE` = `vcs.base_branch`, default `main`). If
`vcs.assign_reviewer`, assign each of `vcs.reviewers` (default `copilot`) with `gh pr edit --add-reviewer`.
