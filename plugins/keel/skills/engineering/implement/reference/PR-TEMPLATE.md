# PR body template

```markdown
## Summary
- {what changed and why — bullet 1}
- {bullet 2}

## Test plan
- [ ] {verification step}
- [ ] {verification step}

## Ponytail debt ledger
- {any `ponytail:` shortcuts, each with its ceiling + upgrade trigger — or "none"}

## Known limitations
- {anything the review surfaced but deferred, with reason — or "none"}
```

Create with `gh pr create --base "$BASE"` (`$BASE` = `vcs.base_branch`, default `main`). If
`vcs.assign_reviewer`, assign each of `vcs.reviewers` (default `copilot`) with `gh pr edit --add-reviewer`.
