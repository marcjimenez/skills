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

## Comments get the same minimalism

Prose is not exempt from the diet. Two tests before any comment survives: could a reader who has never
seen the code have written it just from the code (Ousterhout), and does it explain **why** rather than
**what** (Google)? A comment needed to explain *what* is a refactoring signal, not a writing task.

The failure mode to watch for is **commit-message content leaking into source**: how the bug was found,
what was tried, what changed. The code carries facts about its present state; the commit carries the story
of the edit.

In TypeScript, `/** */` is for consumers and `//` is for maintainers — a JSDoc block on a module-private
helper is usually the wrong form. Never restate types the signature already gives.

**Do not set a ratio target.** SonarQube shipped a 25% comment-density gate and deprecated it in 2022,
because it is *"very artificial"* and developers write fake comments to turn the gate green. Use smells
instead: a comment block longer than the code it introduces, or one covering several unrelated topics, and
push each comment down to the narrowest scope it applies to.

The real reason to write fewer is rot. Across 1,500 systems, code and comments co-evolve in only **7%** of
method changes, so nearly every comment you write will drift. Read `reference/COMMENTS.md` for the
anti-pattern table, the substitutions to try first, the counterweight against cutting too far, and sources.

## Never commit throwaway scripts

Ad-hoc verification harnesses, e2e drivers and probe scripts stay in the scratchpad. Paste their output
into the PR instead. The repo carries code that CI runs and the team maintains; a script needing a running
server and a token is neither, so it rots and misleads people into thinking it is a gate. It also brings
its own review burden — an e2e harness written this way turned out to contain a code injection, because it
interpolated externally-sourced names into a shell and Python. If a check deserves to be permanent, write
it as a real test.

## Intensity + guardrails

The intensity level (lite / full / ultra) governs how hard you cut. Default is **full**. The guardrail
list names what is NEVER simplified away at any intensity. Read `reference/PONYTAIL.md` for both.
