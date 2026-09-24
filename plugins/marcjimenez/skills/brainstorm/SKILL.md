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
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. A remote that is a local,
# relative or Windows path is not a portable identity, so it falls through to the path below.
REMOTE="$(git remote get-url origin 2>/dev/null)"
case "$REMOTE" in *://*|*@*:*) ;; *) REMOTE="" ;; esac
# Lowercased with tr, not sed's \L: BSD sed does not implement it and emits a literal L. GitHub treats
# Owner/Repo and owner/repo as one repository, so without this they would hash to two caches.
REPO_KEY="$(printf '%s' "$REMOTE" \
  | sed -E 's#/+$##; s#^[a-z+]+://##; s#^[^/@]*@##; s#^[^/:]+[:/]##; s#\.git$##; s#[/ ]#-#g' \
  | tr '[:upper:]' '[:lower:]')"
case "$REPO_KEY" in ""|.|..|-*|*:*|*\\*) REPO_KEY="" ;; esac
if [ -z "$REPO_KEY" ]; then
  # --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is
  # the worktree and would split the cache. --path-format=absolute (git 2.31+) also canonicalizes.
  G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || git rev-parse --git-common-dir 2>/dev/null)"
  [ -n "$G" ] && G="$(cd -- "$G" 2>/dev/null && pwd -P)"
  # Only a normal checkout's common dir ends in /.git. A submodule's is .git/modules/<name> and a bare
  # repo's is the repo itself; for those the common dir IS the identity, so do not strip a parent.
  case "$G" in */.git) R="${G%/.git}" ;; *) R="$G" ;; esac
  [ -n "$R" ] && REPO_KEY="$(basename "$R" .git)-$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
fi
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
