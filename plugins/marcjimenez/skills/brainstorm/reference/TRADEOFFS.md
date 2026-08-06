# Brainstorm output format

Write to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/brainstorm.md`:

````markdown
# Brainstorm — <slug>
Problem: <understood problem>   ·   Ponytail: <level>   ·   Research: runs/<slug>/research.md (breadth)

## Options
### Option A — <name>
Thesis: <one line>
Sketch:
```lang
<rough shape: interface / pseudocode / architecture bullets>
```
Reuse/ladder: <highest rung this option can reach>
Pros: … · Cons: … · Risk: L/M/H · Effort: S/M/L

### Option B — …
### Option C — …

## Comparison
| Option | Reuse rung | Risk | Effort | New deps | Blast radius |
|--------|-----------|------|--------|----------|--------------|
| A | 5 | L | S | none | small |

## Recommendation
<chosen option + why> → hand to /marcjimenez:plan to expand into a full plan.
````

`brainstorm` diverges (many approaches, breadth research, never committed); `plan` converges (one approach,
depth research, code examples, task seed). Compose them: brainstorm → pick winner → `/marcjimenez:plan` on it.
