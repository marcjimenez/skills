---
name: integration-test
description: >-
  Runs a feature end to end against a real running system: starts the services, acquires a token, issues
  the actual calls, inspects the database rows they wrote, then undoes them and proves the undo worked.
  Learns each repo's run recipe once and reuses it; discovers the recipe from the repo's own files when
  none exists. Always asks which environment to target before doing anything. Invoked by name, or by
  /marcjimenez:implement-beta as its end-to-end phase. Triggers on: "integration test", "test it end to
  end", "does this actually work", "run it against prod", "test against dev".
---

# marcjimenez integration-test

Unit tests prove the pieces behave. This proves the feature works. It runs the real calls against a real
environment, reads what landed in the database, and cleans up after itself.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
# One cache per REPOSITORY, keyed by the origin remote so every worktree and workspace share it.
# get-url, not `config --get`: only get-url expands an insteadOf rewrite. Lowercased with tr, not
# sed's \L, which BSD sed does not implement and silently turns into a literal L.
REPO_KEY="$(git remote get-url origin 2>/dev/null \
  | sed -E 's#^([a-z+]+://[^/]+/|[^/:]+:)##; s#\.git$##; s#[/ ]#-#g' | tr '[:upper:]' '[:lower:]')"
# A local-path remote leaves a leading '-', which every coreutils tool reads as an option; an unknown
# scheme leaves a ':'. Either way the repo path below is the better identity, so fall through.
case "$REPO_KEY" in ""|-*|*:*) REPO_KEY="" ;; esac
# --git-common-dir is the MAIN checkout's git dir from inside a worktree, where --show-toplevel is the
# worktree and would split the cache. --path-format=absolute makes it absolute AND canonical.
[ -n "$REPO_KEY" ] || REPO_KEY="$(G="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
  && [ -n "$G" ] && R="$(dirname "$G")" \
  && printf '%s-%s' "$(basename "$R")" "$(printf '%s' "$R" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
[ -n "$REPO_KEY" ] || { echo "not in a git repository" >&2; exit 1; }
RUN_DIR="$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>"
mkdir -p "$RUN_DIR"
```

Reuse the plan's or task file's `<slug>`; derive one per `/marcjimenez:task-tracking` if neither exists.
Evidence goes to `$RUN_DIR/integration.md`, never inside the target repo.

## Phase 1 — Load the recipe

First, check `$RUN_DIR/integration.md` for reversals from an earlier run with no matching cleanup proof.
If any exist, present them and settle them before starting anything new. A previous run's standing
mutations are this run's first job.

Then read the `integration_test` section through the standard precedence (inline args → per-repo → global →
defaults). Schema: `reference/RECIPE-SCHEMA.md`.

No recipe for this repo means discovery: work out how to run it from the repo's own files per
`reference/DISCOVERY.md`, then present the draft recipe as numbered steps and get it confirmed before
running anything.

## Phase 2 — Ask which environment

Ask every run, even when the recipe is already known. Present the configured environments with
`default_env` pre-selected, and say plainly which ones are mutating:

> Run against **prod** (mutating, writes real rows that are undone afterwards) or **dev**?

A repo with only one environment still gets the question, because the answer is also the confirmation to
proceed.

## Phase 3 — Load the scenarios

Take them from the **Integration scenarios** section of `$RUN_DIR/plan.md`. If there is no plan, or the
plan has no scenarios, derive them from the confirmed requirements and get them confirmed before running
anything.

Each scenario needs four parts. Without all four it is not runnable:

| Part | Content |
|------|---------|
| Given | starting state, and any fixture that has to exist first |
| Action | the exact call: the full query, mutation, request, or command |
| Expected | the observable result: response shape AND the database rows it should produce |
| Undo | the exact reversal that puts the system back |

A fixture this run creates to satisfy Given is itself a mutation and needs its own written reversal. A
fixture that already existed is never deleted.

## Phase 4 — Bring the system up

Start `services` in the background, poll `ready_check` until it passes (fail the run on timeout rather
than proceeding against a half-started system), then acquire the token via `auth`. Capture it straight
into the variable in one command, `TOKEN="$({auth.command})"`, check only that it is non-empty, and never
run the command bare where its output would reach the transcript.

From here on, every exit runs `teardown` and writes whatever evidence exists. A timeout, a failed
scenario, and a failed reversal all leave services running otherwise.

## Phase 5 — Run each scenario

For each one, in this order:

1. Query the database for the **before** state, capturing every column the reversal will need to restore,
   not just whether the row exists.
2. Write the scenario's exact reversal into `$RUN_DIR/integration.md`. This happens BEFORE the mutation is
   issued, so a crash mid-run still leaves a written record of what needs undoing. Confirm the file
   contains it before going on. No written reversal, no mutation.
3. Issue the action. Capture the full response.
4. Query the database for the **after** state.
5. Compare against Expected. A mismatch is a finding: report it and fix the code, do not adjust the
   expectation to match what happened.

Raw SQL, regexes over real input, and wire-format strings are the reason this phase exists, so make sure a
scenario executes each one against the real engine. A mocked `query()` proves the code path and never the
statement. Two defects in one change passed unit tests and prose review and appeared only on execution: a
bind parameter the warehouse refused to type (`-$1` over `unknown`), and an `ESCAPE '\'` clause that left
the string literal unterminated because that engine reads a backslash inside a literal as its own escape.

