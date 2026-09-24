# Signals — what the digest reports and how to read each one

## Contents

Skill usage · Corrections · The unslop hook · Gate compliance · Tool mix · What is deliberately absent

## Skill usage

`skills_in_window` is the day. `skills_in_baseline` is the last 30 days, which is the one to judge by:
a skill can legitimately go a day unused. `unused_over_baseline` lists skills with zero invocations over
the whole baseline.

A zero is one of three things and the audit has to say which:

- **Mis-triggered.** The work it covers happened and it did not fire. Fix the `description`, which is the
  only thing the model sees when choosing. Evidence: sessions doing that kind of work in the window.
- **Unreachable.** It carries `disable-model-invocation` and nothing hands off to it, so only a human can
  start it. `setup` is the honest example and is not a finding.
- **Unnecessary.** The work never came up. Note it and move on; a month of that is a deletion argument.

A skill firing far more than the work warrants is the same problem inverted: its description is too
greedy and it is being loaded on turns it cannot help.

## Corrections

`corrections_total` counts user messages that push back on what just happened, deduplicated across the
several transcript files a resumed conversation writes. `corrections_sampled` quotes them with the skill
that was active.

The detector is tuned to miss rather than over-report, and it still lets through a pasted alert that opens
with "No". **Read every quoted hit.** A correction that lands repeatedly under one skill is that skill's
instructions failing; a scatter across many is ordinary conversation.

## The unslop hook

`unslop_reminders` counts how often the `UserPromptSubmit` hook injected its text; `unslop_invocations`
counts how often the skill was actually invoked. The gap is not a violation, because the hook itself says
a skill already in context should not be reloaded.

The number to watch is the reminder count alone. It is injected on every prompt whether or not the turn
writes prose, so its weekly cost is the count times the length of the hook text. Report that cost when it
grows, and the change it implies is narrowing the hook's trigger, not the skill.

## Gate compliance

`pushed_without_review` lists sessions that ran `git push` or `gh pr create` with no code review anywhere
in the session. A review dispatched as subagents counts, which is how it is usually run; without that
allowance the check reports every careful session as a violation.

A non-empty list is the most serious thing the digest produces, because the gate is what everything else
rests on. Name the session and what it pushed.

## Tool mix

`top_tools` is context, not a target. It is worth reading when one tool dwarfs the rest: a session that is
almost entirely `Bash` with a handful of `Edit` calls suggests work being done through the shell that a
dedicated tool would do more legibly, which is a CLAUDE.md question rather than a skill question.

## Attribution trailers (from git, not the transcripts)

`SKILL.md` §2 asks git directly. Three details there are load-bearing and were each wrong once:

- `--all`, not HEAD. Every commit made in a worktree sits on a branch the canonical clone is not on, so
  walking HEAD returned zero across a week that held 41 commits.
- Both `~/conductor/repos` and `~/conductor/workspaces`. The first holds 3 checkouts, the second holds
  the rest.
- `--author` scoped to your own email. The rule is yours; a teammate's commit is not your violation.
  Unscoped, one week of these repos returns 62 commits and not one of them is yours. Reporting those
  would make the first line of the report a false accusation.

Deduplicate by SHA: every worktree of a repo sees the same commits.

## What is deliberately absent

Attribution trailers, force pushes and bare `git stash` were checked here once and removed. A Bash command
string cannot distinguish authoring a violation from grepping for one, and the first version flagged the
audit's own source for containing the pattern it searches for. Git history answers those exactly, so
`SKILL.md` §2 asks git instead. Do not put them back here.

Commits landing on `main` are not checked at all: the branch is not recoverable from the command string,
and a check that guesses is worse than none.
