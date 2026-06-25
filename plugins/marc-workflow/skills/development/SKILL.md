---
name: development
description: "Full-cycle development workflow with requirements grilling, task tracking, and 7-subagent adversarial code review (including documentation accuracy). MUST invoke when: implementing a feature, fixing a bug, refactoring code, building a new module, adding functionality, or making non-trivial code changes. Triggers on: 'build', 'implement', 'develop', 'add feature', 'fix bug', 'refactor', 'new module', 'create', 'wire up'. Enforces zero-ambiguity requirements, tracked task completion, and adversarial code review before the PR is pushed."
---

# Development Workflow

You are bound to this workflow until every task is complete. No shortcuts. No early exits.

CRITICAL RULE: You are NOT done until every checkbox in your task file is `[x]`. If you feel like stopping, you are wrong. Read the task file. If unchecked items remain, keep working. The only valid exit is a fully-checked task file with a merged-ready PR.

---

## Phase 0: Fresh Branch

```bash
git checkout main && git pull origin main
git checkout -b {prefix}/{feature-slug}
```

Prefix: `feat/` | `fix/` | `refactor/` | `docs/` based on change type.

GATE: Confirm you are on a fresh branch with clean working tree before proceeding.

---

## Phase 1: Codebase Reconnaissance

Build a mental model BEFORE touching code. You cannot write good code in a codebase you don't understand.

1. Read `CLAUDE.md` at repo root (if exists) — these are your laws
2. Read relevant docs: README, CONTRIBUTING, architecture docs, ADRs
3. Explore the target area: find related files, existing patterns, current tests
4. Map dependencies: what imports this? what does this import?
5. Search for reusable utilities — if it exists, USE IT. Do not rewrite.

Output to user: 3-5 bullets summarizing what you found and what patterns you'll follow.

---

## Phase 2: Requirements Grilling

You will NOT write code until requirements are unambiguous. This is non-negotiable.

If `$ARGUMENTS` contains a URL, fetch and analyze it first.

Then interrogate the user on EVERY applicable dimension:

| Dimension | Question |
|-----------|----------|
| Scope | What is IN scope? What is explicitly OUT? |
| I/O | What data enters? What comes out? What format? |
| Errors | What happens when X fails? Silent? Retry? Propagate? |
| Integration | What other modules/services are touched? |
| Contracts | Does this change any API, schema, type, or interface? |
| Edge cases | What are the weird inputs? Empty? Null? Concurrent? |
| Done | What specific observable behavior means "this works"? |

DO:
- Ask all questions in ONE message (not one at a time)
- Challenge vague answers ("what do you mean by 'handle errors'?")
- Restate your understanding as a numbered spec

DO NOT:
- Accept "you figure it out" — push back
- Proceed on assumptions — name them and ask
- Ask obvious questions the code already answers

GATE: User must explicitly say "confirmed" / "yes" / "go" / "correct". Anything less = ask again.

---

## Phase 3: Task File

Create the execution plan. This file is your contract with yourself.

```bash
mkdir -p /tmp/tasks/{feature-slug}
```

Write `/tmp/tasks/{feature-slug}/todo.md`:

```markdown
# {Feature Name}

## Implementation
- [ ] {atomic task} — verify: {exact check}
- [ ] {atomic task} — verify: {exact check}

## Tests
- [ ] {test task} — verify: {test passes}

## Quality
- [ ] All tests pass (run command: {exact command})
- [ ] Lint clean (run command: {exact command})
- [ ] Build succeeds (run command: {exact command})
- [ ] Self-review diff: no debug code, no TODOs, no console.logs

## Ship
- [ ] 7-subagent review launched on LOCAL diff (NOT pushed yet)
- [ ] All critical/high findings fixed
- [ ] Documentation reviewed + updated (in sync with code)
- [ ] Final re-review clean
- [ ] ONLY NOW: push branch + create PR with summary + test plan
- [ ] All boxes in this file checked
```

Rules for tasks:
- Each task is ONE logical unit (completable without context-switching)
- "verify" field must be a concrete check (command output, test name, assertion)
- If you can't define "verify", the task is too vague — split it

GATE: Present task list to user. Get confirmation before coding.

---

## Phase 4: Implementation

Execute tasks. Mark complete as you go. Never leave the task file stale.

**Execution loop (repeat per task):**
1. Implement the task
2. Run its verification check
3. If check fails → fix → re-run (loop until green)
4. Mark `[x]` in todo.md
5. Commit if logical boundary reached (conventional prefix)
6. Move to next task

**Non-negotiable rules:**
- Match existing style. Don't impose your preferences.
- Run tests after EVERY logical chunk, not just at the end.
- One concern per commit. Atomic changes only.
- If you discover a new task mid-work, ADD it to todo.md before doing it.

