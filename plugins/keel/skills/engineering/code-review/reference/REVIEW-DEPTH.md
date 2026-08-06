# Review depth — config schema

Path derivation (`KEEL_HOME`/`REPO_KEY`), the 4-source precedence, the tier→reviewer presets, and the
first-run flow all live in `SKILL.md`. This file owns the JSON schema and field semantics.

## Layout (never in the target repo)

```
$KEEL_HOME/global/config.json               # global default (written on first run)
$KEEL_HOME/repos/<REPO_KEY>/config.json     # per-repo override (optional)
$KEEL_HOME/repos/<REPO_KEY>/runs/<slug>/    # durable artifacts (research.md, plan.md, todo.md)
```

Nothing is ever written into the target repository — no `.gitignore` edits, no committed config, no
CLAUDE.md marker block. Config and artifacts live only under `$KEEL_HOME`.

## Merge nuance

Deep-merge per leaf field: a per-repo file that sets only `tier` still inherits `confidence_threshold`,
`max_rounds`, etc. from global. `reviewers[]` replaces wholesale and is read only when `tier="custom"`.

## Schema (with example values)

```json
{
  "code_review": {
    "tier": "standard",
    "reviewers": ["convention", "logic", "security", "test", "simplicity", "reinvention"],
    "confidence_threshold": 80,
    "max_rounds": 3,
    "adversarial_verification": { "enabled": true, "votes": 3 }
  }
}
```

The Simplicity reviewer also honors the top-level `defaults.ponytail_intensity` (owned by CONFIG-SCHEMA).

| Field | Type | Meaning |
|-------|------|---------|
| `code_review.tier` | `quick\|standard\|paranoid\|custom` | preset selector; drives the reviewer set |
| `code_review.reviewers` | string[] | reviewer slugs; read ONLY when `tier="custom"` |
| `code_review.confidence_threshold` | int 0–100 | drop findings below this |
| `code_review.max_rounds` | int | fix/re-review loop cap |
| `code_review.adversarial_verification.enabled` | bool | run verifier voting on critical/high findings |
| `code_review.adversarial_verification.votes` | int, odd | independent verifier passes per finding; a majority must CONFIRM to report it |

Reviewer slugs (8): `convention, logic, security, test, simplicity, performance, documentation, reinvention`.

Presets (`quick`/`standard`/`paranoid`) and the first-run flow: see `SKILL.md`.
