---
name: plan
description: Produce a research-backed implementation plan with concrete code examples before any code is written.
disable-model-invocation: true
---

# keel plan

Turn an understood problem into an implementable plan grounded in real evidence, with code examples and
explicit reuse decisions. Writes a plan artifact; does NOT write product code.

## Steps

1. **Pin the requirements.** Invoke `/keel:requirements` until the spec is unambiguous and confirmed. Skip
   only if the user already handed you a confirmed spec.

2. **Research (depth).** Invoke `/keel:research` in `depth` mode on the confirmed problem: reuse hunt
   first, then GitHub examples, official docs (Context7/WebFetch), best practices, and adversarial
   verification of load-bearing claims. It writes a research brief to
   `$KEEL_HOME/repos/$REPO_KEY/runs/<slug>/research.md`.

3. **Decide build-vs-reuse.** Invoke `/keel:reuse` and record, for each new piece, the highest ladder rung
   that holds — what you will reuse (with import paths) and what you will therefore NOT build.

4. **Write the plan** to `$KEEL_HOME/repos/$REPO_KEY/runs/<slug>/plan.md` using
   `reference/PLAN-TEMPLATE.md`. The plan MUST contain concrete **code examples** adapted to the repo's
   conventions, each with a source citation, plus a **Task seed** of atomic checkboxes with `verify:`
   fields.

```bash
KEEL_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/keel"   # Windows: %APPDATA%\keel
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

The plan artifact lives under `$KEEL_HOME` — never inside the target repo.

## End

Present the plan, then suggest the next command — do not run it yourself:

> Plan ready at `<path>`. Run `/keel:implement` to build it.
