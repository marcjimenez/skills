---
name: brainstorm
description: Explore multiple solution approaches with tradeoffs and real-world examples before committing to one.
disable-model-invocation: true
---

# marcjimenez brainstorm

Diverge before you converge. Map the option space for a problem, weigh the tradeoffs, and recommend one —
without committing to an implementation.

## Steps

1. **Understand the problem.** If the ask is fuzzy, invoke `/marcjimenez:requirements` to pin the constraints
   enough to compare options (a full spec is not required at this stage).

2. **Research (breadth).** Invoke `/marcjimenez:research` in `breadth` mode — one shallow survey pass: what
   already exists, what's reusable (ladder rungs), how others solved it. Enough to sketch options; skip
   per-claim verification.

3. **Generate 2–4 approaches.** For each: a one-line thesis, a rough sketch (interface / pseudocode /
   architecture bullets), the highest reuse rung it can reach, and pros / cons / risk / effort. Structure
   per `reference/TRADEOFFS.md`.

4. **Compare + recommend.** Build the comparison matrix and pick a winner with a one-paragraph rationale.

Write to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/brainstorm.md` (never inside the target repo).

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

## End

Suggest the next command — do not run it yourself:

> Recommended: Option <X>. Run `/marcjimenez:plan` to expand it into a full plan.
