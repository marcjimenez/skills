---
name: development
description: "Full-cycle LangGraph agent development workflow. Use when: building a new agent, implementing a new node, adding features to existing agents, fixing agent bugs, or refactoring agent code in the ai-core monorepo. Triggers on: 'build agent', 'implement node', 'add feature', 'develop', 'new graph', 'fix agent bug'. Enforces task tracking, eval analysis, and 5-subagent deep code review."
---

# LangGraph Agent Development (Beta)

You are executing a rigorous, multi-phase development workflow for LangGraph agents in the ai-core Nx monorepo. Follow each phase sequentially. Do NOT skip phases. Do NOT stop until every task is marked complete.

## Phase 1: Deep Repository Understanding

Before writing any code, build a complete mental model of the affected area.

**Actions:**
1. Read `CLAUDE.md` at the repo root
2. Read `docs/BEST_PRACTICES.md`
3. Read the README for the specific agent/lib being modified
4. Use `mcp__nx-mcp__nx_workspace` to understand workspace architecture
5. Use `mcp__nx-mcp__nx_project_details` for every affected project
6. Explore existing patterns in the target area using subagents
7. Identify all files that will be touched and their dependencies

**Output:** Summarize your understanding to the user in 3-5 bullet points.

---

## Phase 2: Requirements Grilling

Do NOT proceed to implementation until requirements are 100% clear. Ambiguity causes rework.

**Actions:**
1. If `$ARGUMENTS` contains a Nuclino URL, fetch it via `mcp__nuclino__get_item` and analyze
2. If `$ARGUMENTS` contains a PRD or description, parse into structured requirements
3. Ask the user pointed questions about ALL of the following:
   - **State design:** What TypedDicts are needed? What fields? What reducers?
   - **Node boundaries:** What should be separate nodes vs combined? What are the edges?
   - **Error handling:** What happens on failure at each stage? Fallback behavior?
   - **Integration points:** Which external calls (Slack, APIs, DB)? Sync or async?
   - **Breaking changes:** Does this affect existing state? Need migrations?
   - **Acceptance criteria:** How do we know this is correct? What are the edge cases?
   - **Eval coverage:** What behavior should be eval'd? What metrics?

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
- [ ] Integration tests for {flow}
...

## Evals
- [ ] Determine eval impact
- [ ] Create/update eval suite (if needed)
- [ ] Run affected evals — all pass
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
- Follow `CLAUDE.md` and `docs/BEST_PRACTICES.md` to the letter
- Use `nx` for all build/test/lint operations (never raw pytest/tsc)
- Run `nx run-many -t test,lint -p <affected-projects>` after each logical chunk
- Use conventional commit prefixes: `feat:`, `fix:`, `refactor:`, etc.

**LangGraph-specific patterns (enforce these):**
- State MUST be TypedDict with `Annotated[list, add_messages]` for messages
- Include `remaining_steps: int` when using `create_react_agent` with custom state
- Cache compiled graphs in module-level globals (factory called per-run)
- Wrap ALL blocking I/O in graph factories with `ThreadPoolExecutor`
- All Slack SDK calls MUST use `asyncio.to_thread()`
- Nodes return partial state updates only (changed fields, not full state)
- Handle `GraphRecursionError` — return partial answer, don't crash
- Bedrock `content` may be a list, not a string — always handle both

**After each task completes:**
- Mark it `[x]` in `/tmp/tasks/{feature-slug}/todo.md`
- Run tests for affected projects
- Continue to the next task

---

## Phase 5: Eval Analysis

Determine if changes require new or modified evals. Run affected evals.

**Decision tree:**
1. Did you add/modify a graph node's behavior? → Eval needed
2. Did you change prompt content? → Eval needed
3. Did you change routing logic? → Eval needed
4. Did you only refactor internals (same I/O)? → Eval likely NOT needed

**If evals needed:**
1. Follow the pattern in `libs/py/shared/evals-py/evals_py/agents/kudos_ai_companion/`
2. Create metrics in `evals_py/agents/{agent}/metrics.py` using `create_geval_metric()`
3. Create test runner in `evals_py/agents/{agent}/eval_{node}.py` implementing `run() -> SuiteResult`
4. Register agent in `evals_py/agents/registry.py` if new

**Run affected evals:**
```bash
nx affected -t eval:check --base=origin/main
```

**NEVER run `nx run evals-py:eval:check` without the affected filter. Evals cost real money.**

**Loop:** If evals fail, fix the issue and re-run. Repeat until green.

**If no eval impact:** Document in the PR description WHY evals are not affected.

Mark eval tasks `[x]` in todo.md.

---

## Phase 6: PR + 5-Subagent Deep Code Review

Create the PR and run a rigorous multi-agent review.

**Step 1: Create PR**
- Push branch, create PR with conventional commit title
- PR body includes: summary, test plan, eval impact

**Step 2: Launch 5 parallel review subagents**

Each subagent MUST:
- Read the actual `CLAUDE.md` file (not from memory)
- Read `docs/BEST_PRACTICES.md`
- Review the full PR diff (`git diff origin/main...HEAD`)
- Cite specific rule violations with `file:line` references
- Rate confidence (0-100) for each finding

**Subagent assignments:**

1. **CLAUDE.md Compliance**
   - Nx rules (tags, generators, no manual mkdir)
   - Cross-language type conventions (snake_case JSON)
   - Import hierarchy
   - Commit conventions
   - Surgical changes (no unrelated modifications)

2. **BEST_PRACTICES.md Compliance**
   - LangGraph state design (TypedDict, Annotated reducers)
   - Factory pattern with caching
   - ThreadPoolExecutor for blocking I/O
   - Callback patterns
   - Slack streaming rules (50-block limit, recipient params)
   - Common pitfalls (Bedrock content blocks, JSON fence stripping)

3. **Security + Correctness**
   - No secrets in graph state
   - No `--allow-blocking` in production code
   - Input validation at boundaries
   - OWASP top 10 (injection, XSS if applicable)
   - Race conditions in async code
   - State mutation bugs

4. **Test + Eval Coverage**
   - Unit tests for new functions
   - Integration tests for new nodes
   - Eval coverage for behavior changes
   - Edge cases covered
   - Error paths tested

5. **Architecture + Documentation**
   - Nx tags present on new projects
   - Import boundaries respected (no cross-app imports)
   - Shared libs have README
   - Docs still accurate after changes
   - `.env.*.example` updated if new env vars added

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
3. **Never run full eval suite.** Always use `nx affected` filter.
4. **Never skip Phase 6.** Every PR gets 5-subagent review.
5. **Never commit to main.** Always feature branch + PR.
6. **Never guess.** If uncertain, ask the user.
