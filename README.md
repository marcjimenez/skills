# Skills

Personal Claude Code skills marketplace for Marc Jimenez.

## Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `langgraph-agent` | `development-beta` | Full-cycle LangGraph agent development workflow with task tracking, eval analysis, and 5-subagent code review |

## Usage

Add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "marcjimenez-skills": {
      "source": {
        "source": "github",
        "repo": "marcjimenez/skills"
      }
    }
  }
}
```

Then enable per-project in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "langgraph-agent@marcjimenez-skills": true
  }
}
```
