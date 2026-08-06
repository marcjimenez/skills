# Task file template

Write to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/todo.md`:

```markdown
# {Feature Name}

## Implementation
- [ ] {atomic task} — verify: {exact check}
- [ ] {atomic task} — verify: {exact check}

## Tests
- [ ] {test task} — verify: {test passes}

## Quality
- [ ] All tests pass (run command: {exact command})
- [ ] Lint clean (run command: {exact command})
- [ ] Build succeeds (run command: {exact command})
- [ ] Self-review diff: no debug code, no TODOs, no console.logs

## Ship
- [ ] /marcjimenez:code-review run on LOCAL diff (NOT pushed yet)
- [ ] All critical/high findings fixed
- [ ] Documentation reviewed + updated (in sync with code)
- [ ] Final re-review clean
- [ ] ONLY NOW: push branch + create PR with summary + test plan
- [ ] All boxes in this file checked
```

Adapt the Quality section to the project. For prompt-ware / docs repos with no test/lint/build, substitute
concrete structural checks (JSON parses, frontmatter valid, line counts, no stale references).
