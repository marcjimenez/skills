---
name: code-review
description: >-
  Runs the adversarial multi-reviewer audit on a LOCAL diff before any push or PR. A triage pass reads the
  diff and runs only the reviewers it warrants from the full set of eight — Convention, Logic, Security,
  Test, Simplicity/YAGNI, Performance, Documentation, Reinvention/DRY — plus a mandatory best-practices audit
  against real-world GitHub patterns. MUST run after implementation is complete and BEFORE git push / gh pr
  create whenever a code diff exists. Use PROACTIVELY at the pre-PR gate. Triggers on: "review this", "before
  the PR", "ready to push", a finished feature, pre-merge. Reviews the local diff and does NOT push.
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

1. Inline args on this invocation (`--reviewers`, `--threshold`, `--no-adaptive`) — ephemeral, never written.
2. `$CONFIG_HOME/repos/$REPO_KEY/config.json` — per-repo override.
3. `$CONFIG_HOME/global/config.json` — global user default.
4. Built-in defaults (below).

Review works out of the box — there is no first-run questionnaire and no depth tier to choose. Triage adapts
to each diff automatically.

Full JSON schema and field semantics: `reference/REVIEW-DEPTH.md`.

### The reviewer candidate set

Triage (§0.5) selects from a candidate set of all eight reviewers by default:
`convention, logic, security, test, simplicity, performance, documentation, reinvention`.

- `code_review.reviewers` (string[], optional) REPLACES the candidate set when present — triage picks only
  from these. Use it to permanently drop a reviewer a repo never needs (e.g. omit `documentation` in a repo
  with no docs). Omit it to keep all eight in play.
- `code_review.adaptive` (default `true`): set `false` to skip triage and run the entire candidate set every
  time.

Apply `defaults.ponytail_intensity` (default `full`) to the Simplicity reviewer.

## 0.5 Triage — select the reviewers this diff warrants

Read the diff first, then pick from the candidate set ONLY the reviewers whose concern the change actually
raises. The goal is a relevant panel, not a big one: a docs typo does not need the security reviewer; an auth
change must have it. This is the fix for reviews that felt heavy-handed — you run three sharp reviewers, not
eight rote ones. Map the diff to reviewers:

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

`logic` and `reinvention` are the floor for any change carrying real code — include them whenever they are in
the candidate set. Triage only NARROWS the candidate set; it never runs a reviewer the set excludes. If the
set was trimmed via `code_review.reviewers` to omit one of them, honor that and state plainly that no
correctness/reinvention reviewer ran. If triage would otherwise select nothing (pure formatting or
whitespace), run `logic` when it is in the set and say why.

Print the decision in one block before running, e.g.:
> Reviewing with: logic, security, reinvention — auth-touching diff that adds a new helper.
> Skipped: convention, test, simplicity — no new files, existing tests cover it, net deletion.

## 0.6 Commit first, and treat writing agents as dangerous

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

## 0.7 Two cheap greps worth running every time

Both caught defects that six prose-reading reviewers missed.

```bash
# A control byte makes a file binary to git, so its entire content is invisible in every diff, now and
# in future PRs. A NUL used as a map delimiter hid 3.6KB of new code from the whole panel.
git diff "$BASE"...HEAD --stat | grep -i " Bin " && echo "^ binary to git: unreviewable"
```

## 0.8 Mocks cannot verify a foreign engine

Raw SQL, regexes over real input, and wire-format strings must be **executed** against the real engine
before being called verified. A mocked `query()` proves the code path, never the statement. Two defects in
one change passed unit tests and prose review and appeared only on execution: a bind parameter the
warehouse refused to type (`-$1` over `unknown`), and an `ESCAPE '\'` clause that left the string literal
unterminated because that engine reads a backslash inside a literal as its own escape.

## 1. Launch the selected reviewers + the best-practices audit (parallel)

Launch the reviewers triage selected in §0.5, and IN PARALLEL invoke `/marcjimenez:best-practices` in `review`
mode on the same diff. The best-practices audit runs on EVERY review — it is not one of the eight candidate
reviewers and triage never drops it — and judges the diff against how well-regarded projects do the same thing.

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
