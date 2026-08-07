---
name: issue
description: >-
  Draft a GitHub issue, present it once for confirmation, then file it with the repo's own labels,
  project and assignees. Learns each repo's filing conventions from its existing issues rather than
  asking cold, and persists them so the question is answered once. Use PROACTIVELY whenever the user
  wants to create, file, open, or draft a GitHub issue or ticket. Triggers on: "make a ticket",
  "create an issue", "file an issue", "open an issue", "make a github issue", "draft a ticket".
---

# GitHub issue — draft, confirm, file

Produces one well-formed issue and files it correctly. The work is in getting the metadata right and the
body written in the repo's own idiom; creating it is a single command at the end.

**Never create the issue before the user has seen the draft.** Filing is visible to the whole team and an
issue with the wrong label or project is corrected by hand afterwards.

## 0. Resolve configuration (always first)

```bash
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez"   # Windows: %APPDATA%\marcjimenez
TOP="$(git rev-parse --show-toplevel 2>/dev/null)"
REPO_KEY="$([ -n "$TOP" ] && printf '%s-%s' "$(basename "$TOP")" "$(printf '%s' "$TOP" | { command -v shasum >/dev/null 2>&1 && shasum || sha1sum; } | cut -c1-8)")"
```

Deep-merge these, highest precedence first. For each field take the first source that defines it. Read each
with the Read tool; a missing file contributes nothing and is not an error.

1. Inline arguments on this invocation (`--repo`, `--project`, `--label`, `--assignee`) — ephemeral, never written.
2. `$CONFIG_HOME/repos/$REPO_KEY/config.json` → the `issues` object.
3. `$CONFIG_HOME/global/config.json` → the `issues` object.
4. What step 2 discovers from the repo itself.

Full schema: see `reference/ISSUE-CONFIG-SCHEMA.md`.

**If no `issues` block exists for this repo, do NOT run a questionnaire.** Go to step 2, discover the
conventions, propose them as part of the single confirmation in step 4, and write them to the per-repo
config once the user approves. A repo answers this question about itself better than the user can from memory.

## 1. Preflight

Run these before drafting, so a permissions problem surfaces in seconds rather than after the user has
reviewed a body.

```bash
gh auth status                       # authenticated at all?
gh auth status 2>&1 | grep -q "'project'" || echo "MISSING project scope"
```

| Check | Failure | Say this |
| --- | --- | --- |
| `gh` authenticated | not logged in | `gh auth login` |
| `project` scope on the token | `--project` fails with an opaque error | `gh auth refresh -s project --hostname github.com` |
| Every label already exists | `gh` will not create labels | offer `gh label create <name> --description "..." --color <hex>` |
| Assignees can be assigned | silent omission or hard error | confirm each has repo access |

Resolve the repo explicitly rather than relying on the working directory when the user named one.

## 2. Learn the repo's conventions

Discovery beats interrogation. Three cheap calls tell you almost everything:

```bash
gh label list --repo "$REPO" --limit 100
gh project list --owner "$OWNER" --limit 30
gh issue list --repo "$REPO" --limit 5 --state all --json number,title,labels,assignees,projectItems
```

From the recent issues, take the label and project that appear consistently. Then read one issue body in
full and mirror its structure — heading names, whether it opens with a bolded deliverable line, whether
acceptance criteria are checkboxes.

Report what you found in one line, e.g. "the last 3 issues all carry `personalization` and sit on Backlog",
so the user is approving an observation rather than a guess.

## 3. Draft the body to a file

**Write the body to a file. Never pass it as `--body`.** Issue bodies contain backticks, code fences, pipes
and quotes, and inlining them into a shell argument mangles them. Put the file in the scratchpad directory,
never in the repository.

**Invoke `/marcjimenez:writing-for-agents`** to ensure the body follows house writing principles. Then apply
these issue-specific rules:

- **Open with the deliverable in one sentence.** A reader who stops after the first line should know what
  will exist when this is done.
- **Say why before what.** The reason survives longer than the plan and is what lets someone re-scope the
  work when the plan turns out wrong.
- **Prefer verified specifics to description.** Real row counts, real column names, real file paths, real
  volumes. If a claim can be checked, check it and put the number in. A ticket asserting "the table is
  large" ages badly; one saying "502,815,744 rows as of 2026-08-07" does not.
- **Name what is blocked and by what**, with issue numbers, so the reader knows whether they can start.
- **Make "Done when" checkable.** Each box should be something a person can observe, not a quality
  adjective. "Refresh completes inside its window and the figure is recorded" beats "performance is good".
- **State open questions as open** rather than resolving them silently in prose.
- Match the repo's structure from step 2 (section headings, checkbox style, opening format).

When the user is filing several related tickets, draft them all before creating any, so cross-references
between them can be filled in. Create the depended-upon one first and edit its number into the other.

## 4. Present once, then confirm

Show the user, in one message:

- the resolved **repo, title, labels, project, assignees** (and, when discovered rather than configured,
  the evidence for each)
- the **full body** as drafted
- anything you were unable to verify and have therefore stated as an open question

Then ask once, offering: file it, edit something first, or discard. Only proceed on an explicit yes.

## 5. Create

```bash
gh issue create --repo "$REPO" \
  --title "$TITLE" \
  --label "$LABEL" \
  --assignee "$ASSIGNEE" \
  --project "$PROJECT" \
  --body-file "$BODY_FILE"
```

Repeat `--label` and `--assignee` per value. Omit `--project` entirely when there is none; an empty string
is an error. The command prints the created URL to stdout — capture it.

## 6. Verify, then report

Creation succeeding is not proof the metadata landed: a failed `--project` association does not always fail
the create.

```bash
gh issue view "$NUMBER" --repo "$REPO" --json number,title,labels,assignees,projectItems,url
```

Confirm the labels, assignees and project are what was approved, and **compare the returned URL's repo to
the one you passed**. GitHub silently follows rename redirects, so `--repo org/old-name` can file into
`org/new-name`. When they differ, say so plainly and use the returned name from then on.

Report the URL. If any metadata did not stick, say which and fix it with `gh issue edit` rather than
leaving it for the user to notice.

## 7. Persist what was learned

If this repo had no `issues` config and the user approved the discovered conventions, write them to
`$CONFIG_HOME/repos/$REPO_KEY/config.json`. Never write configuration into the target repository: no
committed config, no `.gitignore` edits, no CLAUDE.md changes.

## Completion criteria

- [ ] The issue exists, and its URL has been reported.
- [ ] Labels, assignees and project on the created issue match what the user approved.
- [ ] The repo in the returned URL is the repo that was intended.
- [ ] Every cross-reference to a sibling ticket resolves to a real issue number.
- [ ] The per-repo config reflects the approved conventions, or already did.
