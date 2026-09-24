---
name: code-review
description: >-
  Reviews a LOCAL diff for the two things a PR bot reads past: whether each piece reinvents something a
  library, the framework, the stdlib or this repo already provides, and whether it is written and commented
  to be maintained. Two agents run it: a unit-by-unit reuse and maintainability audit, and a best-practices
  audit against the tech stack's own documentation, both caching what they learn so later runs are cheaper.
  Correctness, security, tests and performance are left to the PR reviewer. MUST run after implementation
  and BEFORE git push / gh pr create whenever a code diff exists. Use PROACTIVELY at the pre-PR gate.
  Triggers on: "review this", "before the PR", "ready to push", a finished feature, pre-merge. Does NOT push.
---

# Code review — reuse, maintainability, and what the docs say

Two agents, on the LOCAL diff. This does not push and does not open a PR; that is the caller's job once it
returns clean. This is narrow on purpose: Copilot already reviews the PR for correctness, security,
test gaps, performance and style. What it does not do is search the repo and the dependency tree for the
thing you just rewrote, or read a technology's own documentation to see how it expects to be used.

## 0. Load config

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

Read `$CONFIG_HOME/repos/$REPO_KEY/config.json`, then `$CONFIG_HOME/global/config.json`, taking the first
that defines each field; a missing file contributes nothing and is not an error. Fields used:
`vcs.base_branch` (default `main`) → `$BASE`, `code_review.max_rounds` (default 3), and
`code_review.waivers`. Full schema: `/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`.

**Commit before delegating.** An agent that edits source to prove a finding restores with
`git checkout -- <file>`, which silently discards uncommitted work in that file; a clean tree makes that
harmless. After any agent that touched source, re-run typecheck, lint and tests rather than trusting a
"restored" claim.

```bash
# A control byte makes a file binary to git, hiding its whole content from every diff, now and later.
git diff "$BASE"...HEAD --stat | grep -i " Bin " && echo "^ binary to git: unreviewable"
```

## 1. Size the review

Review `git diff "$BASE"...HEAD` when the work is committed (the `/marcjimenez:implement` case), or
`git diff $(git merge-base "$BASE" HEAD)` for a standalone review with a dirty tree.

Count the changed units: new or changed functions, helpers, classes, types, modules, and public config
surfaces. One file and a handful of units is a **small** diff: agent 1 makes one pass over the whole change
and returns one verdict. Anything larger is **deep**: enumerate the units as a checklist, batching trivial
ones (renames, constants, pure config) onto one line and giving each of the rest its own box.

Either way the run keeps one file, `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/review.md`, with a `## Checklist`
section that a small diff leaves out and a `## Verdicts` section that starts empty and is filled in §2.
Print which mode ran in one line, so a skipped deep pass is visible rather than silent.

## 2. Agent 1 — reuse, maintainability, comments

Launch it with the prompt, the cache rules, and the output format in `reference/UNIT-AUDIT.md`. A subagent
resolves none of §0 for itself, so hand over the expanded absolute paths rather than the variable names:

- the diff, the `review.md` checklist on a deep diff, and any CLAUDE.md or CONTRIBUTING for the touched area
- `$CONFIG_HOME/practices/` and `$CONFIG_HOME/repos/$REPO_KEY/utilities.md`, the two caches it reads
- `defaults.ponytail_intensity` (default `full`), which decides how hard it cuts
- the three files the prompt defers to, by absolute path, so nothing sits two hops from here and risks a
  partial read: `reuse/reference/CLIMB-THE-LADDER.md`, `reuse/reference/REINVENTION-CATALOG.md`, and
  `coding-style/reference/COMMENTS.md`

It returns its verdicts rather than writing them. You replace the `## Verdicts` section of `review.md` with
its `VERDICTS` block, and fold its `UTILITIES` block into `utilities.md`, dropping any entry it reported as
no longer resolving. Agent 2 writes its own brief under `practices/`, which no other agent touches.

## 3. Agent 2 — best practices

In parallel, invoke `/marcjimenez:best-practices` in `review` mode on the same diff. It reads or writes a
brief per technology under `$CONFIG_HOME/practices/`, so the documentation research is paid for once and
reused by every later run and every other repo.

Its findings are **blocking as a class**: each must be resolved (the code changed to match the prior art)
or explicitly waived with a stated reason. Waivers persist in `code_review.waivers` so an accepted
divergence is not re-litigated on the next PR.

## 4. Fix, then re-review

Fix the findings and re-run only the affected agent, up to `max_rounds`. After that, surface anything left
as known limitations for the caller's PR description. Best-practices findings are the exception and cannot
be deferred.

## 5. Return clean

- [ ] Every checklist box carries a verdict, or the small-diff pass returned one for the whole change.
- [ ] Every best-practices finding is resolved or waived with a reason.
- [ ] Docs flagged by a finding are updated in this pass, or deferred with a reason.
- [ ] `utilities.md` and any brief written this run are on disk, so the next run is cheaper.

Then the caller (`/marcjimenez:implement`) proceeds to push and open the PR.

> Standalone repo-wide sweep, not tied to a diff: `reference/AUDIT-MODE.md`.
