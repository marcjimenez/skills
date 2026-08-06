# Research playbook — tools + brief format

## Path setup

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
mkdir -p "$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>"    # research.md lives here
```

## 1. Reuse hunt (in-repo + installed deps)

```bash
rg -n 'debounce|retry|throttle|groupBy' --glob '!node_modules'     # similar names/behavior
cat package.json pyproject.toml go.mod 2>/dev/null                  # what's already installed
```

## 2. GitHub implementation examples (via Bash + gh)

In order of cost:

```bash
gh search code '<symbol or pattern>' --language <lang> --limit 20   # real usages
gh search repos '<topic>' --sort stars --limit 10                   # canonical libs / reference impls
gh search prs '<pattern>' --limit 10                                # how a bug/pattern was actually solved
gh api repos/{owner}/{repo}/contents/{path}?ref=<sha>              # pull the exact file
```

Pin every fetched snippet to a commit SHA (`blob/<sha>/path#L10-L40`) so citations don't rot. Use
`WebSearch` for discovery when you don't yet know the repo/library name; `WebFetch` on a raw
`github.com/.../blob/<sha>/...` URL to read the snippet.

## 3. Official docs (Context7 REST API — no MCP required)

Context7 is a plain REST API you `curl`; it does NOT require any MCP server to be installed. It needs the
`context7` connection enabled and its key (`CONTEXT7_API_KEY`) in `secrets.env`. Two calls:

```bash
[ -f "$CONFIG_HOME/secrets.env" ] && . "$CONFIG_HOME/secrets.env"
# 1. resolve a library name -> a Context7 id
curl -s -H "Authorization: Bearer $CONTEXT7_API_KEY" \
  "https://context7.com/api/v1/search?query=<library>"          # -> ids like /reactjs/react.dev (+ trustScore)
# 2. fetch focused docs for that id
curl -s -H "Authorization: Bearer $CONTEXT7_API_KEY" \
  "https://context7.com/api/v1/<id>?type=txt&topic=<topic>&tokens=2000"
```

If `context7` is disabled or no key is set, fall back to `WebFetch` on the library's official doc site.

## 4. Best practices & pitfalls

`WebSearch` for known footguns, version-specific gotchas, security advisories. Cross-check each against the
docs from step 3 — a blog post can be stale; the versioned docs win.

## 5. Evaluating a NEW (not-installed) dependency

Ladder rung 5 permits proposing a library only when repo / stdlib / native / installed all miss. Before
proposing one, research the candidate and make the maintenance-vs-savings call EXPLICITLY:

- Find candidates (`gh search repos`, registry, Context7 `trustScore`); compare stars, release recency,
  open-issue health, bus factor, license, and transitive-dependency weight.
- Weigh both sides: the code we'd write and maintain WITHOUT it, vs the cost of taking it on (supply-chain
  surface, version churn, breaking changes, audit burden).
- Adopt ONLY if the maintenance we SAVE clearly beats the maintenance and risk we TAKE ON. A 20-line helper
  we fully understand often beats a dependency.

Record the verdict in the brief: `Proposed dep: <name> — saves: <x> — costs: <y> — verdict: adopt | build-it-ourselves`.

## Research brief format

Write to `$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>/research.md`:

````markdown
# Research Brief — <slug>
Problem: <one-paragraph restatement>   ·   Mode: depth | breadth   ·   Ponytail: <level>

## 1. Reuse decisions (Climb the Ladder)
Highest rung that holds: <n> — <name>
| Need | Rung | Reuse this | Import / source | Why — and what we will NOT build |
|------|------|-----------|-----------------|----------------------------------|

New-dependency verdicts (only when rung 5 reached):
- Proposed dep: <name> — saves: <x> — costs: <y> — verdict: adopt | build-it-ourselves

## 2. Reusable utilities found in-repo
- `path/file.ts:symbol` — what it does; use instead of new code.

## 3. External implementation examples
- <title> — https://github.com/org/repo/blob/<sha>/path#L10-L40 — why relevant. (verified: yes|no)

## 4. Official docs
- <library>@<version> via Context7 (id: /org/lib) — key API `foo(bar)` … — <url>

## 5. Best practices & pitfalls
- <practice> — <source> — applies because <reason>.
- Gotcha: <version-specific issue> — <source>.

## 6. Code examples to embed in the plan
```lang
// minimal snippet, adapted to our repo conventions
```
Source/derivation: <url or "adapted from docs §x"> · Verified against: <second source>

## 7. Open questions / unverified
- <claim we could not confirm> — resolve in the plan.
````
