---
name: code-review
description: >-
  Runs the adversarial multi-reviewer audit on a LOCAL diff before any push or PR. A triage pass reads the
  diff and runs only the reviewers it warrants — Convention, Logic, Security, Test, Simplicity/YAGNI,
  Performance, Documentation, Reinvention/DRY — drawn from a user-chosen depth pool, plus a mandatory
  best-practices audit against real-world GitHub patterns. MUST run after implementation is complete and
  BEFORE git push / gh pr create whenever a code diff exists. Use PROACTIVELY at the pre-PR gate. Triggers
  on: "review this", "before the PR", "ready to push", a finished feature, pre-merge. Reviews the local diff
  and does NOT push.
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

### Resolve the reviewer pool

The tier sets the POOL of reviewers eligible to run — a ceiling, not a fixed roster. The triage in §0.5
picks the subset of this pool the diff actually warrants.

- tier in {quick, standard, paranoid} → the baked-in pool below; ignore `reviewers`.
- tier == custom → the `reviewers` list is the pool.

```
quick pool:    logic, security, reinvention
standard pool: convention, logic, security, test, simplicity, reinvention
paranoid pool: convention, logic, security, test, simplicity, performance, documentation, reinvention
```

Apply `defaults.ponytail_intensity` (default `full`) to the Simplicity reviewer. Set
`code_review.adaptive: false` to skip triage and run the whole pool (the old fixed-roster behavior).

## 0.5 Triage — select the reviewers this diff warrants

Read the diff first, then pick from the pool ONLY the reviewers whose concern the change actually raises. The
goal is a relevant panel, not a big one: a docs typo does not need the security reviewer; an auth change must
have it. This is the fix for reviews that felt heavy-handed — you run three sharp reviewers, not eight rote
ones. Map the diff to reviewers:

| Include this reviewer when the diff… | Reviewer |
| --- | --- |
| adds or changes executable logic (not docs/config only) | `logic` |
| touches auth, user-input→sink, secrets, network, deserialization, file paths, SQL/shell | `security` |
| adds or changes non-trivial logic or branches | `test` |
| adds new code files or a substantial amount of code | `convention` |
| adds code, a new abstraction, or is net-additive | `simplicity` |
| touches loops, queries, hot paths, or data structures at scale | `performance` |
| changes public surface (API, flags, env, commands) or touches docs | `documentation` |
| adds any new function, helper, util, type, or dependency | `reinvention` |

`logic` and `reinvention` are the floor for any change carrying real code — but triage only NARROWS the pool,
never adds a reviewer the tier excludes. If a custom pool deliberately omits one of them, honor the pool and
state plainly that no correctness/reinvention reviewer ran. If triage would otherwise select nothing (pure
formatting or whitespace), run `logic` when it is in the pool and say why.

Print the decision in one block before running, e.g.:
> Reviewing with: logic, security, reinvention — auth-touching diff that adds a new helper.
> Skipped from pool: convention, test, simplicity — no new files, existing tests cover it, net deletion.

## 1. Launch the selected reviewers + the best-practices audit (parallel)

Launch the reviewers triage selected in §0.5, and IN PARALLEL invoke `/marcjimenez:best-practices` in `review`
mode on the same diff. The best-practices audit runs on EVERY review — it is not one of the pool reviewers and
triage never drops it — and judges the diff against how well-regarded projects do the same thing.

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
- **Best-practices findings are BLOCKING as a class.** Each finding from `/marcjimenez:best-practices` must be
  resolved (code changed to match the prior art) or explicitly WAIVED (a recorded decision that our
  divergence is justified here, with the reason stated). This is independent of `confidence_threshold`,
  which governs only the adversarial reviewers. An unwaived, unresolved best-practices finding fails the
  review. Waivers persist in the per-repo config so an accepted divergence is not re-flagged on future PRs
  (mechanism owned by `/marcjimenez:best-practices`).

## 3. Fix + re-review (max `max_rounds`, default 3)

Fix all critical/high (including doc updates) and every best-practices finding (fix or waive with a reason);
re-run ONLY the affected reviewers; fix new findings. After `max_rounds`, surface anything remaining as
"known limitations" for the caller's PR description — except unresolved best-practices findings, which must
be resolved or waived and cannot be deferred as a known limitation.

## 4. Documentation sync gate

Before returning clean, confirm: every flagged doc is updated or consciously deferred (with reason); new
public behavior is documented; no doc example/snippet is now broken; and every best-practices finding is
resolved or waived.

Return clean → the caller (`/marcjimenez:implement`) proceeds to push + PR.

> Standalone repo-wide audit (not tied to a diff): `reference/AUDIT-MODE.md`.
