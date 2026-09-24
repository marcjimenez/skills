---
name: setup
description: Configure marcjimenez — external connections and their API keys, code-review settings, VCS/PR settings, and the default minimalism intensity, persisted to your marcjimenez config. Run once to get started, or any time to change the policy.
disable-model-invocation: true
---

# marcjimenez setup — first-run wizard

Interactive configurator for marcjimenez. Writes `config.json` (policy) and `secrets.env` (API keys) under the
marcjimenez config home. It NEVER writes into the target repository — no committed config, no `.gitignore` edits,
no CLAUDE.md changes.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
# One cache per REPOSITORY, keyed by the origin remote so every worktree and workspace share it.
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. A remote that is a local,
# relative or Windows path is not a portable identity, so it falls through to the path below.
REMOTE="$(git remote get-url origin 2>/dev/null)"
case "$REMOTE" in *://*|*@*:*) ;; *) REMOTE="" ;; esac
# Lowercased with tr, not sed's \L: BSD sed does not implement it and emits a literal L. GitHub treats
# Owner/Repo and owner/repo as one repository, so without this they would hash to two caches.
REPO_KEY="$(printf '%s' "$REMOTE" \
  | sed -E 's#/+$##; s#^[a-z+]+://##; s#^[^/@]*@##; s#^[^/:]+[:/]##; s#\.git$##; s#[/ ]#-#g' \
  | tr '[:upper:]' '[:lower:]')"
case "$REPO_KEY" in ""|.|..|-*|*:*|*\\*) REPO_KEY="" ;; esac
if [ -z "$REPO_KEY" ]; then
  # --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is
  # the worktree and would split the cache. --path-format=absolute (git 2.31+) also canonicalizes.
  G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || git rev-parse --git-common-dir 2>/dev/null)"
  [ -n "$G" ] && G="$(cd -- "$G" 2>/dev/null && pwd -P)"
  # Only a normal checkout's common dir ends in /.git. A submodule's is .git/modules/<name> and a bare
  # repo's is the repo itself; for those the common dir IS the identity, so do not strip a parent.
  case "$G" in */.git) R="${G%/.git}" ;; *) R="$G" ;; esac
  [ -n "$R" ] && REPO_KEY="$(basename "$R" .git)-$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
fi
[ -n "$REPO_KEY" ] || { echo "not in a git repository" >&2; exit 1; }
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

## 2. Code review

Code review runs the same two agents on every diff and scales its own depth to the diff's size, so there is
nothing required here. Offer its two optional knobs, `max_rounds` and `waivers`, only if asked; both are
documented in `reference/CONFIG-SCHEMA.md`.

`/marcjimenez:resolve-code-review` (triages a PR's existing review comments) reads a `resolve_code_review`
section with two optional knobs, both default true: `auto_reply_bots` (post a clear rebuttal to a bot
comment autonomously) and `auto_resolve` (resolve a thread once addressed, reversible). It works with no
config; offer these only if the user wants to turn off autonomous bot replies or thread resolution.
Rebuttals to human reviewers are always printed before posting regardless.

## 3. VCS / PR settings

Ask: `base_branch` (default `main`), `branch_prefixes` (default `feat/fix/refactor/docs`), whether to
`assign_reviewer` after opening a PR and to whom (`reviewers`, default `["copilot"]`). Write the `vcs`
section.

## 4. Technology practice briefs

`/marcjimenez:best-practices` caches what each technology's own maintainers say about using it well, one
file per technology at `$CONFIG_HOME/practices/<technology>.md`, shared across every repo because a schema
language's conventions do not change between projects.

Offer two knobs, both optional, written to a `practices` section:

- `max_age_days` (default 90): reuse a brief younger than this, re-research past it.
- `enabled` (default true): set false to skip the step entirely, which also skips the class of finding it
  catches.

`mkdir -p "$CONFIG_HOME/practices"` while writing, and say which briefs already exist so the user can see
what is cached rather than discovering it on the next audit. Deleting a file there is a valid way to force
a re-research.

## 5. Default minimalism intensity

Ask `defaults.ponytail_intensity` (`lite`/`full`/`ultra`, default `full`).

## 6. Integration testing (optional)

`/marcjimenez:integration-test` needs no configuration: it derives a repo's run recipe from that repo's own
files and offers to persist it after a green run. Offer to set `integration_test` by hand only if the user
wants to pre-seed a recipe or change which environment is pre-selected (`default_env`, most often `prod`).
Shape: `/marcjimenez:integration-test` `reference/RECIPE-SCHEMA.md`.

## 7. Agent handoff (optional)

`/marcjimenez:issue` applies a ready label to tickets that pass its readiness gate, and
`/marcjimenez:implement` claims a ticket before working it. Both read `agent_handoff`, and both work on the
defaults, which match labels that already exist in the user's repos. Offer this section only to rename a
label or change `claim_ttl_hours`. Field detail:
`/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`.

## 8. Target + write

Ask **global** (`$CONFIG_HOME/global/config.json`, every repo) vs **per-repo**
(`$CONFIG_HOME/repos/$REPO_KEY/config.json`, this repo only — wins over global). `mkdir -p` the parent, write
the JSON, print the resolved paths and a one-line effective-policy summary. Confirm `secrets.env` is
`chmod 600` and that `practices/` exists. No repo files are touched.

`practices/` is global by design even when the rest of the config is per-repo: a brief for GraphQL is worth
writing once, not once per checkout.
