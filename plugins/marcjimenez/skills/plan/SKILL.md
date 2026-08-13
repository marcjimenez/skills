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

Present the plan summary (1-2 sentences of what will be built and what will be reused), then ask for implementation approval using AskUserQuestion:

> Plan ready at `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/plan.md`
> 
> [1-2 sentence summary]
> 
> Proceed with implementation?

If user confirms (yes / y / go / proceed / build / build it / let's do it / confirmed):
  Invoke /marcjimenez:implement using the Skill tool:
  
  ```
  Skill({
    skill: "marcjimenez:implement",
    args: ""
  })
  ```
  
  Implement will auto-detect the plan artifacts (research.md, plan.md) by slug and adopt them.

If user declines (no / n / not yet / later / skip):
  Exit cleanly:
  
  > Plan saved. Run `/marcjimenez:implement` when you're ready to build.

If user wants to review first (show / review / details / show me the plan):
  Display the full plan.md contents, then re-ask the approval question.
