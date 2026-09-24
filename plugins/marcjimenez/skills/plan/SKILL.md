---
name: plan
description: >-
  Produce a research-backed implementation plan with concrete code examples before any code is written.
  Use PROACTIVELY after a brainstorm concludes or when the user says "plan this", "let's plan", or selects
  an approach to expand.
---

# marcjimenez plan

Turn an understood problem into an implementable plan grounded in real evidence, with code examples and
explicit reuse decisions. Writes a plan artifact; does NOT write product code.

## Steps

1. **Pin the requirements.** Invoke `/marcjimenez:requirements` until the spec is unambiguous and confirmed. Skip
   only if the user already handed you a confirmed spec.

2. **Research (depth).** Invoke `/marcjimenez:research` in `depth` mode on the confirmed problem: reuse hunt
   first, then GitHub examples, official docs (Context7/WebFetch), best practices, and adversarial
   verification of load-bearing claims. It writes a research brief to
   `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/research.md`.

3. **Decide build-vs-reuse.** Invoke `/marcjimenez:reuse` and record, for each new piece, the highest ladder rung
   that holds — what you will reuse (with import paths) and what you will therefore NOT build.

4. **Check prior art.** Invoke `/marcjimenez:best-practices` in `advisory` mode on the chosen approach so the plan
   reflects proven design patterns and idiomatic dependency use, not just a workable sketch. It builds on the
   research brief from step 2; fold its guidance into the code examples in the next step.

5. **Write the plan** to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/plan.md` using
   `reference/PLAN-TEMPLATE.md`. The plan MUST contain concrete **code examples** adapted to the repo's
   conventions, each with a source citation, plus a **Task seed** of atomic checkboxes with `verify:`
   fields.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
# One cache per REPOSITORY, keyed by the origin remote so every worktree and workspace share it.
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. Lowercased with tr, not
# sed's \L, which BSD sed does not implement and silently turns into a literal L.
REPO_KEY="$(git remote get-url origin 2>/dev/null \
  | sed -E 's#^([a-z+]+://[^/]+/|[^/:]+:)##; s#\.git$##; s#[/ ]#-#g' | tr '[:upper:]' '[:lower:]')"
# A local-path remote leaves a leading '-', which every coreutils tool reads as an option; an unknown
# scheme leaves a ':'. Either way the repo path below is the better identity, so fall through.
case "$REPO_KEY" in ""|-*|*:*) REPO_KEY="" ;; esac
# --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is the
# worktree and would split the cache. --path-format=absolute makes it absolute AND canonical.
[ -n "$REPO_KEY" ] || REPO_KEY="$(G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
  && [ -n "$G" ] && R="$(dirname "$G")" \
  && printf '%s-%s' "$(basename "$R")" "$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
[ -n "$REPO_KEY" ] || { echo "not in a git repository" >&2; exit 1; }
```

The plan artifact lives under `$CONFIG_HOME` — never inside the target repo.

## End

Present the plan summary (1-2 sentences of what will be built and what will be reused), then ask for approval:

> Plan ready at `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/plan.md`
>
> [1-2 sentence summary]
>
> Proceed with implementation?

If the user confirms (yes / y / go / proceed / build / build it / approved):
  Invoke `/marcjimenez:implement` — it auto-detects this plan's artifacts (research.md, plan.md) by slug.
  If the plan carries Integration scenarios and the user wants them run as part of the build, offer
  `/marcjimenez:implement-beta` instead: same cycle, plus a required end-to-end phase before review.

If the user wants to review first (show / review / details):
  Display the full plan.md contents, then re-ask.

If the user declines (no / not yet / later):
  > Plan saved. Run `/marcjimenez:implement` when ready.

Either way, if no issue tracks this work yet, offer one before you finish:

> No ticket tracks this. Draft one from the plan?

On yes, invoke `/marcjimenez:issue`. The plan already carries what an agent-ready ticket needs, so this is
a handoff rather than fresh drafting: Approach becomes What to build, the Task seed's verifies become
Acceptance criteria, the files named in Reuse decisions and Code examples become Files, and Constraints
and non-goals become the scope boundary. A ticket that passes `/marcjimenez:issue`'s readiness gate can be
picked up later without this session's context.
