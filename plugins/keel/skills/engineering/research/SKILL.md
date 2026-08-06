---
name: research
description: >-
  Gathers real evidence BEFORE code is written. Use PROACTIVELY before implementing against any unfamiliar
  library, framework, API, or pattern, and inside planning. Reads CLAUDE.md and maps the target area, greps
  the repo for existing utilities to reuse, searches GitHub for real implementation examples, pulls current
  official docs via the Context7 REST API or WebFetch (no MCP required), and checks best practices and
  known pitfalls. It also evaluates whether a NEW dependency is worth its maintenance cost. Triggers on: an
  unfamiliar API, "how does X work", a new dependency, "is there an existing helper", planning, or any
  implementation lacking a proven pattern.
---

# Research — evidence before code

Given an understood problem, gather proof before writing anything. The output is a research brief that
feeds `/keel:plan` and `/keel:brainstorm`. Two modes (the caller passes one):

- **depth** — full pipeline + adversarial verification of load-bearing claims. Used by `plan` on the one
  chosen approach.
- **breadth** — one shallow survey pass, skip per-claim verification, fast. Used by `brainstorm` to map
  the option space.

## Connections: use only what's enabled

Before any external call, read the `connections` section of config.json (schema + how it's stored:
`/keel:setup` `reference/CONFIG-SCHEMA.md`). Use ONLY connections marked `enabled`; if one is off, fall back
to the next enabled source. For a connection with `auth: "api_key"`, load its key immediately before the
call and never echo it:

```bash
KEEL_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/keel"   # Windows: %APPDATA%\keel
[ -f "$KEEL_HOME/secrets.env" ] && . "$KEEL_HOME/secrets.env"
```

If no config resolves, all built-in connections are on by default. If every external connection is off,
say so in the brief and rely on the reuse hunt + repo evidence alone.

## Pipeline (laziest answer first)

1. **Reuse hunt FIRST (ladder rungs 1-5).** The laziest research result is "we already have it." Apply the
   Climb-the-Ladder doctrine — see `/keel:reuse`. grep the repo (`shared`/`utils`/`common`/`lib`, siblings);
   read `package.json` / `pyproject.toml` / `go.mod` ("is lodash already available?"); check framework
   built-ins and stdlib. If a rung ≤5 fully covers a need, record it and STOP external search for that need.
2. **GitHub implementation examples** (if `github_cli` enabled) — `gh search code`, `gh search repos`, then
   fetch the exact snippet pinned to a commit SHA. Technique in `reference/RESEARCH-PLAYBOOK.md`.
3. **Official docs** — the Context7 REST API via `curl` (no MCP required) if `context7` enabled + its key
   is set; else WebFetch (if `web_fetch` enabled) for the doc site. Endpoints in `reference/RESEARCH-PLAYBOOK.md`.
4. **Best practices & pitfalls** (if `web_search` enabled) — WebSearch for footguns, version-specific
   gotchas, security advisories; cross-check each against the docs from step 3.
5. **Adversarial verification (depth only)** — confirm every load-bearing claim (this API exists, this is
   the current signature, this snippet compiles under our version) against a second independent source
   before it enters the brief. Reuse the installed `deep-research` skill's fan-out/verify harness rather
   than building a new verifier.
6. **Synthesize the brief** — write it per the format in `reference/RESEARCH-PLAYBOOK.md` to
   `$KEEL_HOME/repos/$REPO_KEY/runs/<slug>/research.md`.

The brief MUST deliver: sources with URLs, reusable utilities with import paths + why, best-practice notes,
and concrete code examples to embed in the plan.