### Don't Reinvent the Wheel (CRITICAL)

Before writing ANY new function, helper, utility, or abstraction, you MUST prove nothing existing solves it. This is not optional.

**Search order (do ALL of these before writing custom code):**

1. **Codebase first** — grep/search the repo for existing utilities, helpers, or patterns that do the same thing. Check shared libs, utils directories, common modules.
2. **Installed dependencies** — check `package.json`, `pyproject.toml`, `go.mod` for already-installed packages. Read their docs. They likely have a function for what you need.
3. **Framework built-ins** — check the framework's own API (React hooks, LangGraph utilities, FastAPI dependencies, etc.). Use WebFetch or context7 to read current docs if unsure.
4. **Well-known maintained libraries** — if nothing installed covers it, check if a highly-vetted, actively-maintained library exists (100k+ downloads/week, recent commits, strong community). You may PROPOSE adding it as a dependency, but explain why.

**What counts as reinventing:**
- Writing a custom debounce/throttle when lodash is installed
- Writing date parsing when dayjs/date-fns is available
- Writing a retry wrapper when the HTTP client has one built in
- Writing custom validation when zod/pydantic is in the project
- Writing string utils that exist in the language stdlib
- Writing a state machine when the framework has one
- Reimplementing something that exists 3 directories away

**If you catch yourself writing >10 lines for something that feels generic, STOP.** Search again. It almost certainly exists.

**When proposing a new dependency:**
- Must be actively maintained (commits in last 6 months)
- Must have significant adoption (not a random GitHub repo)
- Must solve a real gap (not just "slightly nicer API")
- Present to user: package name, why needed, alternatives considered

---

## Phase 5: Pre-PR Verification

Run the full quality gauntlet. Nothing ships without this.

```bash
# Run these (adjust per project):
{test command}
{lint command}
{build command}
```

Then self-review (local only — nothing is pushed yet):
```bash
git diff main...HEAD
```

Check for:
- [ ] Accidentally staged files (.env, .DS_Store, node_modules)
- [ ] Debug code (console.log, debugger, print statements)
- [ ] TODO/FIXME/HACK comments you introduced
- [ ] Unused imports or variables you added
- [ ] Hardcoded values that should be config

Fix anything found. Re-run quality checks. Loop until clean.

Mark verification tasks `[x]`.

---

## Phase 6: 7-Subagent Adversarial Review, THEN PR

CRITICAL ORDERING: The review runs on your LOCAL diff. Do NOT push. Do NOT create the PR. Do NOT commit to a remote. The push + PR creation is the VERY LAST action in Step 5, and only after the review is clean. This is non-negotiable.

### Step 1: Launch 7 review subagents in parallel

Each subagent receives this context:
- The full local diff: `git diff main...HEAD` (compare against local main, nothing is pushed)
- Any CLAUDE.md, CONTRIBUTING, or style guides in the repo
- The relevant docs for the touched area (README, architecture docs, ADRs, API docs, inline doc comments)
- Instruction to be RUTHLESSLY adversarial: assume the code is broken and prove it. A review that finds nothing is a failed review — dig deeper.

Every subagent operates under these robustness rules:
- Read the ACTUAL surrounding code, not just the diff hunks. Context outside the diff matters.
- Every finding needs a concrete trigger: a specific input, sequence, or state that exposes it. No vague "this might be a problem."
- Trace each changed value end to end: where it comes from, every branch it flows through, where it lands.
- Assume hostile inputs, concurrent callers, and partial failure at every boundary.
- Self-check before reporting: "Could I defend this finding to a staff engineer with a runnable repro?" If not, drop it or lower confidence.

Each subagent must output findings as:
```
[CONFIDENCE: 0-100] [SEVERITY: critical|high|medium|low]
FILE:LINE — Problem. Concrete trigger/repro. Fix.
```

**Subagent 1: Convention + Style**
> You are reviewing this diff for compliance with repo conventions. Read CLAUDE.md and any style guides first. Check: naming conventions, import ordering, file organization, commit message format, code comment style, TypeScript/Python idioms. Cross-reference at least 3 existing files in the same area to confirm the real convention before flagging. Flag every deviation. Confidence 80+ only.

**Subagent 2: Logic + Correctness**
> You are reviewing this diff for bugs. Think adversarially. Check: off-by-one errors, null/undefined access, race conditions, incorrect boolean logic, missing awaits, wrong comparison operators, state that can desync, error paths that swallow failures, incorrect handling of empty/partial results. For EACH finding, write the exact input or execution sequence that triggers the bug. If you cannot construct a trigger, do not report it.

