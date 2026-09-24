# Technology practice briefs

A cache of what a technology's own maintainers say about using it well, kept at
`$CONFIG_HOME/practices/<technology>.md` and shared across every repo, because GraphQL's
conventions do not change between projects.

## Contents

Why this exists · When to write one · Freshness · Sourcing bar · Format · A smell is a prompt, not a verdict

## Why this exists as its own step

Auditing "how do well-regarded repos use this library" finds API misuse. It does not find
the conventions the technology itself defines, and those are where the expensive mistakes
live, because they are invisible in any single call site.

A worked example. A GraphQL schema had implementation detail written into its SDL
descriptions: column names, transaction mechanics, which signals were persisted. Every
reviewer read it as ordinary code comments and passed. The rule that condemns it is
specific to GraphQL and stated by its maintainers: `"""descriptions"""` are shipped to
every client through introspection and rendered in tooling, `#` comments are stripped, and
a schema should not expose the implementation details of a service. No amount of comparing
against other repos' resolvers surfaces that. Asking "what does GraphQL say about
documenting a schema" surfaces it immediately.

So the question this step asks is not "how do others call this API" but "what does this
technology consider correct use, and what does it consider a smell".

The brief answers a second question too, in its `Provides` section: what does this
technology already ship that somebody is about to rewrite by hand? That list is expensive
to derive from the docs and the same in every repo, so it is worth caching even though it
moves across major versions. `/marcjimenez:code-review` reads it before it starts grepping,
so the reuse question costs a file read rather than a research pass.

## When to write one

Write a brief for a technology the target leans on structurally, where "using it wrong" is
possible in a way the compiler will not catch. Good candidates: a schema or IDL language
(GraphQL, Protobuf, Avro), an ORM or query builder, a state or effect system, a migration
tool, an infrastructure DSL.

Skip it for a technology used incidentally, one with no meaningful conventions of its own,
or one already covered by a fresh brief.

## Freshness

Reuse a brief whose `researched` date is within `practices.max_age_days` (default 90, see
`/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`). Past that, re-research and rewrite it,
keeping the file at the same path so citations stay stable. Conventions move slowly, so the
default is generous; a brief that turns out wrong should be rewritten immediately whatever
its age, and the correction noted in `Superseded`.

## Sourcing bar

Same bar as the rest of the audit. Cite the technology's own documentation, specification,
or a maintainer's writing. A conference talk or a well-argued post from a maintainer counts.
A blog post by a stranger restating the docs does not, and neither does a Stack Overflow
answer, unless it is the only place a real pitfall is written down and it is labelled as
such.

## Format

```markdown
---
technology: graphql
researched: 2026-08-21
sources:
  - https://graphql.org/learn/schema/
  - https://www.apollographql.com/docs/graphos/schema-design/guides/demand-oriented-schema-design
---

# GraphQL

## Rules
One per line, each falsifiable and each with the source it came from. A rule that cannot be
checked against a diff is an opinion, not a rule.

- SDL `"""descriptions"""` are published to clients via introspection; `#` comments are
  stripped. Implementation detail belongs in `#`. [graphql.org/learn/schema]
- A schema should not expose the implementation details of a service. [Principled GraphQL]

## Provides
What this technology ships that people commonly rehand-roll, with the import path. Written
for the reuse question, so name the symbol somebody would otherwise write themselves.

- `graphql.buildSchema(sdl)` — parse and validate SDL; no need for a custom loader.
- `@graphql-tools/merge` `mergeTypeDefs` — merging SDL across files.

## Smells
What "wrong" looks like in a diff, concretely enough to grep for.

- A description naming a database column, an index, a cache, or a transaction.
- A description explaining why a field is absent.

## Not rules
Things that look like rules and are not, so a later audit does not flag them. Record the
reason.

- Descriptions on every field. Useful, not required; a self-evident field does not need one.

## Superseded
Anything a later run found to be wrong here, with the date. Keeps a corrected brief from
silently reverting.
```

Rules and smells are what a later audit greps against. Keep them short and checkable; put
the reasoning in the rule's own line rather than in a paragraph above it.

## A smell is a prompt, not a verdict

Smells are deliberately broad, so they over-match. Run against one real schema, the GraphQL
brief flagged seventeen descriptions and roughly a third were fine: "lets a client tell a
stale cached copy from the live one" mentions a cache and is exactly what a caller needs;
"nothing is persisted" tells a caller the call has no side effects.

Read every hit and decide. Reporting a smell as a finding without reading it is worse than
not running the check, because it trains the reader to ignore the output. When a hit turns
out to be legitimate for a reason that will recur, add it to **Not rules** so the next run
does not spend the same attention on it.
