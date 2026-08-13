---
name: best-practices
description: >-
  Audits an implementation, plan, or diff against real-world best practices and design patterns sourced
  from high-signal GitHub repositories and official docs. Given what we are building and the dependencies
  in play, it finds where we diverge from how the ecosystem does it well and reports each divergence with a
  citation and a concrete fix. Use PROACTIVELY inside planning, during implementation, and in code review.
  Triggers on: "is this the best way", "best practice", "design pattern", "how do others do this", "are we
  using X correctly", "idiomatic", planning, review, or any non-trivial use of a dependency or framework.
---

# Best practices — audit our approach against real-world prior art

Given a target (a diff, a planned approach, or an in-progress implementation) and the dependencies and
frameworks it leans on, judge it against how well-regarded projects actually do the same thing. The output
is a list of divergences, each with a real citation and a concrete change — not abstract advice.

This skill judges; it does not discover from scratch. `/marcjimenez:research` gathers the evidence (what exists,
how an API works, which dep to pick); this skill evaluates the chosen approach against that evidence plus
targeted prior art. When a research brief already exists for this work (`runs/<slug>/research.md`), read it
first and build on its GitHub findings rather than re-searching.

## Modes (the caller passes one)

- **review** — audit a committed diff. Findings are BLOCKING as a class: each must be resolved or explicitly
  waived with a stated reason before the caller proceeds. Used by `/marcjimenez:code-review`.
- **advisory** — audit a plan or in-progress implementation. Findings SHAPE the work but do not gate it.
  Used by `/marcjimenez:plan` and `/marcjimenez:implement`.

## Connections: use only what's enabled

This audit has authority only when it cites real GitHub code or official docs, so it needs those connections.
Resolve connections exactly as `/marcjimenez:research` does (see its **Connections** section): use ONLY sources
marked `enabled`, and if an enabled `auth: "api_key"` connection is missing its key, prompt for it once and
persist it. Treat a connection that FAILS at call time the same as off — for example an `enabled` `gh` that
turns out unauthenticated — by falling back to the next enabled source and noting the gap in your output,
never by skipping an audit item silently. If every external source is off or failing, say so plainly and
limit findings to what the repo itself and its installed-dependency docs can support.

## Steps

1. **Identify the surface to audit.** What are we building or changing, and what dependencies, frameworks,
   and APIs does it lean on?
   - review mode: parse the diff — the new/changed functions, the libraries they import, the patterns used.
   - advisory mode: the chosen approach and its dependency list.
   Write the audit list as specific items: "our React Query usage for X", "our retry logic around fetch",
   "our LangGraph node structure" — not "the whole file".

2. **Gather prior art (reuse research's GitHub playbook — do NOT duplicate it).** For each item, find how
   high-signal projects do it and what the docs recommend. Mechanics live in
   `/marcjimenez:research` `reference/RESEARCH-PLAYBOOK.md` §2–4: `gh search code`/`repos`/`prs` for real,
   high-star usage pinned to a commit SHA, and official docs via Context7 (or WebFetch) for the idiomatic
   form. Prefer canonical sources: the library's own examples and docs, and repos with many stars and recent
   activity. A single stale blog post is not prior art.

3. **Compare and find divergences.** For each item, contrast our approach with the prior art. A divergence
   is real only when the ecosystem's way is concretely better HERE — safer, more idiomatic, less code, or it
   avoids a known pitfall — AND applies to our context. When our divergence is justified (repo convention,
   a constraint the ecosystem example lacks), say so and do NOT flag it.

4. **Report.** One finding per divergence, most severe first:
   ```
   [SEVERITY: high|medium|low]
   <what we do> — <what well-regarded projects do> (cite: SHA-pinned URL or doc) — <why theirs is better
   here> — <the concrete change>.
   ```
   State items that already match prior art as matching — silence is not a pass. Severity: misusing a
   dependency in a way that breaks or is unsafe = high; a clearly-better idiomatic pattern we skip = medium;
   a minor stylistic divergence = low.

## Blocking + waiver (review mode only)

Every finding must end **resolved** (the code changed to match) or **waived** (a conscious, recorded decision
that our divergence is justified here, with the reason stated). An unwaived, unresolved finding blocks the
review. The waiver is what keeps blocking-for-all from stalling a PR on pedantry: it forces a decision on
each finding without forcing a change.

Waivers persist so a divergence is decided ONCE, not re-litigated every PR. Before flagging, read
`code_review.waivers` from the per-repo config (`$CONFIG_HOME/repos/$REPO_KEY/config.json`) and drop any
finding that matches a recorded waiver (same file-area + divergence). When the user waives a new finding,
append `{ "area": …, "divergence": …, "reason": … }` to that list. Report resolutions and fresh waivers back
to the caller.

## Completion criteria

- [ ] Every dependency, framework, and pattern of substance in the target was audited; none silently skipped.
- [ ] Each finding cites a real, SHA-pinned GitHub source or an official doc — no unsourced assertions.
- [ ] Each finding names the concrete change, not "consider improving".
- [ ] Items that already match prior art are stated as matching, not omitted.
- [ ] review mode: every finding is resolved or explicitly waived with a reason before returning.
