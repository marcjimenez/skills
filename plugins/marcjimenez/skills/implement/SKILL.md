---
name: implement
description: >-
  Runs the full build cycle: claim the issue, branch, grill requirements, track tasks, build with
  minimalism discipline, fanning work out across worktree-isolated subagents when it will not fit one
  context window, prove the feature works against a real environment, review the local diff, and open a PR
  carrying the completed task list and its evidence. Use PROACTIVELY after a plan is approved or
  when the user says "build it", "implement", "go ahead", or confirms a plan.
---

# marcjimenez implement

The full build cycle. You are bound to it until every task box is `[x]`. No shortcuts, no early exits. The
only valid exit is a fully-checked task file with a merge-ready PR.

## Phase 0 — Claim the issue

Skip only when the work traces to no issue. Otherwise claim it before anything else, so a second agent finds the lock held rather than two
branches existing. This runs first for that reason: a branch created and then abandoned because the
claim was lost is wasted work and a confusing artifact.

GATE — `/marcjimenez:implement` and a parallel workspace can reach the same ticket seconds apart. Follow `reference/CLAIM.md`: an idempotency read, then `POST /git/refs` on `${claim_ref_prefix}${N}`, which is
the only GitHub primitive with a real compare-and-swap. Build the ref from config, never from the literal
default: the ref name is the lock identity, so a worker using a different value excludes nobody. A 422 means another agent holds it: stop, say so, and
exit. Losing a claim is a normal outcome.

Once the ref is yours, publish it with `in_progress_label` and an assignee so the issue shows it is taken.
Labels are the visible signal; the ref is the lock. Release is an explicit step once the PR is open, not a
`trap`: each tool call is its own shell, so an EXIT trap would fire the moment the claiming command
returned and hand the issue straight to the next agent.

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

## Phase 3.5 — Serial, or fan out?

Default is serial. Fan out only when the change will not fit one context window, its units are each
demoable alone, and those units can be made file-disjoint from their `files:` lines. Any one of the three
failing means serial, and saying which one failed is the whole decision.

Print the verdict in one line before Phase 4, e.g.:

> Serial: 4 tasks, 6 files, fits one window.

or

> Fan-out: 9 units, 3 file-disjoint groups, independent PRs — two units share `registry.ts` so they are
> in the same group and run in order.

Mechanics, the worker brief, the recursion guard and both reconvergence shapes: `reference/FAN-OUT.md`.
A fanned-out run replaces Phase 4 with that file's loop and rejoins here at Phase 4.5.

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

## Phase 4.5 — Post-reconvergence gate (fan-out only)

Skip on a serial run; the Phase 5 gauntlet already covers it.

After the units are back together, build and run the suite again **in the main checkout, not a worktree**.
This is blocking.

Per-unit green does not survive reconvergence: add/add conflicts in a shared registry drop code silently,
and a worktree can skip tests that read gitignored fixtures, a local database or credentials and still
report green. Every worker passing in isolation is not the claim being made. This is the only check that
sees what was actually produced.

Also reconcile what the workers reported touching against what they declared. A file edited but not
declared is not a failure by itself, but it means the partition was wrong and the next run's `files:` lines
need widening.

## Phase 5 — Pre-PR verification

Run the quality gauntlet and self-review the local diff — nothing pushed yet. Full checklist + the ponytail
debt-ledger grep: `reference/PRE-PR-VERIFICATION.md`. Loop until clean; mark verification tasks `[x]`.

## Phase 6 — End-to-end verification (hard gate)

Sanity checks are green, so now prove the feature works. GATE — invoke `/marcjimenez:integration-test`,
and do NOT begin Phase 7 until the evidence file exists on disk:

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
# One cache per REPOSITORY, keyed by the origin remote so every worktree and workspace share it.
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. A remote that is a local,
# relative or Windows path is not a portable identity, so it falls through to the path below.
REMOTE="$(git remote get-url origin 2>/dev/null || true)"
case "$REMOTE" in *://*|*@*:*) ;; *) REMOTE="" ;; esac
# Lowercase FIRST, so an upper-case scheme or a .GIT suffix is stripped by the patterns below rather
# than surviving into the key. tr, not sed's \L: BSD sed does not implement it and emits a literal L.
# GitHub treats Owner/Repo and owner/repo as one repository, so this also stops them hashing to two.
REPO_KEY="$(printf '%s' "$REMOTE" | tr '[:upper:]' '[:lower:]' \
  | sed -E 's#/+$##; s#^[a-z+]+://##; s#^[^/@]*@##; s#^[^/:]+(:[0-9]+)?[:/]##; s#\.git$##; s#[/ ]#-#g')"
case "$REPO_KEY" in ""|.|..|-*|*:*|*\\*) REPO_KEY="" ;; esac
if [ -z "$REPO_KEY" ]; then
  # --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is
  # the worktree and would split the cache. --path-format=absolute (git 2.31+) also canonicalizes.
  G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || git rev-parse --git-common-dir 2>/dev/null || true)"
  [ -n "$G" ] && G="$(cd -- "$G" 2>/dev/null && pwd -P)"
  # Only a normal checkout's common dir ends in /.git. A submodule's is .git/modules/<name> and a bare
  # repo's is the repo itself; for those the common dir IS the identity, so do not strip a parent.
  case "$G" in */.git) R="${G%/.git}" ;; *) R="$G" ;; esac
  [ -n "$R" ] && REPO_KEY="$(basename "$R" .git)-$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
fi
unset REMOTE G R   # scratch only; do not leak generic names back to the caller
[ -n "$REPO_KEY" ] || { echo "not in a git repository" >&2; exit 1; }
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
12. **Fan out only when it will not fit, and never by layer.** A unit is a vertical slice that can be
    demoed alone. Per-unit green is not the claim; the post-reconvergence gate is.
13. **Climb the Ladder before writing code** (`/marcjimenez:reuse`); never cut a guardrail (`/marcjimenez:coding-style`).
