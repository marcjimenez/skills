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
KEEL_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/keel"   # Windows: %APPDATA%\keel
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

1. Inline args on this invocation (`--tier`, `--reviewers`, `--threshold`) — ephemeral, never written.
2. `$KEEL_HOME/repos/$REPO_KEY/config.json` — per-repo override.
3. `$KEEL_HOME/global/config.json` — global user default.
4. Built-in `standard` preset (below).

**If none of files 2–3 exist → FIRST RUN (do NOT run a long questionnaire):** ask ONE AskUserQuestion —
"How deep should code review go on this repo?" options `quick (3)`, `standard (6)`, `paranoid (8)`,
`Customize…`. A tier pick → write it to `$KEEL_HOME/global/config.json` and proceed (never re-asked, any
repo). `Customize…` → tell the user to run `/keel:setup`; proceed THIS run with `standard`. Headless (can't
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

## 1. Launch the selected reviewers in parallel

Each reviewer receives the full local diff. Inside `/keel:implement` (work already committed) that is
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

Return clean → the caller (`/keel:implement`) proceeds to push + PR.

> Standalone repo-wide audit (not tied to a diff): `reference/AUDIT-MODE.md`.
