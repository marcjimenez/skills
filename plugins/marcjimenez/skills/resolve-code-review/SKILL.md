---
name: resolve-code-review
description: >-
  Works through the review comments on a pull request: fetches every review thread, states a take on each,
  autonomously handles the self-explanatory ones (fix and reply and resolve, or rebut a false-positive and
  resolve), and batches the ones that need a product/context assumption into a single Q&A session with the
  user. Valid comments needing real code changes are queued as atomic tasks and chained into planning and
  implementation. Every reply and every question is run through unslop first. Use PROACTIVELY when the user
  says "address the review", "resolve the PR comments", "handle the review feedback", "respond to Copilot /
  CodeRabbit", or after a reviewer leaves comments. HARD GATE: never posts, resolves, or pushes without
  passing the rules below.
---

# resolve-code-review: triage and resolve a PR's review comments

Given a pull request, enumerate its review comments, judge each one, act on the clear ones, and ask the
user about the ones that need a call only they can make. This runs AFTER a PR exists and reviewers (human
or bot) have commented. It is distinct from `/marcjimenez:code-review`, which runs the adversarial panel on
a LOCAL diff before the PR. This one resolves comments that already exist on the PR.

## 0. Load config and resolve the PR

Read the `vcs` section of config.json (schema: `/marcjimenez:setup` `reference/CONFIG-SCHEMA.md`) for
`base_branch` and any `resolve_code_review` knobs (auto-reply-to-bots, auto-resolve; defaults below).

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel)"
REPO_KEY="$(basename "$TOP")-$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)"
```

Resolve the target PR: default to the PR for the current branch (`gh pr view --json number,url`). If none
exists, say so and stop. If the user named a PR number, use it. Requires `gh` authenticated
(`gh auth status`); if not, stop and tell the user.

## 1. Fetch every review thread (GraphQL)

Fetch review threads with their resolution state and node ids in one query, then map each comment to its
thread. The exact query, the three comment surfaces, and the footguns are in `reference/GH-MECHANICS.md`.
Two things that will bite if skipped:

- `gh pr view --json comments` returns only the top-level conversation, NOT inline review threads and NOT
  their resolved state. Use the GraphQL `reviewThreads` query.
- Resolving a thread later needs the thread node id (`PRRT_...`); replying needs the numeric comment id.
  They come from different fields of the same query. Map `comments.databaseId -> thread.id` now.

Skip threads already `isResolved`. Treat `isOutdated: true` (the code under the comment changed) as a
strong "probably already addressed" signal: verify against the current diff, and if handled, just resolve.
Paginate past 100 threads (see the reference).

## 2. State a take on each comment

For each unresolved comment, classify it with the rubric in `reference/VALIDITY-RUBRIC.md` and write a
one-line take: `{path}:{line} ({type}/{severity}): {verdict} because {reason}`. The verdict is one of
accept (valid, will change code), rebut (invalid: false premise, bot false-positive, or clearly out of
scope), defer (valid but non-blocking preference, offer a follow-up), or question (needs an answer before
it can be decided). Note whether the author is a bot (`user.type == "Bot"`).

The core of the rubric: is the factual premise true (re-read the cited code), is it correctness / security
/ performance, is it in scope, is it a question rather than a request. Facts and data overrule preference.
The most common invalid class is a comment that flags a nonexistent issue or overlooks an already-present
fix.

## 3. The two-bucket gate

Route each comment by whether acting on it needs an assumption the user must make.

**Self-explanatory (act autonomously).** The take is unambiguous and needs no product, scope, or priority
call:
- accept + mechanical fix (typo, missing null check, rename, obvious bug): make the fix, reply with the
  commit, resolve the thread.
- rebut (bot false-positive, false premise, plainly out of scope): post an evidence-based rebuttal, resolve
  the thread.
- Thread resolution is reversible (`unresolveReviewThread`), which keeps this low-stakes. A public rebuttal
  reply is the one write that cannot be taken back, so PRINT exactly what you are about to post before
  posting it. That is a surfacing step, not an approval prompt; it does not slow this path.

**Needs an assumption or product judgment (hold for Q&A).** The comment's validity or its correct fix
turns on intent, scope, priorities, or domain knowledge you should not invent (for example: "should this
also handle the legacy tenant?", "is this endpoint meant to be public?", a design tradeoff, a
behavior-changing suggestion). Collect ALL such comments and run ONE Q&A session:
- Use `AskUserQuestion` where the choices are discrete (accept / rebut / defer, or picking among concrete
  fixes). Use plain prose questions where the answer is open-ended.
- Batch them. Never drip-feed one prompt per comment.
- Then act on the answers: fix-and-resolve, rebut-and-resolve, or enqueue.

## 4. unslop every outward and user-facing word

Run every rebuttal reply AND every Q&A question through `/marcjimenez:unslop` before it is shown or posted.
The user is probed in plain standard English: no "Great question", no filler openers, no hedging clusters,
no em-dashes, no bold-label fragments. Rebuttal craft (acknowledge then counter, lead with evidence, fix
the code if the reviewer misread it, separate preference from correctness, never a bare "no", comment on
the code not the person) is in `reference/VALIDITY-RUBRIC.md`.

## 5. Queue the valid code-change comments

Comments accepted for a real code change (more than a one-line mechanical fix) become atomic tasks in
`/marcjimenez:task-tracking` format, carrying the metadata needed to reply and resolve afterward:

```
- [ ] {path}:{line}: {one-line fix}
      severity: {..}  type: {..}  thread_id: {PRRT_..}  comment_id: {id}  review: {pr_review_id}
      verify: {concrete check that proves it's done}
```

One comment maps to one task, unless several share a root cause (collapse them and resolve their threads
together). Order by severity, then group by file.

## 6. Chain to plan, then user review, then implement

Hand the queue to `/marcjimenez:plan` so the fixes are planned with concrete examples, present the plan to
the user for review, and on approval `/marcjimenez:implement` builds them. After each fix lands, reply to
the comment with the commit sha and resolve its thread (mechanics in `reference/GH-MECHANICS.md`). For a
small queue of mechanical fixes, skip planning and fix directly in the build loop; use judgment.

## Rules

1. **Never invent a product decision.** If validity or the fix needs an assumption, it goes to Q&A, not to
   autonomous action.
2. **Print before you post.** Public rebuttal replies are irreversible; show the exact text first.
3. **unslop everything outward-facing.** Rebuttals and questions both.
4. **Auto-reply to bots, be careful with humans.** Bot comments (Copilot, CodeRabbit) are advisory and
   non-blocking by construction, so a clear rebuttal to a bot is safe to post autonomously. A rebuttal to a
   human, even a self-explanatory one, is still printed first.
5. **Resolve only what is addressed.** Resolve a thread after the fix lands or the rebuttal is posted, not
   before. Resolution is reversible if you get it wrong.
6. **Don't expand the PR.** Out-of-scope but valid comments get a follow-up issue (`/marcjimenez:issue`)
   and a decline, not scope creep.
