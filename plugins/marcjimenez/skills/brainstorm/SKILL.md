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
# One cache per REPOSITORY, keyed by the origin remote so every worktree and workspace share it.
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. Lowercased with tr, not
# sed's \L, which BSD sed does not implement and silently turns into a literal L.
REPO_KEY="$(git remote get-url origin 2>/dev/null \
  | sed -E 's#^([a-z+]+://[^/]+/|[^/:]+:)##; s#\.git$##; s#[/ ]#-#g' | tr '[:upper:]' '[:lower:]')"
# A local-path remote leaves a leading '-', which every coreutils tool reads as an option; an unknown
# scheme leaves a ':'. Either way the repo path below is the better identity, so fall through.
case "$REPO_KEY" in ""|-*|*:*) REPO_KEY="" ;; esac
# --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is the
# worktree and would split the cache. --path-format=absolute makes it absolute AND canonical.
[ -n "$REPO_KEY" ] || REPO_KEY="$(G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
  && [ -n "$G" ] && R="$(dirname "$G")" \
  && printf '%s-%s' "$(basename "$R")" "$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
[ -n "$REPO_KEY" ] || { echo "not in a git repository" >&2; exit 1; }
```

## End

Present the options with pros/cons/tradeoffs, state your recommendation, then ask if the user wants to proceed:

> Explored [N] approaches. Recommended: [APPROACH] because [REASON].
>
> Proceed to detailed planning of this approach?

If the user confirms (yes / y / go / plan it / proceed):
  Invoke `/marcjimenez:plan` with the chosen approach as context.

If the user picks a different option (option N / use approach N):
  Note which one, then invoke `/marcjimenez:plan` with that approach.

If the user declines (no / not yet / let me think):
  > Approaches documented. Run `/marcjimenez:plan` when ready.
