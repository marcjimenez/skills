---
name: implement
description: Run the full build cycle — branch, grill requirements, track tasks, build with minimalism discipline, verify, adversarial review, and open a PR.
disable-model-invocation: true
---

# marcjimenez implement

The full build cycle. You are bound to it until every task box is `[x]`. No shortcuts, no early exits. The
only valid exit is a fully-checked task file with a merge-ready PR.

## Phase 0 — Fresh branch

Read the `vcs` section of config.json first (schema: `/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`). Defaults:
`base_branch=main`, prefixes `feat/fix/refactor/docs`.

```bash
BASE="main"   # ← vcs.base_branch from config
git checkout "$BASE" && git pull origin "$BASE"
git checkout -b {prefix}/{slug}   # prefix ∈ vcs.branch_prefixes
```
GATE: on a fresh branch off `$BASE` with a clean working tree before proceeding. (In a pre-created workspace
branch, confirm you're on a non-base feature branch that's clean.)

## Phase 1 — Requirements

Invoke `/marcjimenez:requirements` until the spec is unambiguous and confirmed. Skip only if `/marcjimenez:plan` already
produced a confirmed spec — in that case adopt its Context and Task seed.

## Phase 2 — Task file

Invoke `/marcjimenez:task-tracking` to create (or adopt the plan's Task seed into) the durable task file at
`$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/todo.md`. Reuse the plan's `<slug>` if a plan exists (so it finds
the same `runs/<slug>/` dir); otherwise derive `<slug>` per `/marcjimenez:task-tracking`. GATE: present the task
list; get confirmation before coding.

## Phase 3 — Build loop (per task)

1. Implement the task. Before writing new code, the reuse + style disciplines apply automatically:
   `/marcjimenez:reuse` (climb the ladder before any new function/util/dep) and `/marcjimenez:coding-style` (ponytail
   minimalism, guardrails, match repo conventions). On hitting an unfamiliar API, `/marcjimenez:research`. When the
   task makes non-trivial use of a dependency, framework, or pattern (a new integration, an unfamiliar API,
   or a usage not already established in the repo), invoke `/marcjimenez:best-practices` in `advisory` mode so
   the code follows how the ecosystem does it well; skip it for routine use of an already-adopted dependency
   in an already-established way.
2. Run its `verify:` check. If it fails → fix → re-run until green.
3. Mark `[x]` in the task file.
4. Commit at logical boundaries (conventional prefix). One concern per commit.
5. If you discover a new task mid-work, ADD it to the file before doing it.

## Phase 4 — Pre-PR verification

Run the quality gauntlet and self-review the local diff — nothing pushed yet. Full checklist + the ponytail
debt-ledger grep: `reference/PRE-PR-VERIFICATION.md`. Loop until clean; mark verification tasks `[x]`.

## Phase 5 — Review, THEN PR (hard gate)

GATE — invoke `/marcjimenez:code-review` on `git diff "$BASE"...HEAD`. Do NOT run `git push` and do NOT run
`gh pr create` until it returns clean and docs are in sync. This is non-negotiable; the review runs on the
LOCAL diff and the push is the FIRST time anything leaves your machine.

After the review returns clean:

```bash
git push -u origin HEAD
gh pr create --base "$BASE" --title "{prefix}: {description}" --body "$(cat <<'EOF'
<use reference/PR-TEMPLATE.md>
EOF
)"
```

If `vcs.assign_reviewer` is true, assign each reviewer in `vcs.reviewers` (default `copilot`):
`gh pr edit --add-reviewer <reviewer>`.

## Phase 6 — Completion

Read the task file top to bottom. Every line must be `[x]` — if any is `[ ]`, go back and finish it. Report
to the user: PR URL, review findings addressed, doc updates, any best-practices divergences waived (with
reasons), any known limitations.

## Inviolable rules

1. **Task file is the source of truth** — not your memory. Read it.
2. **Requirements can't be skipped** — ask, don't guess.
3. **Review can't be skipped** — especially for "small" changes. `/marcjimenez:code-review` runs on the local diff.
4. **Review BEFORE push.** Push + PR is the last step, only after review is clean and docs synced.
5. **Docs ship with code.** Stale docs are a review failure.
6. **Never commit to the base branch.** Branch + PR always.
7. **Never stop with unchecked tasks.**
8. **Fresh base branch first.** Stale branches = conflicts.
9. **Climb the Ladder before writing code** (`/marcjimenez:reuse`); never cut a guardrail (`/marcjimenez:coding-style`).
