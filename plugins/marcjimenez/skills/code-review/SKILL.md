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
returns clean. The panel is narrow on purpose: Copilot already reviews the PR for correctness, security,
test gaps, performance and style. What it does not do is search the repo and the dependency tree for the
thing you just rewrote, or read a technology's own documentation to see how it expects to be used.

## 0. Load config

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
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
surfaces. One file and a handful of units is a **small** diff, and agent 1 makes one pass over the whole
change. Anything larger is **deep**: write a unit checklist to
`$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/review.md`, batching trivial units (renames, constants, pure
config) onto one line and giving each remaining unit its own box. Print which mode ran in one line, so a
skipped deep pass is visible rather than silent.

## 2. Agent 1 — reuse, maintainability, comments

Launch it with the prompt, the cache rules, and the output format in `reference/UNIT-AUDIT.md`. Hand it the
diff, the unit checklist, and any CLAUDE.md or CONTRIBUTING for the touched area.

## 3. Agent 2 — best practices

In parallel, invoke `/marcjimenez:best-practices` in `review` mode on the same diff. It reads or writes a
brief per technology under `$CONFIG_HOME/practices/`, so the documentation research is paid for once and
reused by every later run and every other repo.

Its findings are **blocking as a class**: each must be resolved (the code changed to match the prior art)
or explicitly waived with a stated reason. Waivers persist in `code_review.waivers` so an accepted
divergence is not re-litigated on the next PR.

## 4. Fix, then re-review

Fix the findings and re-run only the affected agent, up to `max_rounds`. After that, surface anything left
as known limitations for the caller's PR description, except unresolved best-practices findings, which
must be resolved or waived and cannot be deferred.

## 5. Return clean

- [ ] Every unit in the checklist carries a verdict.
- [ ] Every best-practices finding is resolved or waived with a reason.
- [ ] Docs flagged by a finding are updated in this pass, or deferred with a reason.
- [ ] `utilities.md` and any brief written this run are on disk, so the next run is cheaper.

Then the caller (`/marcjimenez:implement`) proceeds to push and open the PR.

> Standalone repo-wide sweep, not tied to a diff: `reference/AUDIT-MODE.md`.
