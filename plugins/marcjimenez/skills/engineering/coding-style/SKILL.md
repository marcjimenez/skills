---
name: coding-style
description: >-
  The house coding style — apply to ALL code you write, edit, or refactor. Enforces ponytail minimalism
  (the best code is the code never written: deletion over addition, boring over clever, fewest files,
  shortest working diff), the `ponytail:` shortcut-comment convention, root-cause-not-symptom bug fixes,
  and the guardrails that are NEVER cut at any intensity (validation, error handling, security,
  accessibility, comprehension, the one runnable check). Repo CLAUDE.md and existing conventions win over
  house style. Use PROACTIVELY whenever writing or changing non-trivial code.
---

# Coding style — ponytail minimalism

You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never
written. This discipline shortens the solution, never the reading.

**Repo conventions win.** If the repo's `CLAUDE.md` or existing code establishes a convention, follow it
over anything here. Match existing style; don't impose your preferences.

## The core moves

- **Deletion over addition. Boring over clever. Fewest files, shortest working diff** — but only once you
  understand the problem; the smallest change in the wrong place isn't lazy, it's a second bug.
- **No unrequested abstractions:** no interface with one implementation, no factory for one product, no
  config for a value that never changes.
- **Before writing new code, climb the ladder** — see `/marcjimenez:reuse`.
- **Bug fix = root cause, not symptom.** grep every caller; fix once where all callers route through.
- **Mark deliberate simplifications with a `ponytail:` comment** so a shortcut reads as intent, not
  ignorance. If it has a known ceiling, the comment names the ceiling AND the upgrade path:
  `# ponytail: global lock, per-account locks if throughput matters`.

## Intensity + guardrails

The intensity level (lite / full / ultra) governs how hard you cut. Default is **full**. The guardrail
list names what is NEVER simplified away at any intensity. Read `reference/PONYTAIL.md` for both.
