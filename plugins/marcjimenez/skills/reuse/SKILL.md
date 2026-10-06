---
name: reuse
description: >-
  Enforces the Climb-the-Ladder reuse doctrine BEFORE any new function, helper, utility, type, or
  abstraction is written, or any dependency added. Stops at the first rung that holds: YAGNI,
  existing repo utility, stdlib, native platform/framework feature, installed dependency,
  one-liner, minimum new code. Use PROACTIVELY whenever about to create new code, add a package, or
  audit existing code for duplication. Triggers on: "is there a util that already does this", "do
  we already have one", "DRY", "DRY this up", "can we reuse", "don't reinvent the wheel", "fix this
  at the source", "do we need a library for this", "write a helper", and any request to create a
  new file, function, component, or type.
---

# Reuse — Climb the Ladder before writing code

The best code is the code never written. Before writing ANY new function, helper, utility, or
abstraction, climb the ladder and stop at the FIRST rung that holds. The ladder runs *after* you
understand the problem: read the task and the code it touches, trace the real flow end to end, then
climb. Two rungs work → take the higher one and move on.

1. **Does this need to exist at all?** Speculative need = skip it, say so in one line. (YAGNI)
2. **Already in this codebase?** grep/search the repo for an existing utility, helper, type, or pattern.
3. **Stdlib does it?** Use the language standard library.
4. **Native platform/framework feature covers it?** Check the framework's own API first.
5. **Already-installed dependency solves it?** Read `package.json` / `pyproject.toml` / `go.mod`.
6. **Can it be one line?** Make it one line.
7. **Only then:** write the minimum code that works.

Full doctrine, the ">10 lines STOP" heuristic, root-cause-not-symptom bug fixes, and the two-stdlib-options
rule: read `reference/CLIMB-THE-LADDER.md`.

The catalog of things people reinvent (debounce → lodash, dates → dayjs/date-fns, retry → HTTP client,
validation → zod/pydantic, …): read `reference/REINVENTION-CATALOG.md`.

Honor the active ponytail intensity (lite/full/ultra) — see `/marcjimenez:coding-style`. `ultra` climbs hardest.

**Never cut a guardrail to save code** (validation, error handling, security, accessibility, the one
runnable check). Lazy means writing less code, not a flimsier solution. See `/marcjimenez:coding-style` for the
full guardrail list.
