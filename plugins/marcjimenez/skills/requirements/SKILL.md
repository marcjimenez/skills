---
name: requirements
description: >-
  Grills a coding request to zero ambiguity BEFORE implementation. Use PROACTIVELY whenever a
  build/fix/refactor request is vague, underspecified, or assumption-laden. Interrogates scope, I/O, error
  handling, integration, contracts, edge cases, and done-criteria in one pass, then restates a numbered
  spec and gates on explicit user confirmation. Triggers on: "build", "implement", "add", "fix", "change",
  "wire up" carrying any unstated behavior, format, or boundary.
---

# Requirements grilling

You will NOT write code until requirements are unambiguous. This is non-negotiable.

If the request contains a URL or ticket reference, fetch and analyze it first.

Interrogate the user on EVERY applicable dimension — the full table is in `reference/DIMENSIONS.md`
(Scope, I/O, Errors, Integration, Contracts, Edge cases, Done, End-to-end).

**DO:**
- Ask all questions in ONE message (not one at a time). At three or more, render a questions page instead:
  `/marcjimenez:plan` `reference/HTML-ARTIFACT.md`. Each question carries what is needed to decide it, a
  diagram where the shape is the question and a code sample where the difference is in the code, with
  radios, checkboxes for multi-answer, and one button that copies every answer as a single line to paste
  back. Below three, a message is lighter than a page deserves.
- Challenge vague answers ("what do you mean by 'handle errors'?").
- Restate your understanding as a numbered spec.

**DO NOT:**
- Accept "you figure it out" — push back.
- Proceed on assumptions — name them and ask.
- Ask obvious questions the code already answers.

**GATE:** the user must explicitly say "confirmed" / "yes" / "go" / "correct". Anything less = ask again.
