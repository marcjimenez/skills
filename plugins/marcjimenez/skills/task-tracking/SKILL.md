---
name: task-tracking
description: >-
  Maintains a durable task file as the single source of truth for multi-step coding work. Use PROACTIVELY
  whenever a build or plan spans more than one step. Writes atomic checkboxes each with a concrete verify,
  marks [x] only when the verify passes, and enforces the rule: NOT done until every box is checked.
  Triggers on: a multi-step feature, "plan the work", starting an implementation, tracking progress across
  several changes.
---

# Task tracking

The task file is your contract with yourself. It is the source of truth — not your memory, not your
feeling of "done."

CRITICAL RULE: You are NOT done until every checkbox in the task file is `[x]`. If you feel like stopping,
read the task file. If unchecked items remain, keep working.

## Where the task file lives (durable, never in the repo)

Artifacts live under the marcjimenez config home, keyed by repo — never inside the target repository, never in
`/tmp` (which is wiped on reboot):

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"          # macOS + Linux; Windows: %APPDATA%\marcjimenez
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
RUN_DIR="$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>"
mkdir -p "$RUN_DIR"
# task file: $RUN_DIR/todo.md
```

**`<slug>` (canonical, shared by all marcjimenez skills):** the feature in kebab-case — lowercase, spaces and
underscores → hyphens, strip other punctuation (e.g. "Add OAuth login" → `add-oauth-login`). Derive it
ONCE. If `/marcjimenez:plan` already produced artifacts for this feature, reuse its `<slug>` so `research.md`,
`plan.md`, and `todo.md` share one `runs/<slug>/` directory. If the branch is `{prefix}/{slug}`, the branch
slug IS the slug.

One cache serves every worktree of a repo, so two parallel workspaces can reach for the same `<slug>`.
The task file records its `branch:` for exactly this reason. Before creating `runs/<slug>/`, read any
`todo.md` already there. A matching `branch:` means the directory is your own earlier run, so reuse it. A
different one means somebody else is mid-flight, so suffix your directory with your whole branch name,
slashes to hyphens: `fix/oauth-token-refresh` sharing the slug `oauth-token-refresh` gets
`runs/oauth-token-refresh--fix-oauth-token-refresh`. Branch names are unique, so the suffix always is.

## Writing tasks

- Each task is ONE logical unit, completable without context-switching.
- Every task has a `verify:` field that is a concrete check (command output, test name, assertion). If you
  can't define the verify, the task is too vague — split it.
- If you discover a new task mid-work, ADD it to the file before doing it.
- Mark `[x]` only after the verify passes.

The template (Implementation / Tests / Quality / Ship): see `reference/TASK-FILE-TEMPLATE.md`.
