# Issue Configuration Schema

Configuration for GitHub issue filing conventions, stored in `$CONFIG_HOME/repos/$REPO_KEY/config.json` or `$CONFIG_HOME/global/config.json`.

## Schema

```jsonc
{
  "issues": {
    "repo": "owner/repository",       // GitHub repo in owner/name format
                                      // Omit to use current directory's origin
    
    "project": "Backlog",             // Project title where issues should be added
                                      // Set to null for no project
    
    "labels": ["bug", "backend"],     // Array of label names to apply to all issues
                                      // Labels must already exist in the repo
    
    "assign_self": true,              // Assign the current GitHub user to issues
                                      // Default: false
    
    "extra_assignees": ["username"],  // Additional GitHub usernames to assign
                                      // Users must have repo access
    
    "body_sections": [                // Section headings for issue body structure
      "Deliverable",                  // Mirrored from existing issues
      "Why",                          // Can be customized per repo
      "What to build",
      "Done when",
      "References"
    ]
  }
}
```

## Field Details

### `repo`
- Format: `owner/repository`
- When omitted: Uses the current directory's git remote origin
- Example: `"trykudos/personalization"`

### `project`
- The title (not ID) of a GitHub Project to add issues to
- Must match exactly (case-sensitive)
- Set to `null` or omit to skip project assignment
- Requires `project` scope on GitHub token: `gh auth refresh -s project`

### `labels`
- Array of label names that exist in the repository
- Labels are NOT created automatically
- To create missing labels: `gh label create <name> --description "..." --color <hex>`
- Multiple labels are applied with repeated `--label` flags

### `assign_self`
- When `true`, assigns the current authenticated GitHub user
- When `false` or omitted, no self-assignment
- Determined by `gh api user` at issue creation time

### `extra_assignees`
- Array of GitHub usernames
- Each user must have repository access or assignment silently fails
- Applied in addition to self-assignment when `assign_self: true`

### `body_sections`
- Array of heading names for structuring the issue body
- Discovered from existing issues during first use
- Can be manually customized after discovery
- Used as a template when drafting new issues

## Discovery vs Configuration

When no `issues` block exists for a repository, the skill:

1. Reads recent issues to find common labels and projects
2. Reads one issue body to mirror its structure
3. Proposes discovered conventions in the confirmation step
4. Writes approved conventions to `$CONFIG_HOME/repos/$REPO_KEY/config.json`

This happens once per repository. Subsequent invocations use the persisted config.

## Configuration Precedence

Highest to lowest:

1. **Inline arguments** (ephemeral, this invocation only)
   - `--repo owner/name`
   - `--project "Project Title"`
   - `--label labelname` (repeat for multiple)
   - `--assignee username` (repeat for multiple)

2. **Per-repo config** at `$CONFIG_HOME/repos/$REPO_KEY/config.json`

3. **Global config** at `$CONFIG_HOME/global/config.json`

4. **Discovered conventions** from the repo's existing issues

## Example Configuration

### Personal config for all repos
`~/.config/marcjimenez/global/config.json`:
```json
{
  "issues": {
    "assign_self": true
  }
}
```

### Per-repo override
`~/.config/marcjimenez/repos/skills-a1b2c3d4/config.json`:
```json
{
  "issues": {
    "repo": "marcjimenez/skills",
    "project": "Backlog",
    "labels": ["enhancement"],
    "assign_self": true,
    "body_sections": [
      "Summary",
      "Motivation",
      "Implementation",
      "Acceptance Criteria"
    ]
  }
}
```

## Config Home Resolution

Cross-platform config directory:

- **macOS / Linux**: `${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez`
- **Windows**: `%APPDATA%\marcjimenez`

Repository key format: `<basename>-<sha1-prefix>` where `sha1-prefix` is the first 8 characters of the full repo path's SHA1 hash. This ensures unique keys even when basename collides.
