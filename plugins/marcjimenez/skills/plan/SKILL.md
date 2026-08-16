---
name: plan
description: Produce a research-backed implementation plan with concrete code examples before any code is written.
disable-model-invocation: true
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
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

The plan artifact lives under `$CONFIG_HOME` — never inside the target repo.

## End

Present the plan summary (1-2 sentences of what will be built and what will be reused), then hand off. Do NOT
invoke `/marcjimenez:implement` yourself: it is user-invoked only (`disable-model-invocation`), so the Skill tool
blocks it. Tell the user to run it:

> Plan ready at `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/plan.md`
>
> [1-2 sentence summary]
>
> Run `/marcjimenez:implement` to build it — it picks up this plan's artifacts (research.md, plan.md) by slug.

If the user asks to review first, display the full plan.md, then repeat the run line.
