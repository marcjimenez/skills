# Plan template

Write to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/plan.md`:

````markdown
# Plan — <slug>
Status: draft | approved   ·   Ponytail: <level>   ·   Research: runs/<slug>/research.md

## Context & problem
The understood problem (from the confirmed requirements): why this change, what it must achieve.

## Constraints & non-goals
What's explicitly out of scope; hard constraints (perf, compat, deadlines).

## Approach
The single chosen design in prose. A mermaid diagram if it clarifies flow.

## Reuse decisions (from the Ladder)
For each new piece: highest rung reached, what we reuse (import path), what we deliberately DON'T build.
| Need | Rung | Reuse this | Import / source | Not building |
|------|------|-----------|-----------------|--------------|

## Code examples
Concrete snippets adapted to this repo's conventions. Each cites its source.
```lang
// example, adapted from <source>
```

## Risks & open questions
Incl. anything unverified from the research brief §7.

## Verification plan
Observable checks that prove it works — these become `implement`'s `verify:` fields.

## Task seed
- [ ] <atomic task> — verify: <exact check>
- [ ] <atomic task> — verify: <exact check>

## Sources
Citations copied from the research brief (URLs pinned to commit SHAs).
````

The **Task seed** is the clean handoff: `/marcjimenez:implement` consumes it to build the durable task file.
