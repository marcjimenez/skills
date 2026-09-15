# Discovering a repo's run recipe

Run this when no `integration_test` config exists for the repository. The goal is a recipe drawn from what
the repo already documents about itself, not an invented one. Ask the user only for what the files cannot
answer.

## Where to look, in order

Stop as soon as you have a working answer for each part.

| Looking for | Sources, best first |
|-------------|--------------------|
| How to start it | `CLAUDE.md`, `README.md`, `CONTRIBUTING.md` run sections; `package.json` scripts (`dev`, `start`, `serve`); `Makefile` targets; `docker-compose.yml`; `Procfile`; `Tiltfile` |
| When it is ready | a health or readiness route in the router; the port in the dev script or compose file; whatever CI waits on before its e2e job |
| How to authenticate | an auth helper already installed on this machine; a `*-cli` in `devDependencies`; `.env.example` token names; the auth header in existing e2e tests or a `.http`/Postman collection |
| Which endpoint | `.env.example`, the GraphQL or REST client config, the base URL in existing tests |
| How to read the data | `DATABASE_URL` in `.env.example`; a `psql`/`prisma`/`drizzle` script; a configured database MCP tool; the ORM's schema file for table and column names |
| Existing scenarios | an `e2e/`, `integration/`, or `__tests__/integration` directory; `.github/workflows/*.yml` jobs named e2e or integration |

`.github/workflows/` is usually the single highest-signal file. CI already has to start the app from
nothing, so its job steps are a working recipe someone maintains.

## Reuse before writing

Prefer a command the repo or the machine already provides over anything hand-rolled:

- If a project CLI or an installed skill already fetches a token, call it. Do not write login code.
- If a database query fails on an expired session, use whatever login workflow the machine already has for
  that datastore rather than adding credential handling to the recipe.
- If the repo already has an e2e runner, drive it rather than issuing raw requests alongside it.

## What to ask the user

Only the parts the files genuinely do not answer. Ask them together, in one message, not one at a time:

- which environment to target, and the base URL for each, if `.env.example` does not name them
- whether a fixture or seeded account is needed before the scenarios can run
- anything ambiguous about how to undo a write, since guessing here is the one mistake that costs real data

## Before running it

Present the derived recipe as numbered steps and get it confirmed. Persist nothing yet: the recipe is
saved only after the run goes green, per the skill's rules.
