---
name: integration-test
description: >-
  Runs a feature end to end against a real running system: starts the services, acquires a token, issues
  the actual calls, inspects the database rows they wrote, then undoes them and proves the undo worked.
  Learns each repo's run recipe once and reuses it; discovers the recipe from the repo's own files when
  none exists. Use PROACTIVELY after unit tests and lint are green and BEFORE code review, so the review
  sees real evidence. Triggers on: "integration test", "test it end to end", "does this actually work",
  "run it against prod", "test against dev", a finished feature awaiting verification.
---

# marcjimenez integration-test

Unit tests prove the pieces behave. This proves the feature works. It runs the real calls against a real
environment, reads what landed in the database, and cleans up after itself.

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
RUN_DIR="$CONFIG_HOME/repos/$REPO_KEY/runs/<slug>"
```

Evidence goes to `$RUN_DIR/integration.md`, never inside the target repo.

## Phase 1 — Load the recipe

Read the `integration_test` section through the standard precedence (inline args → per-repo → global →
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

## Phase 4 — Bring the system up

Start `services` in the background, poll `ready_check` until it passes (fail the run on timeout rather
than proceeding against a half-started system), then acquire the token via `auth`. Never echo the token.

## Phase 5 — Run each scenario

For each one, in this order:

1. Query the database for the **before** state.
2. Write the scenario's exact reversal into `$RUN_DIR/integration.md`. This happens BEFORE the mutation is
   issued, so a crash mid-run still leaves a written record of what needs undoing.
3. Issue the action. Capture the full response.
4. Query the database for the **after** state.
5. Compare against Expected. A mismatch is a finding: report it and fix the code, do not adjust the
   expectation to match what happened.

## Phase 6 — Undo, then prove it

Run every reversal, then **re-query** to show the rows are gone. A zero exit code is not proof. If a
reversal fails, say so loudly and leave the record in the evidence file; do not mark the run clean.

## Phase 7 — Tear down and persist

Stop the backgrounded services per `teardown`. Write `$RUN_DIR/integration.md`: environment, each scenario
with its action, response, before and after rows, and its cleanup proof.

If the recipe came from discovery and the run went green, offer to persist it to
`$CONFIG_HOME/repos/$REPO_KEY/config.json` so the next run skips discovery. Ask first.

## Inviolable rules

1. **The undo is written down before the mutation runs.** A mutation whose reversal you do not know stops
   the run. Ask rather than guessing at a DELETE.
2. **Cleanup is proven by re-querying**, never inferred from an exit code.
3. **No scenarios means no run.** Go get them. Do not substitute a smoke test you invented and call the
   feature verified.
4. **A recipe is persisted only after it has worked** end to end. Never save a guess.
5. **The environment question is asked every run.** A remembered answer is not consent.
6. **Never widen a reversal.** Undo exactly the rows this run created, matched by id. A `DELETE` with no
   `WHERE`, or one scoped by timestamp alone, is never acceptable.
7. **Secrets stay out of the transcript.** Tokens are captured into variables, never echoed, never written
   into the evidence file.
