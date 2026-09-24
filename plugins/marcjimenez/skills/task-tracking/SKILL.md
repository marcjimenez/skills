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
# One cache per REPOSITORY, shared by every worktree and workspace. --git-common-dir, not
# --show-toplevel: inside a worktree the latter returns the worktree, which splits the cache.
REPO_KEY="$(git config --get remote.origin.url 2>/dev/null \
  | sed -E 's#^(https?://[^/]+/|git@[^:]+:|ssh://[^/]+/)##; s#\.git$##; s#[/ ]#-#g')"
[ -n "$REPO_KEY" ] || REPO_KEY="$(G="$(git rev-parse --git-common-dir 2>/dev/null)" \
  && R="$(CDPATH= cd -- "$(dirname "$G")" && pwd -P)" \
  && printf '%s-%s' "$(basename "$R")" "$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
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
Before creating `runs/<slug>/`, check whether `todo.md` is already there naming a different branch. If it
is, append that branch's last segment (`add-oauth-login-retry-backoff`) rather than writing over work in
progress somewhere else.

## Writing tasks

- Each task is ONE logical unit, completable without context-switching.
- Every task has a `verify:` field that is a concrete check (command output, test name, assertion). If you
  can't define the verify, the task is too vague — split it.
- If you discover a new task mid-work, ADD it to the file before doing it.
- Mark `[x]` only after the verify passes.

The template (Implementation / Tests / Quality / Ship): see `reference/TASK-FILE-TEMPLATE.md`.
