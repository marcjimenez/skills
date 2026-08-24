---
name: unslop
description: >-
  Detects and rewrites AI "slop" in prose and code, and runs on essentially all writing. Use PROACTIVELY
  whenever you draft or edit a commit message, PR or issue body, doc, README, code comment, Slack message,
  SKILL.md, or CLAUDE.md, and whenever you write or refactor non-trivial code. Flags slop by DENSITY
  (clustered tells, not single words), rewrites to plain natural prose, and rejects BOTH the AI-slop style
  and the clipped "caveman" over-correction. Never claims to detect authorship and never gates on a score.
  Triggers on: writing anything for a human to read, "clean this up", "does this sound like AI", a
  commit/PR/issue body, a review rebuttal, before posting or committing text.
---

# unslop: write like a person, not a model

The job is to make prose and code read as if a careful human wrote them: plain, specific, varied. That
means removing the tells that mark text as machine-generated, without swinging into the opposite tic of
clipped, article-dropping terseness. Both extremes are detectable; the target is the natural middle.

This skill is the tell catalog and the rewrite engine. It does not replace the house style rules:
`/marcjimenez:writing-for-agents` owns agent-facing prose structure (the information ladder, context and
cognitive budgets, trigger-word descriptions), and `/marcjimenez:coding-style` with its
`reference/COMMENTS.md` owns the comment discipline (why-not-what, comment rot). unslop adds the tell
catalog those two lack and the concrete rewrite moves. Follow them; do not restate them.

## The doctrine (read before flagging anything)

1. **Density over occurrence.** No single tell is proof. "Delve" once in a paragraph by a human is fine;
   "delve", "leverage", "seamless", and "it's worth noting" in four consecutive sentences is slop. Flag
   clusters, not words. Weak tells (em-dashes, rule-of-three, "however", a lone hedge) are flagged ONLY
   when they cluster or exceed a visible density, never on a single sighting.

2. **Reject both failure modes.** Slop is one failure. The other is the "caveman" over-correction:
   stripping articles, conjunctions, and connectors to dodge detection, which leaves trailing fragments
   and flat, disjointed rhythm ("Fixed bug. Cache broke. Now works."). CLAUDE.md forbids this style
   directly. Rewrite toward natural, varied human prose, not maximal terseness.

3. **Never adjudicate authorship.** Do not label text "AI-written" and do not compute or report a slop
   score as a verdict. Detectors that try are unreliable and biased (a Stanford study falsely flagged
   61% of non-native-English essays). Surface the specific tells, explain why, and rewrite. The human
   judges.

4. **Code slop is contextual.** A code pattern is slop when it is redundant, inconsistent with its own
   file or repo, or defends against a state that cannot happen, NOT merely when it is thorough. Never
   strip a genuinely useful docstring on a public API, real error handling at a trust boundary, correct
   optional chaining on a nullable value, or team-standard formatting. See the exclusions list in
   `reference/CODE-TELLS.md`.

5. **The deletion test.** For any sentence, ask: if I remove it, is a fact, number, date, constraint, or
   tradeoff lost? If nothing is lost, delete it. Most pure-slop sentences survive deletion with zero
   information loss.

## How to run

1. **Detect.** Read the text (or diff). For prose, scan against `reference/PROSE-TELLS.md`; for code and
   comments, scan against `reference/CODE-TELLS.md`. Note each tell with its location and signal strength.
2. **Weigh by density.** Group the tells. A short passage with several clustered tells is slop; a scatter
   of one or two weak tells across a long, otherwise-specific document is not. Do not over-flag.
3. **Rewrite.** Apply the moves below and the per-tell fixes in the reference files. Keep every real fact;
   remove only the slop wrapping it. Preserve the author's meaning and any deliberate voice.
4. **Report briefly.** Show the rewrite. If asked, name the top tells you removed and why, in one or two
   sentences. Do not lecture and do not print a score.

## The rewrite moves (prose)

- Lead with the point; delete the runway. Cut opener clichés ("In today's fast-paced world", "It's worth
  noting that") and start with the fact.
- Swap Latinate inflation for plain verbs, one to one: utilize to use, facilitate to help, leverage to
  use, elevate to improve, garner to collect, commence to start, delve into to look at.
- Restore the plain copula: "serves as / stands as / functions as" back to "is/are".
- Cite or cut floating authority: "studies show" and "experts agree" become a named source with a link,
  or the claim goes.
- Break the templates: rewrite "It's not just X, it's Y" and "not X, but Y" into a direct statement; vary
  paragraph openers so fewer than half start with a formal connector; cut autopilot triads to the one
  attribute that is true.
- Prefer specifics over intensifiers: delete "robust / seamless / crucial / pivotal" and name the
  measurable property ("handles partial failures", "cuts p95 latency to 40ms").
- Fix formatting tics: sentence-case headings, drop emoji bullets, turn "**Key takeaway:** ..." bold-label
  fragments into full sentences.
- Cut the recap: state intent once; do not restate a diff line by line and then summarize the summary.
- Do not overcorrect: keep articles, conjunctions, and the occasional dash. Natural, not telegraphic.

## The rewrite moves (code)

- Delete comments that narrate the line; which comments to keep is owned by `/marcjimenez:coding-style`
  `reference/COMMENTS.md`.
- Collapse single-use abstractions and premature interfaces; inline the one call site.
- Remove dead code, unused imports, leftover debug prints, and "TODO: implement" stubs shipped as done.
- De-duplicate genuine repetition once past the rule of three; before that, leave it.
- Tighten error handling: remove try/catch and null checks that defend impossible states or swallow real
  failures; catch specific errors, not everything.
- Conform to repo conventions: the project's logger over print/console.log, its naming, its error style.
- Flatten control flow with guard clauses and early returns; simplify redundant boolean and if/else-return
  constructs.
- Replace hand-rolled utilities with the stdlib or an already-installed dependency
  (`/marcjimenez:reuse`).
- Fix `as any` / `# type: ignore` escape hatches by typing correctly; verify hallucinated or stale imports
  resolve.

## Guardrails

- Meaning is preserved. A rewrite that drops a fact, a caveat, or a number is a failed rewrite.
- Respect deliberate voice. If the author's style is intentionally informal or playful and not sloppy,
  leave it.
- Repo and house conventions win over anything here.
- When invoked to clean prose that will be posted or committed (a rebuttal, a PR body, a Q&A question),
  return prose that passes its own catalog: no em-dashes, no bold-label openers, no filler openers, no
  sycophancy.

Full catalogs and signal strengths: `reference/PROSE-TELLS.md`, `reference/CODE-TELLS.md`.
