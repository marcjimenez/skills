---
name: session-audit
description: Reads recent Claude Code sessions and reports where the marcjimenez skills, CLAUDE.md and the hooks are not earning their place. Appends to a rolling report and changes nothing else. Run it yourself, or leave it to the weekday schedule.
disable-model-invocation: true
---

# Session audit — is the tooling still worth its context?

Every skill, rule and hook costs context on turns where it contributes nothing. This reads what actually
happened in recent sessions and reports where that trade has gone bad. It is **report only**: it never
edits a skill, never opens a PR, and never files an issue.

## 1. Build the digest

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
REPORT="$CONFIG_HOME/audits/session-audit.md"
mkdir -p "$(dirname "$REPORT")"
"${CLAUDE_PLUGIN_ROOT}"/skills/session-audit/scripts/session-digest.py \
  --hours 24 > /tmp/session-digest.json                        # Monday: --hours 72
```

The transcripts run to gigabytes, so the script does every mechanical count and you read only its output.
Read `/tmp/session-digest.json`, never the raw JSONL. Field meanings: `reference/SIGNALS.md`.

## 2. Add the two checks the transcripts cannot answer

A Bash command string cannot tell authoring a violation from grepping for one, so these come from git:

```bash
for r in ~/conductor/repos/*/ ~/conductor/workspaces/*/*/; do
  [ -e "$r/.git" ] || continue
  # --all, not HEAD: every commit made in a worktree sits on a branch the canonical clone is not on, so
  # walking HEAD alone reported zero violations across a week that contained 41 commits.
  # --author: the rule is yours, so a teammate's commit is not your violation. Unscoped, a week of
  # these repos returns 62 commits and none of them are yours.
  git -C "$r" log --all --since='7 days' --author="$(git config user.email)" --format='%H %s' -i \
      --grep='Co-Authored-By.*Claude' --grep='Generated with .*Claude' 2>/dev/null
# Every worktree of a repo sees the same commits, so report each SHA once.
done | sort -u -k1,1 | cut -c1-9,41-
```

Anything returned is a live CLAUDE.md violation, because that rule is absolute.

## 3. Judge each signal

Work the checklist in `reference/SIGNALS.md`. Every finding needs the number behind it and the change it
implies. Two disciplines carry most of the weight:

- **A count is a prompt, not a verdict.** How to read each one, including which are known to over-match,
  is in `reference/SIGNALS.md`. Give every correction you report a one-clause judgement, so the entry
  itself shows it was read.
- **Silence is a finding too.** A skill that fired zero times over the baseline window is either
  mis-triggered or unnecessary, and saying which is the whole job. Do not report the zero and stop.

## 4. Append the report

Newest entry first, so the file reads top-down:

```markdown
## 2026-09-24 (24h: 6 sessions, 143 messages)

**Finding.** One line naming the skill, rule or hook, the number, and the change it implies.
**Steady.** One line for what was checked and found healthy, so a later run can see what moved.
```

Keep an entry to what changed since the last one. A finding already reported and still open gets one line
saying it is still open, not a restatement.

## 5. Done when

- [ ] Every signal in `reference/SIGNALS.md` has a line in the entry, including the healthy ones.
- [ ] Every finding cites its number and names one concrete change.
- [ ] Every correction in the entry carries a one-clause judgement, not just a quote.
- [ ] `git status --porcelain` in this repo is unchanged from before the run, and no issue or PR exists
      that did not before.
