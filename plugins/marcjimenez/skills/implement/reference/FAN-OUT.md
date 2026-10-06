# Fan-out — splitting an epic across subagents, and getting it back

## Contents

When not to · The unit is vertical · Partition by declared files · The explorer ·
The worker brief · A worktree is not cut from your branch · Reconvergence ·
The gate that sees the whole · Failure modes

## When not to

**If the whole change fits one context window, do not fan out.** Go straight to the serial path and say so
in one line. Fan-out costs roughly 15x the tokens of a serial run, and coding has far fewer genuinely
parallel tasks than research does. A three-file change buys a token bill and a merge problem that did not
previously exist.

Fan out only when all three hold:

1. The change will not fit one context window.
2. It splits into units that are each demoable alone (below).
3. Those units can be made file-disjoint (below). If they cannot, run them sequentially.

## The unit is vertical

A unit is a **tracer bullet**: a narrow but complete path through every layer it touches, including its
tests. It is not a layer.

The gate is one question per unit: **"what can I demo when this is done?"** A unit with no answer is a
horizontal slice and does not pass.

This is the most expensive thing to get wrong: one team that sliced by layer spent most of its agent runs
on rework. "The backend part" and "the frontend part" are the shape to reject, however natural they sound.

## Partition by declared files

Compute this, do not judge it. Each task carries a `files:` line (`/marcjimenez:task-tracking`). Group the
units so that no two units in a group name the same path. Those groups are what may run concurrently.

If no disjoint partition exists, the work is sequential. Say that and run it serially rather than hoping.

A declared list is a declaration, not a guarantee: a unit that touches something it did not declare
collides anyway. That is why the partition is a precondition and never the only check.

## The explorer

Before any implementer, run **one read-only subagent** over the area and write its notes to
`$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/notes.md`. Every implementer reads that file instead of
re-exploring, which is the difference between paying for the exploration once and paying N times.

The notes must pin **exact names for anything in a shared registry**: the error codes, the event names, the
config keys, the enum members. Two implementers inventing one concept as `blockedSince` and `blockedOn` is
the reported failure this prevents, and no amount of worktree isolation catches it.

## The worker brief

One Agent per unit, launched with `subagent_type: "fan-out-worker"`, `isolation: "worktree"` and
`run_in_background: true`.

**The recursion guard is the agent definition, not the brief.** A tool restriction cannot be passed on an
Agent call, so `${CLAUDE_PLUGIN_ROOT}/agents/fan-out-worker.md` omits the Agent tool from its `tools:` and
the brief names that type. Asking a worker in prose not to spawn is the version that loses: one report
reached 50+ agents and another measured 450k tokens through a worker re-spawning the instructions telling
it not to.

Cap concurrent workers at **4**. With `run_in_background: true` the orchestrator is notified as each
finishes, so dispatch the next one on each completion notification; without that the cap is a wish.

Each brief carries exactly five things:

- **The unit**, as its demo sentence and its acceptance check.
- **Its `files:` list**, with the instruction that touching anything outside it is a stop-and-report.
- **The notes path**, as an absolute path. A subagent resolves none of the caller's variables.
- **Its base**, as a commit or branch, with the instruction to confirm the worktree sits on it and
  `git rebase` onto it if not. A worktree shares the common `.git`, so the orchestrator's branch is
  visible from inside it.
- **What to return**: the branch name, the PR URL if it opened one, and any file it touched that was not
  on its list.

## A worktree is not cut from your branch

**Measured, not assumed.** `isolation: "worktree"` cuts the worker's worktree from the repository's
default branch, not from whatever branch the orchestrator is on. Both workers in the first real run came
back based on `origin/main` while the orchestrator sat three commits ahead on a feature branch.

Merging such a branch does not conflict. It cleanly reverts everything the orchestrator had done: a
twelve-line description change arrived carrying the deletion of a reference file, the resurrection of a
deleted skill, and the reversal of an entire merged PR. Git reports it as a successful merge.

Two rules follow, and the second is the one that saves you:

1. **Tell each worker its base explicitly**, and have it confirm the worktree sits on that base before it
   starts. A worker cannot know what the orchestrator is building on.
2. **Never merge a worker's branch. Apply a patch scoped to its declared paths.**
   ```bash
   git diff <base>..<worker-branch> -- <each path from that unit's files: line> | git apply --index -
   ```
   This is the point of `files:`. A path-scoped patch cannot carry a revert of something the unit never
   touched, which a branch merge silently can, and it fails non-zero and atomically on a real conflict.

   **Not `git checkout <branch> -- <paths>`.** Measured: when any declared path was deleted on the worker
   branch, that command errors on the missing pathspec and applies *nothing at all*, including the files
   that would have come across cleanly. The tree looks untouched and the run proceeds to a gate with
   nothing to gate. Scoping to a directory instead is worse: it returns success while resurrecting the
   deleted file and flattening a rename into a copy.

   A unit that renames declares **both** paths in its `files:` line, because the patch needs the old path
   in scope to remove it.

## Reconvergence

**One integration branch is the default inside `implement`**, because `implement` owns the review gate.
Inviolable rules 4 and 5 say the diff is reviewed before anything is pushed, and that only holds if there
is one local diff to review. Then: implementers merge the integration
tip into their own branch before reporting done so landing is a fast-forward, a single merger lands them in
dependency order taken from the tasks' `blocked-by:` lines, and the orchestrator alone edits shared
manifests, lockfiles and barrel files. Those are
the files two workers always collide on, so one named owner is cheaper than any merge strategy.

**Independent PRs** are the alternative, for units genuinely shippable alone. The machinery is smaller and
there is no conflict logic at all, but reconvergence then happens on `main` rather than locally, so two
things change and both are mandatory: each worker runs `/marcjimenez:code-review` on its own diff before
opening its PR, and the gate below moves to after the last PR merges rather than before the first push.
Phase 4.5 has nothing local to inspect under this shape.

State which shape was chosen and why, in one line, before dispatching. The choice is the orchestrator's,
not a setting.

## The gate that sees the whole

**Per-unit green does not survive reconvergence.** Every worker passing in isolation says nothing about the
combined result: add/add conflicts in a shared registry drop code silently, and a worktree can skip tests
that read gitignored fixtures, a local database or credentials while still reporting green.

So after reconvergence, in the **main checkout** and not a worktree, build and run the suite again. This is
blocking. It is the only check that sees what was actually produced.

Then one `/marcjimenez:code-review` over the whole change, not per unit.

## Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| Two units implement the same concept under different names | No shared registry names in the notes | Pin them in `notes.md` before dispatch |
| A unit reports green, the merged result fails | Per-unit verification only | The post-reconvergence gate; it is why it exists |
| Agent count or token spend runs away | A worker inherited the Agent tool | Restrict the leaf tool set, do not ask politely |
| Everything conflicts | Units sliced by layer | Re-slice vertically; a horizontal split cannot be made disjoint |
| Review never terminates | `code-review` run mid-fan-out | Review once, at the end, over the whole change |
| A unit edits a file it never declared | `files:` was a guess | The scoped patch leaves it behind; the gate catches the consequence. Widen the list next time |
| A clean merge reverts the orchestrator's work | The worktree was cut from the default branch | Apply a scoped patch, never merge the branch |
| Reconvergence applied nothing and reported it | `git checkout -- <paths>` with a deleted path | Use the `git diff \| git apply` form; check the exit status |