**Subagent 3: Security**
> You are reviewing this diff for security vulnerabilities. Check: user input flowing to dangerous sinks (SQL, shell, eval, innerHTML), secrets in code or logs, missing auth checks, SSRF vectors, path traversal, timing attacks, insecure defaults, unsafe deserialization, dependency risks. Reference OWASP Top 10 where applicable. Trace every external input from entry point to sink.

**Subagent 4: Test Adequacy**
> You are reviewing this diff for test coverage gaps. Check: new functions without tests, new branches without assertions, error paths untested, edge cases (empty, null, boundary values, concurrent access) missing, tests that assert nothing meaningful (smoke-only), tests that would still pass if the implementation were broken. List each gap as a specific missing test case with its inputs and expected output.

**Subagent 5: Simplicity + Reinvention Check**
> You are reviewing this diff for over-engineering and reinvented wheels. For EVERY new function/helper/utility in the diff, answer: does this already exist? Check: (1) elsewhere in this repo (grep for similar function names, patterns), (2) in already-installed dependencies (read package.json/pyproject.toml, check if lodash/date-fns/etc already have this), (3) in the framework's built-in API (React, LangGraph, FastAPI, etc.), (4) in the language stdlib. Also flag: abstractions serving one caller, unnecessary indirection, things that could be 5 lines but are 50, import boundary violations, dead code. If custom code reimplements something available, cite the existing alternative with its import path and file:line.

**Subagent 6: Performance + Resources**
> You are reviewing this diff for performance and resource problems. Check: N+1 queries, work inside loops that belongs outside, unbounded memory growth, missing pagination/limits, blocking calls on hot paths, leaked handles/connections/listeners, redundant recomputation, missing indexes implied by new queries. For each finding, state the scale at which it bites (e.g. "O(n^2) over the items list — degrades past ~1k rows") and the fix.

**Subagent 7: Documentation Accuracy**
> You are reviewing whether the documentation is still correct and complete after this change. Read the relevant docs for the touched area: README, CONTRIBUTING, architecture docs, ADRs, API/reference docs, changelog, and inline doc comments / docstrings. Check: docs that describe now-changed behavior, signatures, flags, env vars, or endpoints; new public surface (functions, config, commands, schemas) that is undocumented; examples or code snippets in docs that would now fail; setup/usage steps that are now wrong; stale diagrams. For each finding, cite the doc file:line and the exact code change that makes it stale, and state the precise edit needed. Treat missing docs for new public behavior as a high-severity finding.

### Step 2: Triage findings

- Discard findings with confidence < 80
- Group remaining: critical → high → medium → low
- Critical/high = must fix. Medium = fix if easy. Low = note for user.
- Documentation findings: update the docs as part of the fix pass. Code and docs ship together.

### Step 3: Fix + re-review (max 3 rounds)

1. Fix all critical and high findings (including doc updates)
2. Re-run ONLY the affected subagents (not all 7)
3. If new findings surface, fix those too
4. After 3 rounds, surface any remaining as "known limitations" in the PR description

### Step 4: Documentation sync gate

Before the PR exists, confirm explicitly:
- Every doc the Documentation subagent flagged is updated or consciously deferred (with reason)
- New public behavior introduced by this change is documented
- No example/snippet in the docs is now broken

GATE: Do NOT proceed to Step 5 until docs are in sync with the code.

### Step 5: NOW push + create the PR

This is the FIRST time anything leaves your machine. Only reach this step after the review is clean and docs are synced.

```bash
git push -u origin HEAD
gh pr create --title "{conventional prefix}: {description}" --body "$(cat <<'EOF'
## Summary
- {bullet 1}
- {bullet 2}

## Test plan
- [ ] {verification step}
- [ ] {verification step}
EOF
)"
```

### Step 6: Completion

- Mark all Ship tasks `[x]` in todo.md
- Read todo.md top to bottom. Every line must be `[x]`.
- If any line is `[ ]`, GO BACK and complete it. Do NOT proceed.
- Report to user: PR URL, summary of review findings addressed, doc updates made, any known limitations.

---

## Inviolable Rules

1. **The task file is the source of truth.** Not your memory. Not your feeling of "done." READ IT.
2. **Phase 2 cannot be skipped.** "Just do it" is not a requirement. Push back.
3. **Phase 6 cannot be skipped.** Even for "small" changes. Especially for "small" changes. All 7 subagents run.
4. **Review BEFORE push.** The 7-subagent review runs on the LOCAL diff. Do NOT push or create the PR until the review is clean and docs are synced — that is the last step.
5. **Docs ship with code.** Stale docs are a review failure. The Documentation subagent gates the PR.
6. **Never commit to main.** Branch + PR. Always.
7. **Never guess requirements.** Ask. Every time.
8. **Never stop with unchecked tasks.** If the task file has `[ ]`, you are not done.
9. **Fresh main first.** Stale branches = merge conflicts = wasted time.
