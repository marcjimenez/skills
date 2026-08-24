# Code slop tells

Code slop is contextual: a pattern is slop when it is redundant, inconsistent with its own file or repo,
or defends against a state that cannot happen, NOT merely when it is thorough. Read the exclusions at the
bottom before flagging. Comment rules live in `/marcjimenez:coding-style` `reference/COMMENTS.md`; this
file cites them rather than restating them.

## Comments

- Narrating the line: `// increment the counter` above `counter++`; `// loop through users`. Delete. Which
  comments earn their place is owned by COMMENTS.md.
- Pro-forma docstrings on trivial private helpers: a full docstring on a two-line internal function.
  Strip it; the public-versus-private docstring rule is in COMMENTS.md.
- Section-divider and banner comments: `# ===== USER AUTH =====`, ASCII banners, emoji-prefixed headers.
  Delete; let module and function structure organize the file.

## Error handling and defensiveness

- Redundant try/catch that swallows the error: `try { await save(user) } catch (e) { /* ignore */ }`
  around code with no real failure mode there. Remove it, or make the catch do something meaningful
  (typed error, retry, log-with-context, rethrow). Catch specific exceptions, not everything.
- Defensive checks for impossible states: `if (!user) return` on a non-nullable typed argument, or a
  `typeof x !== 'string'` guard on a typed-string field. Trust the type; validate once at the trust
  boundary, not on every internal call.
- Excessive optional chaining "to be safe": `order?.customer?.address?.city` where every field is required.
  Chain only where a value is genuinely nullable, so a real null throws loudly instead of yielding
  `undefined`.

## Naming and consistency

- Verbose names that restate the type: `userDataObject`, `total_user_input_character_count`. Match local
  naming; drop redundant `Object`/`Data`/type suffixes.
- Naming or style inconsistent within one file: the same concept as `userData` in one function and
  `userInfo` two functions later; half-renamed variables. Pick one and apply it throughout the scope.

## Dead weight and stubs

- Unused imports and dead scaffolding: imports never referenced, leftover code from a prior attempt.
  Delete.
- Leftover debug output: `console.log`/`print` in production paths. Remove, or route through the project's
  real logger at the right level.
- "TODO: implement" stubs shipped as done: functions that `pass`, `return None`, `...`, `return 0`, or
  raise `NotImplementedError` behind a finished-looking signature. Implement it, or delete the stub and
  track the gap in an issue.

## Reinvention and duplication

- Reimplementing stdlib / lodash / framework utilities: a hand-rolled `debounce`, `groupBy`, `chunk`,
  date math. The naive version misses edge cases the library handles. Use the existing one
  (`/marcjimenez:reuse`).
- Copy-pasted duplicate or near-clone blocks: byte-identical functions, or the same block pasted across
  files. Extract once real duplication exists (rule of three), then call it.

## Over-engineering

- Single-use abstractions, premature interfaces, one-call-site factories: `const getUserFactory = () =>
  ({ get: id => db.users.find(id) })`. Inline it; call the underlying function directly.
- Wrapping everything in a class; pass-through getters/setters that add no logic. Use a function or a
  plain/dataclass attribute; add a property only when access needs real logic.

## Type escapes and dependencies

- `as any`, `# type: ignore`, `# noqa` used to silence the checker instead of fixing the type. Type it
  correctly and resolve the underlying mismatch.
- Hallucinated, unnecessary, or stale-pinned dependencies: imports of packages that do not exist, wrong
  module paths, a heavyweight dep for a one-liner, or a training-era-old pinned version. Verify every
  import resolves; prefer the stdlib or an existing dependency; pin current versions.

## Formatting and messages

- Over-formal error messages off-key with the codebase: a grammatically perfect full-sentence message in a
  repo that throws `Error("invalid email")`. Match the team's terse style.
- Magic-number config that never changes: bare timeouts, limits, and retry counts inline. Hoist to a named
  constant, unless the literal is genuinely local and self-evident.

## Meta-tell (provenance, not a defect)

A single, huge, "surgically clean" first commit (every branch handled, full docs, perfectly sorted
imports, 200+ lines at once) is a sign of machine generation, but it is not a defect in any line. Do not
strip good code because it arrived all at once; use it as a prompt to review harder and split into logical
commits.

## Exclusions: NOT slop, do not strip

- Descriptive names, docstrings, type hints, and real error handling on PUBLIC surfaces or at genuine
  trust boundaries. These are good practice; they are slop only when uniform on trivial/private code,
  inconsistent with the file, or swallowing errors.
- Sorted and grouped imports and consistent formatting. Linters enforce these team-wide; do not un-sort
  imports to look human.
- Small single-responsibility functions. Slop only at the extreme of over-fragmentation (a 3-line function
  split into three 1-line functions).
- Correct optional chaining on genuinely nullable values. Removing it introduces crashes.
- "Too clean" as a quality judgment. Cleanliness is not a defect.
- Comprehensive branch and error handling at a real trust boundary. Only handling of impossible states or
  trusted internal paths is slop.

The unifying rule: slop is redundant, inconsistent, or defends the impossible. Thoroughness alone is not
slop.

## Optional deterministic backstop (off by default)

The catalog above is judgment plus greppable word lists, which is enough for v1. Where a repo already has
linters, they catch a subset mechanically and can run as a backstop, but they are not a dependency of this
skill:

- JS/TS: eslint-plugin-sonarjs (`no-identical-functions`, `cognitive-complexity`, `no-useless-catch`,
  `prefer-single-boolean-return`), eslint-plugin-unicorn (prefer-native), knip (unused files/exports/deps;
  supersedes the archived ts-prune and depcheck).
- Python: Ruff (`F401` unused import, `F841` unused variable, `E722` bare except, the `SIM` and `PL`
  categories).

Linters cannot judge whether a comment is noise, whether an abstraction is premature, or whether
idiomatic-looking logic is actually wrong. Those stay judgment calls.

## Sources

arXiv 2510.03029 (LLM code smells, avg +63%); arXiv 2307.12596 (ChatGPT code quality, ~47% style);
aislop (github.com/scanaislop/aislop); ai-slop-detector (github.com/flamehaven01/ai-slop-detector);
sloplint (github.com/dannote/sloplint, AST comment slop); refactoring.guru smells; Fowler YAGNI; Kent Beck
Tidy First?; Addy Osmani "Code Review in the Age of AI".
