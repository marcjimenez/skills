# marcjimenez config — full schema

The whole config file. `setup` writes it; skills read the section they need. Same cross-platform home and
precedence as everything else (inline args → per-repo → global → built-in defaults). Nothing here is ever
written into the target repo.

```
$CONFIG_HOME/global/config.json            # global default
$CONFIG_HOME/repos/<REPO_KEY>/config.json  # per-repo override (wins over global)
$CONFIG_HOME/secrets.env                    # API keys, chmod 600, sourced by skills (see below)
```

```json
{
  "defaults": { "ponytail_intensity": "full" },

  "code_review": { "adaptive": true, "...": "see /marcjimenez:code-review reference/REVIEW-DEPTH.md" },

  "resolve_code_review": { "auto_reply_bots": true, "auto_resolve": true },

  "connections": {
    "context7":   { "enabled": true,  "auth": "api_key", "env_var": "CONTEXT7_API_KEY" },
    "web_search": { "enabled": true,  "auth": "none" },
    "web_fetch":  { "enabled": true,  "auth": "none" },
    "github_cli": { "enabled": true,  "auth": "cli" }
  },

  "vcs": {
    "base_branch": "main",
    "branch_prefixes": ["feat", "fix", "refactor", "docs"],
    "assign_reviewer": true,
    "reviewers": ["copilot"]
  }
}
```

## `defaults` and `code_review`

`defaults.ponytail_intensity` (`lite|full|ultra`) is the shared minimalism default. The `code_review`
section (adaptive, reviewers, thresholds, verification, waivers) is owned and documented by
`/marcjimenez:code-review` in its `reference/REVIEW-DEPTH.md` — read that for its field detail; the candidate set
and triage mapping live in code-review's `SKILL.md`.

## `resolve_code_review`

Read by `/marcjimenez:resolve-code-review`. Both default true, so the skill works with no config.

| Field | Type | Meaning |
|-------|------|---------|
| `auto_reply_bots` | bool | post a clear rebuttal to a bot comment (Copilot, CodeRabbit) autonomously; those reviews are advisory and non-blocking (default true) |
| `auto_resolve` | bool | resolve a thread once its comment is addressed; reversible via `unresolveReviewThread` (default true) |

Rebuttals to human reviewers are always printed before posting, regardless of these knobs.

## `connections`

Which external tools the research pipeline (`/marcjimenez:research`) may use. Each entry:

| Field | Type | Meaning |
|-------|------|---------|
| `enabled` | bool | if false, the skill skips this tool and falls back to the next enabled one |
| `auth` | `none\|cli\|api_key` | how it authenticates |
| `env_var` | string | **only for `auth: "api_key"`** — the name of the env var holding the key (value lives in `secrets.env`, never here) |

**No MCP is required anywhere in marcjimenez** — every connection is the harness's own tool or a `curl`-able API.
Built-in connections: `context7` (docs via the context7.com REST API over `curl`, needs `CONTEXT7_API_KEY`;
`https://context7.com/api/v1/search` then `/api/v1/<id>?type=txt&topic=&tokens=` with an
`Authorization: Bearer` header), `web_search` and `web_fetch` (Claude's built-in tools), `github_cli` (uses
the user's existing `gh` auth). To add another keyed integration, add an entry with `auth: "api_key"` and an
`env_var`, e.g.:

```json
"some_api": { "enabled": true, "auth": "api_key", "env_var": "SOME_API_KEY" }
```

## `vcs`

Read by `/marcjimenez:implement`.

| Field | Type | Meaning |
|-------|------|---------|
| `base_branch` | string | branch to branch from, diff against, and target the PR at (default `main`) |
| `branch_prefixes` | string[] | allowed branch-name prefixes |
| `assign_reviewer` | bool | assign a reviewer after opening the PR |
| `reviewers` | string[] | reviewers to assign (e.g. `["copilot"]`) |

## `secrets.env` (API keys)

Keys for `auth: "api_key"` connections live ONLY here — never in `config.json`, never in the repo:

```bash
# $CONFIG_HOME/secrets.env — chmod 600, never commit. Sourced by marcjimenez skills.
export SOME_API_KEY='<value>'
```

Security rules: the file is `chmod 600`; the value is **single-quoted with `'` escaped as `'\''`** (the file
is executed via `.`, so an unquoted value with shell metacharacters would run — see `/marcjimenez:setup` for the
hardened write); `config.json` stores only the `env_var` NAME, never the value; skills load it with
`[ -f "$CONFIG_HOME/secrets.env" ] && . "$CONFIG_HOME/secrets.env"` immediately before the tool call and never
echo or log the value.
