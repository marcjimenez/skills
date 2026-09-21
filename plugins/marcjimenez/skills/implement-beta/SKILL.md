---
name: implement-beta
description: >-
  Opt-in trial of the build cycle with a required end-to-end verification phase. Same as
  /marcjimenez:implement (branch, requirements, task tracking, build loop, review, PR) plus a phase that
  runs the feature against a real environment before code review, and a PR body carrying the completed
  task list. Invoke it by name; it never auto-triggers.
disable-model-invocation: true
---

# marcjimenez implement-beta

> **Beta.** This is `/marcjimenez:implement` plus Phase 6, which proves the feature actually works against
> a running system before review sees it. The stable `/marcjimenez:implement` is unchanged and still owns
> the automatic triggers. Promotion criteria are in the repo README.

The full build cycle. You are bound to it until every task box is `[x]`. No shortcuts, no early exits. The
only valid exit is a fully-checked task file with a merge-ready PR.

## Phase 0 — Claim the issue

Skip only when the work traces to no issue. Otherwise claim it before anything else, so a second agent finds the lock held rather than two
branches existing. This runs first for that reason: a branch created and then abandoned because the
claim was lost is wasted work and a confusing artifact.

GATE — `/marcjimenez:implement` and a parallel workspace can reach the same ticket seconds apart. Follow
`/marcjimenez:implement` `reference/CLAIM.md`: an idempotency read, then `POST /git/refs` on `refs/claims/issue-$N`, which is the
only GitHub primitive with a real compare-and-swap. A 422 means another agent holds it: stop, say so, and
exit. Losing a claim is a normal outcome.

Once the ref is yours, publish it with `in_progress_label` and an assignee so the issue shows it is taken,
and set the release trap. Labels are the visible signal; the ref is the lock.

## Phase 1 — Fresh branch

Read the `vcs` section of config.json first (schema: `/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`). Defaults:
`base_branch=main`, prefixes `feat/fix/refactor/docs`.

```bash
BASE="main"   # ← vcs.base_branch from config
git checkout "$BASE" && git pull origin "$BASE"
git checkout -b {prefix}/{slug}   # prefix ∈ vcs.branch_prefixes
```
GATE: on a fresh branch off `$BASE` with a clean working tree before proceeding. (In a pre-created workspace
branch, confirm you're on a non-base feature branch that's clean.)

## Phase 2 — Requirements

Invoke `/marcjimenez:requirements` until the spec is unambiguous and confirmed. Skip only if `/marcjimenez:plan` already
produced a confirmed spec — in that case adopt its Context and Task seed.

## Phase 3 — Task file

Invoke `/marcjimenez:task-tracking` to create (or adopt the plan's Task seed into) the durable task file at
`$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/todo.md`. Reuse the plan's `<slug>` if a plan exists (so it finds
the same `runs/<slug>/` dir); otherwise derive `<slug>` per `/marcjimenez:task-tracking`.

Add two boxes to the Ship section that the stable skill does not carry. Both carry a `verify:` naming
the artifact, because `/marcjimenez:task-tracking` only allows `[x]` once the verify passes, and a box
with no verify is an opinion:

```markdown
- [ ] End-to-end run — verify: last `Result:` line in `runs/<slug>/integration.md` is `Result: green`
- [ ] Cleanup proven — verify: that file shows a re-query per mutation, each row gone or restored
```

On a waiver run, both verifies become the waiver line itself, in the task file and the PR body.

GATE: present the task list; get confirmation before coding.

## Phase 4 — Build loop (per task)

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

## Phase 5 — Pre-PR verification

Run the quality gauntlet and self-review the local diff — nothing pushed yet. Full checklist + the ponytail
debt-ledger grep: `reference/PRE-PR-VERIFICATION.md`. Loop until clean; mark verification tasks `[x]`.

## Phase 6 — End-to-end verification (hard gate)

Sanity checks are green, so now prove the feature works. GATE — invoke `/marcjimenez:integration-test`,
and do NOT begin Phase 7 until the evidence file exists on disk:

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
RUN_DIR="$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>"            # same <slug> as Phase 3

verdict="$(grep '^Result:' "$RUN_DIR/integration.md" 2>/dev/null | tail -1 | tr -d '\r' | sed 's/[[:space:]]*$//')"
[ "$verdict" = "Result: green" ] && echo "Phase 6 green" || echo "Phase 6 NOT green"
```

That verdict is the proof, not your memory of having invoked the skill. No file means the run never
happened; `Result: failed` means it ran and did not pass. Both block Phase 7, and neither is fixed by
ticking a box. If you are about to mark these `[x]` without `Result: green` on disk, stop and run the
phase. Ticking a box you did not earn is the single failure this phase exists to prevent.

The waiver is the only other exit, and it is narrow. It applies when the diff cannot be exercised at
runtime at all: docs only, a prompt-ware or config repo, a comment fix. If the diff touches code that
runs, the waiver does not apply, however awkward the recipe is to work out. "The recipe was hard to work
out" and "the scenarios were not written" describe the work, not grounds to skip it. Record it as:

> No end-to-end surface: {reason}

in the task file box and the PR body. A mutation left standing keeps the run open no matter what else
passed.

## Phase 7 — Review, THEN PR (hard gate)

GATE — invoke `/marcjimenez:code-review` on `git diff "$BASE"...HEAD`. Do NOT run `git push` and do NOT run
`gh pr create` until it returns clean and docs are in sync. This is non-negotiable; the review runs on the
LOCAL diff and the push is the FIRST time anything leaves your machine.

If the review causes a functional change, re-run the affected scenarios from Phase 6 before pushing. A
review fix that alters behaviour invalidates the evidence gathered before it.

After the review returns clean:

```bash
git push -u origin HEAD
gh pr create --base "$BASE" --title "{prefix}: {description}" --body "$(cat <<'BODY'
<use reference/PR-TEMPLATE.md>
BODY
)"
```

If `vcs.assign_reviewer` is true, assign each reviewer in `vcs.reviewers` (default `copilot`):
`gh pr edit --add-reviewer <reviewer>`.

## Phase 8 — Completion

Read the task file top to bottom. Every line must be `[x]` — if any is `[ ]`, go back and finish it. Report
to the user: PR URL, the environment the end-to-end run targeted and its result (or the waiver and its
reason), review findings addressed, doc updates, any best-practices divergences waived (with reasons), any
known limitations.

## Inviolable rules

1. **Task file is the source of truth** — not your memory. Read it.
2. **Requirements can't be skipped** — ask, don't guess.
3. **Claim before you build.** A lost claim stops the run. The claim excludes other agents, not
   humans, so a person can still start the same work unseen.
4. **Review can't be skipped** — especially for "small" changes. `/marcjimenez:code-review` runs on the local diff.
5. **Review BEFORE push.** Push + PR is the last step, only after review is clean and docs synced.
6. **End-to-end can't be skipped silently.** Green, or a waiver with a written reason.
7. **Never leave a mutation standing.** Cleanup is proven by re-query before the PR opens.
8. **Docs ship with code.** Stale docs are a review failure.
9. **Never commit to the base branch.** Branch + PR always.
10. **Never stop with unchecked tasks.**
11. **Fresh base branch first.** Stale branches = conflicts.
12. **Climb the Ladder before writing code** (`/marcjimenez:reuse`); never cut a guardrail (`/marcjimenez:coding-style`).
