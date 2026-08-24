# Validity rubric and rebuttal craft

How to decide whether a review comment is valid, what bucket it falls in, and how to write a reply that
holds up. Grounding: developers leave 60 to 70 percent of LLM review comments unresolved, and Copilot
comments resolve around 72.9 percent of the time, so triage is the whole point, not a nicety.

## Two axes

**Type.** bug/issue (a real defect), suggestion/refactor (an improvement), nit (trivial preference,
non-blocking), question (a concern, not a request), praise, note/FYI (informational, no action).

**Severity.** critical (data loss, priv-esc, security or reliability failure), high (correctness /
security / maintainability with user impact), medium (should fix, not a blocker), low (polish). Elevate
severity on high-risk files: auth, crypto, secrets, parsing/deserialization, persistence, money-handling.
Any critical/high with a true premise is blocking; medium/low is not.

## Decision procedure (per comment)

1. **Is the factual premise true?** Re-read the cited code against the comment. The most common invalid
   classes are a comment that flags a nonexistent issue ("Incorrect Suggestion") and one that overlooks an
   already-present fix ("Missed Existing Fix"). False premise means invalid: rebut with the evidence.
2. **Is it correctness / security / performance, with a true premise?** Then it is valid and usually
   blocking (elevate on risky files). Facts and data overrule opinion, so you almost always act.
3. **Is it pure preference or linter-owned style?** Then it is a nit, non-blocking. You may defer or
   decline; do not relitigate style inline.
4. **Is it in scope for this PR?** Out-of-scope cleanup is a legitimate decline: file a follow-up issue
   (`/marcjimenez:issue`) and a TODO, do not expand the PR.
5. **Is it a question, not a request?** Answer it; it may need no code change.
6. **Is the thread already resolved or verified-outdated?** If the code already changed and the point is
   handled, verify and just resolve.

Signals a comment is worth acting on: it ships an inline code suggestion (these resolve ~75% vs ~65%
without) and it explains the why. Vague, preference-only, or architectural-without-a-concrete-fix comments
are the ones most safely pushed back on.

Output per comment: `{type, severity, in_scope, premise_valid, verdict: accept | rebut | defer | question,
blocking, author_is_bot}`.

## Which bucket (self-explanatory vs Q&A)

Self-explanatory (act autonomously): the verdict needs no product/scope/priority call. A plain valid fix
(typo, missing guard, obvious bug), or a plainly invalid comment (bot false-positive, false premise,
clearly out of scope).

Q&A (ask the user): the verdict or the correct fix turns on intent, scope, priorities, or domain knowledge
you should not invent. Behavior-changing suggestions, "should this also handle X", design tradeoffs, and
anything where a wrong assumption ships a wrong change. Batch these into one session (see SKILL.md).

## Rebuttal craft (invalid comments)

Run every rebuttal through `/marcjimenez:unslop` before posting. The craft:

- Acknowledge, then counter. Never a bare "no". Explain why you chose the approach and name the tradeoff.
- Lead with evidence: a benchmark, a spec or doc link, a passing or failing test, a named principle. A
  cited rebuttal is near-unarguable; an assertion invites a volley.
- If the reviewer misread the code, prefer fixing the code over winning the argument. A misread is often
  evidence the code is unclear.
- Ask a clarifying question to surface a false premise ("Are you concerned about X, or Y?") rather than
  asserting the reviewer is wrong.
- Separate preference from correctness. Concede preference cheaply; marshal evidence only for correctness,
  security, and performance.
- Comment on the code, never the person. The thread is a permanent record.

## Auto vs ask, by author

- Bot comments (Copilot, CodeRabbit) are advisory and non-blocking by construction. A clear rebuttal to a
  bot is safe to post autonomously. Bots also take managed commands (for example CodeRabbit's
  `@coderabbitai resolve`), but a normal reply plus a GraphQL resolve works uniformly.
- Human comments: a self-explanatory rebuttal is still printed in full before it posts (it is
  irreversible). Anything needing an assumption goes to Q&A.

## Sources

Google eng-practices (handling-comments, pushback, standard): facts overrule preferences, fix the code not
the reviewer, the Nit/Optional/FYI prefixes. Conventional Comments (label spec). thoughtbot code-review
guide. Graphite comment-types. Microsoft severity-taxonomy (Critical/High/Medium/Low, file-risk tiers).
arXiv 2510.05450 and 2607.21997 (resolution-rate studies and the rejection taxonomy). CodeRabbit, Copilot,
and Sourcery docs (comment categories, non-blocking bot behavior).
