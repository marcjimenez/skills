# Pre-PR verification

Run the full quality gauntlet. Nothing ships without this. Everything here is local — nothing is pushed yet.

```bash
# Run these (adjust per project):
{test command}
{lint command}
{build command}
```

For prompt-ware / docs repos with no test/lint/build, substitute concrete structural checks (JSON parses,
frontmatter valid, line counts within limits, no stale references).

Self-review the local diff:

```bash
git diff "$BASE"...HEAD   # $BASE = vcs.base_branch, default main
```

Check for:
- [ ] Accidentally staged files (`.env`, `.DS_Store`, `node_modules`)
- [ ] Debug code (`console.log`, `debugger`, stray `print`)
- [ ] TODO/FIXME/HACK comments you introduced
- [ ] Unused imports or variables you added
- [ ] Hardcoded values that should be config

## Ponytail debt ledger

Harvest every deliberate shortcut so a deferral can't quietly become permanent:

```bash
grep -rnE '(#|//) ?ponytail:' . --exclude-dir={node_modules,.git,dist,build}
```

Apply the debt-ledger doctrine (ceiling + upgrade trigger per marker; roll into the PR description) — see
`/keel:coding-style` `reference/PONYTAIL.md`.

Fix anything found. Re-run the checks. Loop until clean.
