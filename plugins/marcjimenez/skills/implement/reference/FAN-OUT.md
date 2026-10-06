# Fan-out — splitting an epic across subagents, and getting it back

## Contents

When not to · The unit is vertical · Partition by declared files · The explorer ·
The worker brief · Reconvergence · The gate that sees the whole · Failure modes

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

This is the most expensive thing to get wrong. One reported team sliced a 26-ticket stack by layer and
spent roughly twenty agent runs per closed ticket, about three quarters of them rework; their own
post-mortem blamed the slicing rather than the implementations. "The backend part" and "the frontend part"
are the shape to reject, however natural they sound.

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

One Agent per unit, launched with `isolation: "worktree"` and `run_in_background: true`. Cap concurrent
workers at **4**; queue the rest.

Each brief carries exactly five things:

- **The unit**, as its demo sentence and its acceptance check.
- **Its `files:` list**, with the instruction that touching anything outside it is a stop-and-report.
- **The notes path**, as an absolute path. A subagent resolves none of the caller's variables.
- **Its tool set.** Leaf workers get no Agent tool. This is the recursion guard, and it is a tool set
  rather than a sentence because the prose version loses: one report reached 50+ agents and another
  measured 450k tokens through a worker re-spawning the instructions that told it not to.
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
2. **Never merge a worker's branch. Take its declared paths.**
   ```bash
   git checkout <worker-branch> -- <each path from that unit's files: line>
   ```
   This is the point of `files:`. A path-scoped checkout cannot carry a revert of something the unit never
   touched, which a branch merge silently can. It also makes an undeclared edit visible: a file the worker
   changed but did not declare simply does not come across.

## Reconvergence

**Independent PRs by default.** Each worker opens its own PR. This is the smaller machinery and needs no
conflict logic at all, because a unit that is genuinely independent merges on its own.

**One integration branch** when the units cannot be independent. Then: implementers merge the integration
tip into their own branch before reporting done so landing is a fast-forward, a single merger lands them in
dependency order, and the orchestrator alone edits shared manifests, lockfiles and barrel files. Those are
the files two workers always collide on, so one named owner is cheaper than any merge strategy.

State which shape was chosen and why, in one line, before dispatching. The choice is the orchestrator's,
not a setting.

## The gate that sees the whole

**Per-unit green does not survive reconvergence.** Every worker passing in isolation says nothing about the
combined result: add/add conflicts in a shared registry drop code silently, and a worktree can skip tests
that read gitignored fixtures, a local database or credentials while still reporting green.

So after reconvergence, in the **main checkout** and not a worktree, build and run the suite again. This is
blocking. It is the only check that sees what was actually produced, and it is the step most commonly
missing from published fan-out designs.

Then one `/marcjimenez:code-review` over the whole change, not per unit.

## Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| Two units implement the same concept under different names | No shared registry names in the notes | Pin them in `notes.md` before dispatch |
| A unit reports green, the merged result fails | Per-unit verification only | The post-reconvergence gate; it is why it exists |
| Agent count or token spend runs away | A worker inherited the Agent tool | Restrict the leaf tool set, do not ask politely |
| Everything conflicts | Units sliced by layer | Re-slice vertically; a horizontal split cannot be made disjoint |
| Review never terminates | `code-review` run mid-fan-out | Review once, at the end, over the whole change |
| A unit edits a file it never declared | `files:` was a guess | The path-scoped checkout drops it silently; the gate catches the consequence. Widen the list next time |
| A clean merge reverts the orchestrator's work | The worktree was cut from the default branch | Take declared paths, never merge the branch |
