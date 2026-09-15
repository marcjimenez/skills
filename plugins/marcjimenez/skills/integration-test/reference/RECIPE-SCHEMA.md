# Integration test recipe schema

How to run this repo end to end, stored in `$CONFIG_HOME/repos/$REPO_KEY/config.json` (normally per-repo,
since the recipe is repo-specific) or `$CONFIG_HOME/global/config.json`.

## Schema

```jsonc
{
  "integration_test": {
    "default_env": "prod",              // pre-selects the answer; the question is still asked every run

    "environments": {
      "prod": {
        "mutating": true,               // writes real data, so the undo plan is mandatory

        "services": [                   // started in the background, in order
          "pnpm --filter subgraph-foo dev"
        ],

        "ready_check": "curl -sf localhost:4001/health",
        "ready_timeout_seconds": 60,    // default 60; fail the run rather than proceed half-started

        "auth": {
          "command": "<cli> fetch-token --raw",
          "env_var": "API_TOKEN"        // where the captured value is bound, never printed
        },

        "endpoint": "https://api.example.com/graphql",

        "data_access": {
          "kind": "mcp",                // "mcp" or "command"
          "tool": "mcp__postgres-prod__query",
          "writable": false             // default false; true only if this channel may run a reversal
        },

        "teardown": ["<stop the backgrounded services>"]
      },

      "dev": { "...": "same shape, usually mutating: false" }
    }
  }
}
```

## Field details

### `default_env`
The environment pre-selected when the skill asks. It never skips the question. Most repos here set `prod`,
because that is where the real data lives.

### `environments.<name>.mutating`
Marks an environment as writing real data. It is advisory: it shapes how the Phase 2 question is phrased
and how loudly the run warns. It never relaxes a rule. Every scenario that issues a write needs a written
reversal before it runs, and the cleanup proof is mandatory in every environment, whatever this says. Set
it true for anything writing to a shared database, including staging.

### `services`
Commands started in the background before the run, in array order. Each should be a long-running process.
Prefer a command the repo already defines (a `package.json` script, a Make target) over an ad-hoc
invocation, so the recipe does not rot when the startup sequence changes.

### `ready_check` and `ready_timeout_seconds`
A command that exits zero once the system is actually serving. Polled until it passes. On timeout the run
fails; it never proceeds against a half-started system. Default timeout 60 seconds.

### `auth`
`command` prints a credential to stdout; the skill captures it into `env_var` and never echoes it. Prefer
an auth helper the repo or the machine already provides, such as a project CLI's token subcommand or an
installed token-fetching skill, over hand-rolled login code.

If the credential is a static key rather than something fetched, drop `command` and keep `env_var` alone;
the value lives in `$CONFIG_HOME/secrets.env` at `chmod 600`, never in `config.json`.

### `data_access`
How to read the rows a scenario wrote.

| `kind` | Extra field | Meaning |
|--------|-------------|---------|
| `mcp` | `tool` | name of an MCP query tool, e.g. `mcp__postgres-prod__query` |
| `command` | `command` | a shell command taking SQL on stdin, e.g. `psql "$DATABASE_URL" -c` |

`writable` defaults to false, meaning the channel reads and nothing more. Reversals run through the API's
own inverse operation wherever one exists. Set `writable: true` only for a repo where some mutation has no
API inverse and the reversal genuinely has to be SQL; the skill refuses to write through a channel that
has not said so.

Prefer `command` when the repo has a working CLI, since it does not assume a particular MCP server is
installed. Omit `data_access` entirely for a repo with no database; the skill then verifies through the
API response alone.

If a query fails on an expired session, refresh credentials with whatever login workflow the machine
already has for that datastore, then retry; do not add credential handling to the recipe.

### `teardown`
Commands run after the scenarios and their reversals, to stop what `services` started.

## Discovery versus configuration

With no `integration_test` block for a repository, the skill derives one from the repo's own files (see
`DISCOVERY.md`), proposes it, runs it, and offers to persist it only once the run is green. This happens
once per repository.

## Precedence

Highest to lowest: inline arguments (`--env dev`), per-repo config, global config, discovered recipe.
