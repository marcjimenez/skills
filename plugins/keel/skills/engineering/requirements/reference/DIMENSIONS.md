# Requirements dimensions

The dimensions to interrogate (the DO/DON'T method and the confirmation GATE live in `SKILL.md`):

| Dimension | Question |
|-----------|----------|
| Scope | What is IN scope? What is explicitly OUT? |
| I/O | What data enters? What comes out? What format? |
| Errors | What happens when X fails? Silent? Retry? Propagate? |
| Integration | What other modules/services are touched? |
| Contracts | Does this change any API, schema, type, or interface? |
| Edge cases | What are the weird inputs? Empty? Null? Concurrent? |
| Done | What specific observable behavior means "this works"? |

## Inputs to fetch first

- A URL in the request → fetch and analyze it (WebFetch) before grilling.
- A PRD / ticket / doc reference → pull it, parse into structured requirements.

## Output

The confirmed numbered spec is what feeds `/keel:plan` or `/keel:implement`.
