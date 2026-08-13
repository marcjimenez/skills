---
name: setup
description: Configure marcjimenez — external connections and their API keys, code-review depth, VCS/PR settings, and the default minimalism intensity, persisted to your marcjimenez config. Run once to get started, or any time to change the policy.
disable-model-invocation: true
---

# marcjimenez setup — first-run wizard

Interactive configurator for marcjimenez. Writes `config.json` (policy) and `secrets.env` (API keys) under the
marcjimenez config home. It NEVER writes into the target repository — no committed config, no `.gitignore` edits,
no CLAUDE.md changes.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel 2>/dev/null)"
REPO_KEY="$([ -n "$TOP" ] && printf '%s-%s' "$(basename "$TOP")" "$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
```

Follow the full config schema in `reference/CONFIG-SCHEMA.md`. Present each section, propose sensible
defaults, and confirm before writing.

## 1. External connections (+ credentials)

Ask which external tools `/marcjimenez:research` may use — `context7`, `web_search`, `web_fetch`, `github_cli` —
as on/off toggles. For each, write `{ "enabled": <bool>, "auth": "<none|cli|api_key>" }` into the
`connections` section.

For a connection with `auth: "api_key"` (e.g. `context7` uses the context7.com REST API with a
`CONTEXT7_API_KEY` — no MCP; and any other keyed integration the user adds), persist
the key "under the hood" to `secrets.env` and record only the env-var NAME in `config.json` —
`{ "enabled": true, "auth": "api_key", "env_var": "<NAME>" }`, never the value. Use this hardened write
(single-quote-escaped so a value with shell metacharacters can't execute when the file is later sourced;
anchored atomic upsert so a rotated key leaves no stale line; value never in argv or shell history):

```bash
umask 077
mkdir -p "$CONFIG_HOME"
touch "$CONFIG_HOME/secrets.env" && chmod 600 "$CONFIG_HOME/secrets.env"
IFS= read -rs KEY                                  # read without echo; not in argv/history
esc=$(printf '%s' "$KEY" | sed "s/'/'\\\\''/g")    # POSIX escape: each ' -> '\'' (tested injection-safe)
tmp=$(mktemp "$CONFIG_HOME/.secrets.XXXXXX")         # inherits umask 077 -> 0600
grep -v "^export $ENV_VAR=" "$CONFIG_HOME/secrets.env" > "$tmp" 2>/dev/null || true
printf "export %s='%s'\n" "$ENV_VAR" "$esc" >> "$tmp"
mv "$tmp" "$CONFIG_HOME/secrets.env"                 # atomic; drops old line, no dupes
unset KEY esc
```

Prefer to PRINT this block for the user to run in their own terminal: the agent-run shell has no
interactive TTY for `read -rs`, and a key pasted into the chat lands in the conversation transcript. Only
run it inline yourself if the user explicitly asks — and name that transcript risk when you do.

## 2. Code-review depth

Code review is adaptive by default — triage picks the reviewers each diff warrants from all eight, so there
is nothing required here. Offer the optional knobs only: `reviewers` (a shorter candidate set to permanently
drop reviewers a repo never needs), `adaptive: false` (run every reviewer on every diff), plus
`confidence_threshold`, `max_rounds`, `adversarial_verification`. Field detail: `/marcjimenez:code-review`
`reference/REVIEW-DEPTH.md`.

## 3. VCS / PR settings

Ask: `base_branch` (default `main`), `branch_prefixes` (default `feat/fix/refactor/docs`), whether to
`assign_reviewer` after opening a PR and to whom (`reviewers`, default `["copilot"]`). Write the `vcs`
section.

## 4. Default minimalism intensity

Ask `defaults.ponytail_intensity` (`lite`/`full`/`ultra`, default `full`).

## 5. Target + write

Ask **global** (`$CONFIG_HOME/global/config.json`, every repo) vs **per-repo**
(`$CONFIG_HOME/repos/$REPO_KEY/config.json`, this repo only — wins over global). `mkdir -p` the parent, write
the JSON, print the resolved paths and a one-line effective-policy summary. Confirm `secrets.env` is
`chmod 600`. No repo files are touched.
