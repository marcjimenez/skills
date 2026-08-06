---
name: writing-for-agents
description: >-
  The house style for agent-facing prose. Use PROACTIVELY whenever creating or editing a skill (SKILL.md),
  CLAUDE.md, AGENTS.md, a plugin manifest description, or any document written to be consumed by an AI
  agent. Enforces the three-tier information ladder, the context-load vs cognitive-load budgets, checkable
  and exhaustive completion criteria, positive/leading-word phrasing, and pruning to a single source of
  truth. Triggers on: writing a skill, editing CLAUDE.md/AGENTS.md, authoring an agent prompt or workflow
  doc, "write a description for this skill".
---

# Writing for agents

Prose an agent reads is not documentation for humans — it competes for the context window and steers
behavior. Write accordingly.

## Three-tier information ladder

Push material down the ladder to keep the top legible:

1. **In-file steps** — the primary path the agent follows. Keep it short.
2. **In-file reference** — supporting detail the agent may need, further down the same file.
3. **Disclosed files** — `UPPERCASE.md` reference files behind a pointer, loaded only when needed.

A must-have target hidden behind a weakly-worded pointer is a variance bug. If the agent MUST do it, put it
in the steps, not behind a pointer.

## Two budgets

- **Context load** — tokens spent every turn the file is loaded. Keep SKILL.md bodies lean (< 500 lines);
  move detail into reference files loaded on demand.
- **Cognitive load** — effort to find the right instruction. Order by what the agent needs first.

## Descriptions are trigger signals

The `description` frontmatter is how a model decides to load the skill. Write it third-person, state **what
it does AND when to use it**, and be pushy with trigger phrases for model-invoked skills. For user-invoked
skills (`disable-model-invocation: true`) strip the trigger phrasing — the description is human-facing.

## Completion criteria

Make them **checkable AND exhaustive**. A vague "make it work" lets the agent stop early. List the concrete
observable checks that mean done.

## Leading words, positive phrasing

Reuse pretrained concepts; don't coin new terms (a made-up word recruits no priors). Prompt for the
behavior you want rather than steering by negation.

## Prune to a single source of truth

No duplication — one canonical home per fact, referenced elsewhere by pointer (`/marcjimenez:reuse`, not a copied
paragraph). Delete low-relevance lines. A no-op instruction that restates a model default is waste.