## Phase 6 — Undo, then prove it

Run the reversals in reverse order of the mutations that created them, so a row another row references is
not deleted first. Then **re-query** to show each row is gone, or restored to its before-values for a
reversal that undid an update. A zero exit code is not proof.

A reversal runs through the same surface as the action: the API's own inverse operation wherever one
exists. Raw SQL is a last resort, used only when `data_access.writable` is true and the API offers no
inverse. Against a channel that has not declared itself writable, stop and ask rather than writing.

If a reversal fails, attempt the remaining ones so no further rows are stranded, then stop. Append
`Result: failed` to the evidence file with the rows still standing, the reversal that failed, and its
error. Do not persist the recipe and do not hand control back to the caller as passing. A standing
mutation is an open incident.

## Phase 7 — Tear down and persist

Stop the backgrounded services per `teardown`. **Append** the run summary to `$RUN_DIR/integration.md`:
environment, each scenario with its action, response, before and after rows, and its cleanup proof. Append
only, because the reversals written during Phase 5 are the crash record and stay in the file verbatim.
Redact credentials from anything captured: `Authorization: Bearer <redacted>`, never the value.

End the summary with a verdict line of its own, `Result: green` or `Result: failed`, at the start of a
line. Callers gate on it rather than on your say-so:

```bash
grep '^Result:' "$RUN_DIR/integration.md" | tail -1 | tr -d '\r' | sed 's/[[:space:]]*$//'
```

`Result: green` stands alone: no reason, no trailing text. Only `Result: failed` carries a reason after
it, so a caller comparing against the bare string is never tripped by one.

Write `Result: green` only when all four criteria below hold. Everything else is `Result: failed` with the
reason, including a run you abandoned partway. A missing file means the run never happened, which is a
different and equally reportable thing.

If the recipe came from discovery and the verdict is green, persist it to
`$CONFIG_HOME/repos/$REPO_KEY/config.json` so the next run skips discovery: show the block, get a yes,
then merge it into any config already there rather than overwriting the file. A recipe is never saved
against a failed or abandoned run.

## The run is green when

- Every scenario's after-state matched its Expected, response and rows both.
- Every reversal ran, and a re-query showed each row gone or restored to its before-values.
- The services started in Phase 4 are stopped.
- `$RUN_DIR/integration.md` holds every scenario with its before rows, after rows, and cleanup proof, and
  no credential values.

Anything short of all four is not green, whatever else passed. Record the verdict either way: a caller
that finds no `Result:` line treats the run as not having happened.

## Inviolable rules

1. **The undo is written down before the mutation runs.** For a mutation whose reversal you do not know,
   stop and ask the user for the exact reversal; resume only once they give it. Never infer one.
2. **Cleanup is proven by re-querying**, never inferred from an exit code.
3. **Scenarios come from the plan**, or are derived from confirmed requirements and confirmed by the user.
   Never a smoke test you invented and called verification.
4. **A recipe is persisted only after it has worked** end to end. Never save a guess.
5. **The environment question is asked every run.** A remembered answer is not consent.
6. **Scope every reversal to the exact ids this run touched.** A row this run created is deleted by id. A
   row this run modified is restored, column by column, to the values captured in the before-query. A
   `DELETE` with no `WHERE`, or one scoped by timestamp alone, is never acceptable.
7. **A scenario acts only on data this run owns.** Against a mutating environment, every action targets
   records this run created or a test account the recipe names. A scenario that would modify pre-existing
   production rows stops the run and goes to the user.
8. **Secrets stay out of the transcript.** Tokens are captured into variables, never echoed, never written
   into the evidence file.
