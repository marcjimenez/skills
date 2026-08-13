# Review depth — config schema

Path derivation (`CONFIG_HOME`/`REPO_KEY`), the 4-source precedence, the tier→reviewer presets, and the
first-run flow all live in `SKILL.md`. This file owns the JSON schema and field semantics.

## Layout (never in the target repo)

```
$CONFIG_HOME/global/config.json               # global default (written on first run)
$CONFIG_HOME/repos/<REPO_KEY>/config.json     # per-repo override (optional)
$CONFIG_HOME/repos/<REPO_KEY>/runs/<slug>/    # durable artifacts (research.md, plan.md, todo.md)
```

Nothing is ever written into the target repository — no `.gitignore` edits, no committed config, no
CLAUDE.md marker block. Config and artifacts live only under `$CONFIG_HOME`.

## Tier is a pool, not a fixed roster

The tier sets the POOL of reviewers eligible to run. Before running, the triage in `SKILL.md` §0.5 reads the
diff and selects the subset of that pool the change actually warrants (a docs typo skips the security
reviewer; an auth change keeps it). Set `adaptive: false` to skip triage and run the whole pool — the old
fixed-roster behavior. Triage only NARROWS the pool; it never adds a reviewer the tier excludes.

A separate `/marcjimenez:best-practices` audit runs on every review regardless of tier or triage — it is not a
pool reviewer. Its findings are blocking as a class: each must be resolved or explicitly waived. See
`SKILL.md` §1–4.

## Merge nuance

Deep-merge per leaf field: a per-repo file that sets only `tier` still inherits `confidence_threshold`,
`max_rounds`, etc. from global. `reviewers[]` replaces wholesale and is read only when `tier="custom"`.

## Schema (with example values)

```json
{
  "code_review": {
    "tier": "standard",
    "adaptive": true,
    "reviewers": ["convention", "logic", "security", "test", "simplicity", "reinvention"],
    "confidence_threshold": 80,
    "max_rounds": 3,
    "adversarial_verification": { "enabled": true, "votes": 3 },
    "waivers": []
  }
}
```

The Simplicity reviewer also honors the top-level `defaults.ponytail_intensity` (owned by CONFIG-SCHEMA).

| Field | Type | Meaning |
|-------|------|---------|
| `code_review.tier` | `quick\|standard\|paranoid\|custom` | preset selector; drives the reviewer POOL |
| `code_review.adaptive` | bool | triage the diff to a reviewer subset (default `true`); `false` runs the whole pool |
| `code_review.reviewers` | string[] | reviewer slugs forming the pool; read ONLY when `tier="custom"` |
| `code_review.confidence_threshold` | int 0–100 | drop adversarial-reviewer findings below this (best-practices findings are exempt — they block until resolved or waived) |
| `code_review.max_rounds` | int | fix/re-review loop cap |
| `code_review.adversarial_verification.enabled` | bool | run verifier voting on critical/high findings |
| `code_review.adversarial_verification.votes` | int, odd | independent verifier passes per finding; a majority must CONFIRM to report it |
| `code_review.waivers` | array | recorded best-practices waivers `{area, divergence, reason}`; a finding matching a waiver is not re-flagged on future reviews |

Reviewer slugs (8): `convention, logic, security, test, simplicity, performance, documentation, reinvention`.

Presets (`quick`/`standard`/`paranoid`), the triage mapping, and the first-run flow: see `SKILL.md`.
