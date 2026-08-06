# Ponytail — intensity levels, guardrails, debt ledger

## Intensity levels

Default is **full**. The user may set the level for a task ("ponytail lite" / "ultra"), or it is read from
config (`defaults.ponytail_intensity`). The level governs how aggressively `/marcjimenez:reuse` climbs the ladder
and how hard the Simplicity reviewer in `/marcjimenez:code-review` cuts.

| Level | What changes |
|-------|--------------|
| **lite** | Build what's asked, but name the lazier alternative in one line. User picks. |
| **full** | The ladder enforced. Stdlib and native first. Shortest diff, shortest explanation. Default. |
| **ultra** | YAGNI extremist. Deletion before addition. Ship the one-liner and challenge the rest of the requirement in the same breath. |

## Lazy, not negligent (the guardrail)

Never simplify away, at ANY intensity:

- Understanding the problem fully (trace the real flow before picking a rung — a small diff you don't
  understand is a confident wrong fix)
- Input validation at trust boundaries
- Error handling that prevents data loss
- Security measures
- Accessibility basics
- The calibration real hardware needs (a clock drifts, a sensor reads off — the platform is never the spec
  ideal)
- Anything the user explicitly requested (user insists on the full version → build it, no re-arguing)
- The ONE runnable check behind non-trivial logic (a branch, loop, parser, money/security path). Lazy code
  without its check is unfinished. Trivial one-liners need none.

## The `ponytail:` comment convention

Mark a deliberate shortcut with a `ponytail:` comment so it reads as intent. If the shortcut has a known
ceiling, the comment names the ceiling AND the upgrade trigger:

```
# ponytail: global lock, per-account locks if throughput matters
```

## Debt ledger

Harvest every deliberate shortcut before a PR so a deferral can't quietly become permanent:

```bash
grep -rnE '(#|//) ?ponytail:' . --exclude-dir={node_modules,.git,dist,build}
```

Each marker must name a ceiling AND an upgrade trigger. Flag any that names no trigger as `no-trigger`
(those silently rot). Roll the ledger into the PR description so deferrals are tracked, not forgotten.
