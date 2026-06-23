---
name: development
description: "Full-cycle development workflow with requirements grilling, task tracking, and 5-subagent code review. MUST invoke when: implementing a feature, fixing a bug, refactoring code, building a new module, adding functionality, or making non-trivial code changes. Triggers on: 'build', 'implement', 'develop', 'add feature', 'fix bug', 'refactor', 'new module', 'create', 'wire up'. Enforces zero-ambiguity requirements, tracked task completion, and adversarial code review before every PR."
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
- [ ] PR created with summary + test plan
- [ ] 5-subagent review launched
- [ ] All critical/high findings fixed
- [ ] Final re-review clean
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
- Search before writing. If a utility exists, use it.
- Match existing style. Don't impose your preferences.
- Run tests after EVERY logical chunk, not just at the end.
- One concern per commit. Atomic changes only.
- If you discover a new task mid-work, ADD it to todo.md before doing it.

---

## Phase 5: Pre-PR Verification

Run the full quality gauntlet. Nothing ships without this.

```bash
# Run these (adjust per project):
{test command}
{lint command}
{build command}
```

Then self-review:
```bash
git diff origin/main...HEAD
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

## Phase 6: PR + 5-Subagent Adversarial Review

### Step 1: Create PR

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

### Step 2: Launch 5 review subagents in parallel

Each subagent receives this context:
- The full diff: `git diff origin/main...HEAD`
- Any CLAUDE.md or style guides in the repo
- Instruction to be adversarial (try to BREAK the code, not praise it)

Each subagent must output findings as:
```
[CONFIDENCE: 0-100] [SEVERITY: critical|high|medium|low]
FILE:LINE — Problem. Fix.
```

**Subagent 1: Convention + Style**
> You are reviewing this diff for compliance with repo conventions. Read CLAUDE.md and any style guides first. Check: naming conventions, import ordering, file organization, commit message format, code comment style, TypeScript/Python idioms. Flag deviations. Confidence 80+ only.

**Subagent 2: Logic + Correctness**
> You are reviewing this diff for bugs. Think adversarially. Check: off-by-one errors, null/undefined access, race conditions, incorrect boolean logic, missing awaits, wrong comparison operators, state that can desync, error paths that swallow failures. Prove each finding with a concrete scenario.

**Subagent 3: Security**
> You are reviewing this diff for security vulnerabilities. Check: user input flowing to dangerous sinks (SQL, shell, eval, innerHTML), secrets in code or logs, missing auth checks, SSRF vectors, path traversal, timing attacks, insecure defaults. Reference OWASP Top 10 where applicable.

**Subagent 4: Test Adequacy**
> You are reviewing this diff for test coverage gaps. Check: new functions without tests, new branches without assertions, error paths untested, edge cases (empty, null, boundary values, concurrent access) missing, tests that assert nothing meaningful (smoke-only). Suggest specific test cases.

**Subagent 5: Simplicity + Architecture**
> You are reviewing this diff for over-engineering and missed reuse. Check: abstractions that serve one caller, utilities that already exist elsewhere in the repo, dead code introduced, import boundary violations, unnecessary indirection layers, things that could be 5 lines but are 50. Also: docs still accurate after this change?

### Step 3: Triage findings

- Discard findings with confidence < 80
- Group remaining: critical → high → medium → low
- Critical/high = must fix. Medium = fix if easy. Low = note for user.

### Step 4: Fix + re-review (max 3 rounds)

1. Fix all critical and high findings
2. Re-run ONLY the affected subagents (not all 5)
3. If new findings surface, fix those too
4. After 3 rounds, surface any remaining as "known limitations" in PR description

### Step 5: Completion

- Mark all Ship tasks `[x]` in todo.md
- Read todo.md top to bottom. Every line must be `[x]`.
- If any line is `[ ]`, GO BACK and complete it. Do NOT proceed.
- Report to user: PR URL, summary of review findings addressed, any known limitations.

---

## Inviolable Rules

1. **The task file is the source of truth.** Not your memory. Not your feeling of "done." READ IT.
2. **Phase 2 cannot be skipped.** "Just do it" is not a requirement. Push back.
3. **Phase 6 cannot be skipped.** Even for "small" changes. Especially for "small" changes.
4. **Never commit to main.** Branch + PR. Always.
5. **Never guess requirements.** Ask. Every time.
6. **Never stop with unchecked tasks.** If the task file has `[ ]`, you are not done.
7. **Fresh main first.** Stale branches = merge conflicts = wasted time.
