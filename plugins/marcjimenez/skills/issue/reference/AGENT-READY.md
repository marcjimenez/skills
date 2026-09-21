# Agent-ready tickets

A ticket qualifies for the ready label when an agent could pick it up cold and build from it without
asking a question. This is a gate on the handoff, never on filing: a ticket that does not qualify is still
filed, it just does not get the label.

## Why the bar is specific rather than high

The evidence points the opposite way from intuition. A study of what makes an issue ready for a coding
agent (arXiv 2512.21426) predicts whether the resulting PR merges, and finds merged PRs come from issues
that are **shorter**, tightly scoped, and carry explicit pointers to the artifacts involved. Issues that
reference external things (configuration, dependencies, third-party APIs) merge significantly less often.

So the gate checks for named sections, not for length. A long ticket that never says which files to touch
fails; a short one that does, passes.

## Required sections

Defaults for `agent_handoff.required_sections`. The first three are what the repo's own
`ready-for-agent` tickets already use; `Files` is the addition the evidence argues for.

| Section | Holds | Why it is required |
|---|---|---|
| `What to build` (or `What to do`) | one paragraph naming the deliverable | without it the agent picks its own goal |
| `Acceptance criteria` | checkboxes, each observable | the agent's definition of done, and the reviewer's |
| `Files` | the paths the change is expected to touch | the strongest single predictor of a merged PR |
| `Blocked by` (or `Not blocking`) | issue numbers, or "none" | stops an agent starting work that cannot land |

`Files` is a starting point, not a cage. An agent that finds the real change belongs elsewhere should say
so in the PR rather than forcing the listed paths.

## The gate

A heading on its own proves nothing, so the check is that each section exists **and has content**. Three
things it has to get right, each of which a naive grep gets wrong:

- A heading inside a fenced code block is an example, not a section. The template below would otherwise
  satisfy the gate if someone pasted it into a ticket verbatim.
- `## Filesystem changes` is not a `Files` section, so the heading text is anchored at both ends.
- Acceptance criteria are often nested under a parent bullet, so the checkbox match allows indentation.

```bash
# Fenced blocks are examples. Drop them before looking for sections.
BODY="$(awk '/^```/{f=!f; next} !f' "$BODY_FILE")"

# A section counts only when its heading is followed by a non-blank, non-heading line.
section_filled() {
  printf '%s\n' "$BODY" | awk -v pat="$1" '
    tolower($0) ~ /^#+[ \t]/ { inside = (tolower($0) ~ pat); next }
    inside && NF          { found = 1 }
    END                   { exit found ? 0 : 1 }'
}

missing=()
section_filled '^#+[ \t]+(what to build|what to do)[ \t]*$'   || missing+=("What to build")
section_filled '^#+[ \t]+acceptance criteria[ \t]*$'          || missing+=("Acceptance criteria")
printf '%s\n' "$BODY" | grep -qE '^[[:space:]]*- \[[ x]\] '  || missing+=("Acceptance criteria: at least one checkbox")
section_filled '^#+[ \t]+files[ \t]*$'                        || missing+=("Files")
section_filled '^#+[ \t]+(blocked by|not blocking)[ \t]*$'    || missing+=("Blocked by, or Not blocking: none")
```

`required_sections` in config names which sections a repo expects, but the checks above are written out
rather than generated from it. Changing the list means editing this block; there is no indirection today,
and pretending otherwise would be worse than saying so.

Empty `missing` means apply `ready_label`. Otherwise file without it, apply `needs_info_label` if the repo
has one, and report the list so the user can decide whether to fill the gaps or leave it as a human ticket.

Say what is missing and stop. Do not invent acceptance criteria to get a ticket over the bar, because a
ticket that passes on invented criteria is worse than one that honestly fails.

## Body template

Modelled on the repo's existing `ready-for-agent` tickets, plus `Files`.

```markdown
## What to build

One paragraph. What will exist when this is done, and why it is worth doing.

## Acceptance criteria

- [ ] An observable statement, checkable by someone who did not write the code.
- [ ] Another.

## Files

- `path/to/the/main/change.ts` — what changes here
- `path/to/its/test.ts` — the coverage this needs

## Blocked by

- #123

(or `## Not blocking` with "none" when there are no dependencies)
```

## Labels

Read from `agent_handoff`. Defaults match labels that already exist in `trykudos/api`:

| Label | When |
|---|---|
| `ready-for-agent` | the gate passed |
| `ai-generated` | the body was drafted by an agent, which is every ticket this skill files |
| `needs-info` | the gate failed, if the repo has the label |

A repo may not have them. `gh` will not create a label implicitly, so offer the exact commands rather than
letting the create fail:

```bash
gh label create ready-for-agent --repo "$REPO" --color 0E8A16 \
  --description "Fully specified and ready for an implementation agent"
gh label create agent-in-progress --repo "$REPO" --color FBCA04 \
  --description "An agent currently holds this issue"
gh label create ai-generated --repo "$REPO" --color c5def5 \
  --description "Issue created by AI agent"
```

`agent-in-progress` is applied by `/marcjimenez:implement`, not here, but it is created alongside the
others so the handoff does not stall later on a missing label.
