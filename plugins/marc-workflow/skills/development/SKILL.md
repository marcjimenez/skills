---
name: development
description: "Generic full-cycle development workflow. Use when: implementing features, fixing bugs, refactoring code, or building new modules in any repo. Triggers on: 'build', 'implement', 'develop', 'add feature', 'fix bug', 'refactor', 'new module'. Enforces requirements grilling, task tracking, and 5-subagent code review."
---

# Development Workflow

You are executing a rigorous, multi-phase development workflow. Follow each phase sequentially. Do NOT skip phases. Do NOT stop until every task is marked complete.

---

## Phase 0: Fresh Branch

**Actions:**
1. `git checkout main && git pull origin main`
2. Create feature branch: `git checkout -b feat/{feature-slug}` (or `fix/`, `refactor/` as appropriate)

**GATE: Must be on a fresh branch before proceeding.**

---

## Phase 1: Deep Understanding

Before writing any code, build a complete mental model of the affected area.

**Actions:**
1. Read `CLAUDE.md` at the repo root (if it exists)
2. Read any relevant docs (README, CONTRIBUTING, architecture docs)
3. Explore the specific area being modified (related files, existing patterns, tests)
4. Identify all files that will be touched and their dependencies
5. Check for existing utilities, helpers, or patterns that can be reused

**Output:** Summarize your understanding to the user in 3-5 bullet points.

---

## Phase 2: Requirements Grilling

Do NOT proceed to implementation until requirements are 100% clear. Ambiguity causes rework.

**Actions:**
1. If `$ARGUMENTS` contains a URL (Nuclino, Linear, GitHub issue), fetch and analyze it
2. If `$ARGUMENTS` contains a description, parse into structured requirements
3. Ask the user pointed questions about ALL of the following that apply:
   - **Scope:** What exactly is in scope? What is explicitly NOT in scope?
   - **Inputs/Outputs:** What data comes in? What should come out?
   - **Error handling:** What happens on failure? Fallback behavior?
   - **Integration points:** What other systems/modules are affected?
   - **Breaking changes:** Does this affect existing APIs, schemas, or contracts?
   - **Edge cases:** What weird scenarios need handling?
   - **Acceptance criteria:** How do we know this is correct and done?

4. Summarize your understanding back to the user in a structured format
5. WAIT for explicit confirmation ("yes", "correct", "go ahead")
6. If ANY answer is unclear, ask follow-up questions. Repeat until zero ambiguity.

**GATE: Do NOT proceed until the user explicitly confirms requirements.**

---

## Phase 3: Task Planning

Create a comprehensive task list that will serve as your completion checklist.

**Actions:**
1. Create directory: `mkdir -p /tmp/tasks/{feature-slug}`
2. Write `/tmp/tasks/{feature-slug}/todo.md` with ALL subtasks as checkboxes:

```markdown
# {Feature Name}

## Implementation
- [ ] {task 1} — verify: {how to verify}
- [ ] {task 2} — verify: {how to verify}
...

## Testing
- [ ] Unit tests for {component}
- [ ] Integration tests for {flow} (if applicable)
...

## Verification
- [ ] All tests pass
- [ ] Linting clean
- [ ] Build succeeds
...

## PR & Review
- [ ] Create PR with conventional commit
- [ ] 5-subagent code review passes
- [ ] All review findings addressed
- [ ] All tasks in this file marked [x]
```

3. Present the task list to the user for confirmation

**CRITICAL RULE: You are NOT DONE until EVERY checkbox in this file is marked `[x]`. DO NOT STOP. DO NOT ASK IF YOU SHOULD CONTINUE. KEEP WORKING.**

---

## Phase 4: Implementation

Execute the implementation tasks. Follow repo conventions exactly.

**Rules:**
- Search for existing patterns before writing new code (ALWAYS)
- Follow any CLAUDE.md, CONTRIBUTING.md, or style guides in the repo
- Match existing code style, naming conventions, and architecture patterns
- Run tests and linting after each logical chunk
- Use conventional commit prefixes: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, etc.
- Keep commits focused and atomic (one logical change per commit)

**After each task completes:**
- Mark it `[x]` in `/tmp/tasks/{feature-slug}/todo.md`
- Run tests for affected code
- Continue to the next task

---

## Phase 5: Pre-PR Verification

Before creating the PR, ensure everything is clean.

**Actions:**
1. Run full test suite for affected projects
2. Run linting
3. Run build (if applicable)
4. Review your own diff: `git diff main...HEAD`
5. Check for: accidentally committed files, debug code, TODO comments, console.logs
6. Fix any issues found

**Loop:** If anything fails, fix and re-verify until all green.

Mark verification tasks `[x]` in todo.md.

---

## Phase 6: PR + 5-Subagent Deep Code Review

Create the PR and run a rigorous multi-agent review.

**Step 1: Create PR**
- Push branch, create PR with conventional commit title
- PR body includes: `## Summary` (bullet points), `## Test plan` (checklist)

**Step 2: Launch 5 parallel review subagents**

Each subagent MUST:
- Read any CLAUDE.md or style guides in the repo
- Review the full PR diff (`git diff origin/main...HEAD`)
- Cite specific issues with `file:line` references
- Rate confidence (0-100) for each finding

**Subagent assignments:**

1. **Convention Compliance**
   - Repo style guides and CLAUDE.md rules
   - Naming conventions
   - Import patterns
   - Commit message format

2. **Logic + Correctness**
   - Off-by-one errors, null handling, race conditions
   - State management bugs
   - Edge cases not covered
   - Incorrect assumptions

3. **Security**
   - Input validation at boundaries
   - Injection risks (SQL, command, XSS)
   - Secret handling (no hardcoded secrets, no secrets in logs)
   - Auth/authz gaps

4. **Test Coverage**
   - Missing unit tests for new functions
   - Missing edge case tests
   - Missing error path tests
   - Test quality (meaningful assertions, not just smoke tests)

5. **Architecture + Simplicity**
   - Unnecessary abstractions or over-engineering
   - Code that should reuse existing utilities
   - Import boundary violations
   - Dead code or unused variables introduced

**Step 3: Process findings**
- Collect all findings from 5 subagents
- Filter: only findings with confidence >= 80
- Group by severity (critical > high > medium)

**Step 4: Iterate**
- Fix all critical and high findings
- Re-run affected subagents on fixed code
- Max 3 rounds. Surface anything unresolved after 3 rounds.

**Step 5: Complete**
- Mark all review tasks `[x]` in todo.md
- Verify EVERY task in todo.md is `[x]`
- Report final status to user

---

## Rules That Cannot Be Broken

1. **Never stop early.** If tasks remain unchecked, keep working.
2. **Never skip Phase 2.** Unclear requirements cause 10x rework.
3. **Never skip Phase 6.** Every PR gets 5-subagent review.
4. **Never commit to main.** Always feature branch + PR.
5. **Never guess.** If uncertain, ask the user.
6. **Always pull latest main first.** Stale branches cause merge hell.
