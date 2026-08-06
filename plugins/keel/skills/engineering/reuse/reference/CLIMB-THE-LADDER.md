# Climb the Ladder — full doctrine

Before writing ANY new function, helper, utility, or abstraction, stop at the FIRST rung that holds. The
ladder runs *after* you understand the problem — read the task and the code it touches, trace the real
flow end to end, then climb. Two rungs work → take the higher one and move on.

1. **Does this need to exist at all?** Speculative need = skip it, say so in one line. (YAGNI)
2. **Already in this codebase?** grep/search the repo for an existing utility, helper, type, or pattern
   that does the same thing — shared libs, utils, common modules, sibling files. Re-implementing what's a
   few directories over is the most common slop. Reuse it.
3. **Stdlib does it?** Use the language standard library (string/array/collection/path/url helpers, etc.).
4. **Native platform feature covers it?** `<input type="date">` over a picker lib, CSS over JS, DB
   constraint over app code, an HTTP client's built-in retry over a wrapper. Check the framework's own API
   (React hooks, LangGraph utilities, FastAPI dependencies). Use WebFetch or Context7 for current docs if
   unsure.
5. **Already-installed dependency solves it?** Check `package.json`, `pyproject.toml`, `go.mod`. Read its
   docs — it likely exports what you need. Never add a NEW dependency for what a few lines can do. If
   nothing installed covers it and the gap is real, you may PROPOSE a well-vetted library (actively
   maintained, significant adoption, solves a real gap — present package name, why, alternatives
   considered).
6. **Can it be one line?** Make it one line.
7. **Only then:** write the minimum code that works.

## If you catch yourself writing >10 lines for something that feels generic, STOP

Climb the ladder again. It almost certainly exists. See `REINVENTION-CATALOG.md`.

## Bug fix = root cause, not symptom

A report names a symptom. Before you edit, grep every caller of the function you're about to touch. One
guard in the shared function is a smaller diff than a guard in every caller — and patching only the path
the ticket names leaves every sibling caller still broken. Fix it once, where all callers route through.

## Two stdlib options, same size?

Take the one that's correct on edge cases. Lazy means writing less code, not picking the flimsier
algorithm.
