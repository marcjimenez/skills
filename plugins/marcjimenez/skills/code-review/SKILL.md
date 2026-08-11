---
name: code-review
description: >-
  Runs the adversarial multi-reviewer audit on a LOCAL diff before any push or PR. Configurable panel —
  Convention, Logic, Security, Test, Simplicity/YAGNI, Performance, Documentation, Reinvention/DRY — at a
  user-chosen depth persisted in config. MUST run after implementation is complete and BEFORE git push /
  gh pr create whenever a code diff exists. Use PROACTIVELY at the pre-PR gate. Triggers on: "review this",
  "before the PR", "ready to push", a finished feature, pre-merge. Reviews the local diff and does NOT push.
---

# Code review — adversarial panel on the local diff

The review runs on the LOCAL diff. It does NOT push and does NOT create a PR — that is the caller's job,
after this returns clean.

## 0. Load review configuration (always first)

Resolve config by deep-merging these sources, highest precedence first; for each field take the first
source that defines it. Read each with the Read tool — a missing file contributes nothing and is not an
error. Read the `defaults` and `code_review` objects, plus `vcs.base_branch` (default `main`) → `$BASE`.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

1. Inline args on this invocation (`--tier`, `--reviewers`, `--threshold`) — ephemeral, never written.
2. `$CONFIG_HOME/repos/$REPO_KEY/config.json` — per-repo override.
3. `$CONFIG_HOME/global/config.json` — global user default.
4. Built-in `standard` preset (below).

**If none of files 2–3 exist → FIRST RUN (do NOT run a long questionnaire):** ask ONE AskUserQuestion —
"How deep should code review go on this repo?" options `quick (3)`, `standard (6)`, `paranoid (8)`,
`Customize…`. A tier pick → write it to `$CONFIG_HOME/global/config.json` and proceed (never re-asked, any
repo). `Customize…` → tell the user to run `/marcjimenez:setup`; proceed THIS run with `standard`. Headless (can't
prompt) → write `standard` to global, print one line, proceed.

Full JSON schema and field semantics: `reference/REVIEW-DEPTH.md`.

### Resolve the reviewer set

- tier in {quick, standard, paranoid} → use the baked-in set; ignore `reviewers`.
- tier == custom → use `reviewers` verbatim.

```
quick:    logic, security, reinvention
standard: convention, logic, security, test, simplicity, reinvention
paranoid: convention, logic, security, test, simplicity, performance, documentation, reinvention
```

Apply `defaults.ponytail_intensity` (default `full`) to the Simplicity reviewer.

## 0.5 Commit first, and treat writing agents as dangerous

**Commit the work before launching anything that can write.** A reviewer or mutation tester edits source to
prove a finding, and its restore step is usually `git checkout -- <file>`, which silently discards *your*
uncommitted work in that file.

This has happened. Five fixes were reverted twice mid-review, and one revert left an `if` block deleted
that had been removed to prove a mutation — which would have shipped a field admins could never change.
It was caught by the type checker and the linter, not by noticing.

- Commit before delegating. A clean tree makes `git checkout` harmless.
- Never run two writing agents against the same file.
- After any agent that mutated source: re-run typecheck, lint and tests, and diff against the commit.
  Do not trust a "restored" claim.

## 0.6 Two cheap greps worth running every time

Both caught defects that six prose-reading reviewers missed.

```bash
# A control byte makes a file binary to git, so its entire content is invisible in every diff, now and
# in future PRs. A NUL used as a map delimiter hid 3.6KB of new code from the whole panel.
git diff "$BASE"...HEAD --stat | grep -i " Bin " && echo "^ binary to git: unreviewable"
```

## 0.7 Mocks cannot verify a foreign engine

Raw SQL, regexes over real input, and wire-format strings must be **executed** against the real engine
before being called verified. A mocked `query()` proves the code path, never the statement. Two defects in
one change passed unit tests and prose review and appeared only on execution: a bind parameter the
warehouse refused to type (`-$1` over `unknown`), and an `ESCAPE '\'` clause that left the string literal
unterminated because that engine reads a backslash inside a literal as its own escape.

## 1. Launch the selected reviewers in parallel

Each reviewer receives the full local diff. Inside `/marcjimenez:implement` (work already committed) that is
`git diff "$BASE"...HEAD`. For a standalone review with uncommitted work, include the working tree too:
`git diff $(git merge-base "$BASE" HEAD)` (committed + staged + unstaged). Also give each reviewer any CLAUDE.md
/ CONTRIBUTING / style guides, the relevant docs for the touched area, and the instruction to be RUTHLESSLY
adversarial — assume the code is broken and prove it. A review that finds nothing is a failed review — dig
deeper.

Every reviewer operates under these robustness rules:
- Read the ACTUAL surrounding code, not just the diff hunks.
- Every finding needs a concrete trigger: a specific input, sequence, or state.
- Trace each changed value end to end.
- Assume hostile inputs, concurrent callers, and partial failure at every boundary.
- Self-check: "Could I defend this to a staff engineer with a runnable repro?" If not, drop it or lower
  confidence.

Output format per finding:
```
[CONFIDENCE: 0-100] [SEVERITY: critical|high|medium|low]
FILE:LINE — Problem. Concrete trigger/repro. Fix.
```

The exact prompt for each of the 8 reviewers: `reference/REVIEWERS.md`. Run only the selected ones.

## 2. Triage

- Discard findings below `confidence_threshold` (default 80).
- If `adversarial_verification.enabled`, run `votes` (odd) independent verifier passes on each
  critical/high-severity finding; report only if a majority CONFIRM.
- Group: critical → high → medium → low. Critical/high = must fix. Medium = fix if easy. Low = note.
- Documentation findings: fix the docs in the same pass. Code and docs ship together.

## 3. Fix + re-review (max `max_rounds`, default 3)

Fix all critical/high (including doc updates); re-run ONLY the affected reviewers; fix new findings. After
`max_rounds`, surface anything remaining as "known limitations" for the caller's PR description.

## 4. Documentation sync gate

Before returning clean, confirm: every flagged doc is updated or consciously deferred (with reason); new
public behavior is documented; no doc example/snippet is now broken.

Return clean → the caller (`/marcjimenez:implement`) proceeds to push + PR.

> Standalone repo-wide audit (not tied to a diff): `reference/AUDIT-MODE.md`.
