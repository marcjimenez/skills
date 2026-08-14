# Comments — say the non-obvious thing, once

Comments get the same minimalism as code. A comment nobody needs is not free: it is a line to read, a
line to keep true, and a line that dilutes the ones that matter.

## The two tests

Apply both before keeping any comment.

**1. Ousterhout's test.** Could somebody who has never seen this code have written this comment just by
reading the code next to it? If yes, delete it. Note *obvious to whom*: obvious to someone reading it for
the first time, not to you. His review rule is that if a reader says something is not obvious, it is not
obvious — do not argue. Comments must sit at a **different level of detail** from
the code: lower (precision the code cannot express) or higher (intent it cannot express). A comment at the
*same* level is a restatement, which is the most common failure.

**2. Google's test.** Comments should explain **why**, not **what**:

> Usually comments are useful when they explain *why* some code exists, and should not be explaining
> *what* some code is doing. If the code isn't clear enough to explain itself, then the code should be
> made simpler. […] mostly comments are for information that the code itself can't possibly contain, like
> the reasoning behind a decision.

The second sentence is the one people skip. **A comment you need in order to explain *what* is a
refactoring signal, not a writing task.**

## Before writing the comment, try these instead

From Google's *To Comment or Not to Comment*. In order:

| Instead of a comment | Do this |
|---|---|
| `// Subtract discount from price.` | Introduce an explaining variable (`discount = …`) |
| `// Filter offensive words.` | Extract a method (`filterOffensiveWords(words)`) |
| `int width; // Width in pixels.` | Rename (`widthInPixels`) |
| `// Safe since height is always > 0.` | Add the check (`checkArgument(height > 0)`) |

The kernel puts it hardest: *"NEVER try to explain HOW your code works in a comment: it's much better to
write the code so that the working is obvious."* It also treats a comment **inside a function body** as a
signal to split the function instead.

Fowler and Beck name the underlying smell: *"comments are often used as a deodorant. It's surprising how
often you look at thickly commented code and notice that the comments are there because the code is bad.
When you feel the need to write a comment, first try to refactor the code so that any comment becomes
superfluous."*

## Anti-patterns, each with a detection test

| Anti-pattern | Test | Fix |
|---|---|---|
| **Restates the code** | The comment and the line below say the same thing | Delete |
| **Explains HOW** | Narrates the mechanism step by step | Delete, or refactor until it is obvious |
| **Explains the language or library** | Teaches what the docs teach | Delete |
| **Debug narrative** | Contains how the bug was found, what you tried, "this only shows up when…" | Move to the commit message |
| **Describes the edit, not the code** | Says what changed, or argues with a past decision | Move to the commit message; git already holds it |
| **Justifies the author** | "deliberately", "on purpose", "note that" | Delete unless a reader would otherwise *undo* it |
| **Essay where a clause would do** | Three sentences making one point | Cut to one |
| **Repeated across sites** | Same explanation in 2+ places | Document once at the most obvious site; elsewhere write `See the comment in xyz`. A broken pointer is self-evident; a stale duplicate is not |
| **Same words as the code** | The comment reuses the identifier's own words | Use *different* words that add meaning. `downCastParameter` documented as "Downcast PARAMETER to TYPE" adds only the word "to" |
| **Boilerplate docstring** | Restates the signature or the types | Delete. In TS the types are already in the signature |
| **Deodorant** | The comment exists because the code is hard to follow | Refactor until the comment is superfluous |
| **Contradicts the code** | Comment and code disagree after an edit | Fix or delete. A stale comment is worse than none, and has protracted many a debugging session |

## Do not overcorrect

Read this before you start cutting. The rules above target **restatement and narrative**, not comments as
such. Ousterhout, who has argued this at length with Robert Martin, puts the asymmetry bluntly:

> For me the cost of missing comments is easily 10-100x the cost of incorrect comments.

and on the usual excuse for writing none:

> Some people believe that if code is written well, it is so obvious that no comments are needed. This is a
> delicious myth.

Martin concedes the ground that matters, and his concession is the best shared test: **the best comments
tell you something surprising and verifiable about the code.** Surprising and verifiable, keep. Neither,
cut.

A second practical test, from the Google Python guide: *"If you're going to have to explain it at the next
code review, you should comment it now."*

And the framing that resolves the apparent conflict with minimalism, from Hillel Wayne on Chesterton's
fence: documenting *why* code exists is not an obstacle to deleting it, it is **the precondition for
deleting it safely**. A comment that lets the next person remove the code with confidence has paid for
itself.

So: cut the essay, keep the contract.

## Keep these

TotT's four legitimate categories, which are the ones worth defending:

- **Intent / rationale.** `// Compute once because it's expensive.`
- **Protecting a future editor from "fixing" it.** `// New instance because Foo is not thread-safe.`
- **A clarification raised in review.** `// Note that order matters because…`
- **Justifying an apparent bad practice.** `@SuppressWarnings("unchecked") // The cast is safe because…`

Add three more that survive even a hostile minimalist reading:

- **Interface contracts** — which parts of the behaviour a caller may rely on and which may change. There
  is no way to state this in code, so omitting it leaves the interface undefined.
- **Cross-module invariants** — the reader structurally cannot see the other end of the coupling. Put the
  explanation in one place and point at it from each site rather than repeating it.
- **A cross-system gotcha the type system cannot catch** — engine quirks, wire formats, replica staleness.

Even these get a sentence or two. The fact goes in the code; the story goes in the commit.

**TODOs carry a tracked link**, not a name: `// TODO: <bug url> - explanation`. Google prefers a bug
reference *"because bugs are tracked and have follow-up comments"*.

## Comments vs documentation vs the commit

These are three different artifacts. Most over-long comments are the commit message leaking into source.

| Content | Home |
|---|---|
| What this is, how to use it, how it behaves | **Doc comment** (`/** */`), for consumers |
| A constraint or gotcha at one line | **`//` comment** at that line, for maintainers |
| Why the change was made, what broke, how you found it | **Commit message** |
| Measurements, alternatives weighed, review history | **PR description** |

Google draws the commit boundary as: *"Were there decisions you made that aren't reflected in the source
code?"* — those go in the change description. A comment carries facts about the code's **present state**;
the commit carries the story of **the edit**.

**The sources disagree here, and the disagreement is worth knowing.** Ousterhout (§16.3) argues the
opposite of the row above: rationale put only in a commit message is *effectively lost*, and the concrete
risk is that somebody later undoes the change and recreates the bug.

Resolve it with one test:

> **Would a reader who does not know this undo it?**

If yes, a short comment goes in the code, even though the full story is in the commit. If no — it is how
you found it, what you tried, what the numbers were — the commit is enough. So `// not a backslash: this
engine reads one inside a literal as its own escape` earns its line, while the paragraph about how that
was discovered does not.

Note that documentation is explicitly *not* the same category as comments: it *"should instead express the
purpose of a piece of code, how it should be used, and how it behaves when used"*, and is still required
on public surface even where the why-not-what rule would suppress an inline comment.

## TypeScript specifics

- **`/** */` is for consumers, `//` is for maintainers.** *"Use `/** JSDoc */` comments for documentation,
  i.e. comments a user of the code should read. Use `// line comments` for implementation comments."*
  A JSDoc block on a module-private helper is usually the wrong form: make it `//` or delete it.
- **Multi-line implementation comments use stacked `//`, not `/* */`.** The Google TS guide requires this
  (and differs from the JS guide here).
- **Never restate types.** *"JSDoc type annotations are redundant in TypeScript source code."* No `@param`
  types, no `@return` types.
- `@param` earns its place only when it adds a constraint: `@param amountLitres The amount to brew. Must
  fit the pot size!` — and the sibling `logger` param gets no line at all.

## Length

**Do not set a ratio target.** This is the one place where a plausible-sounding number is actively harmful,
and there is a decisive precedent. SonarQube shipped exactly that gate — `InsufficientCommentDensity`,
default 25% — and deprecated it in 2022. SonarSource's own reasoning:

> We don't believe it makes sense to enforce such practice in 2022 […] very artificial and doesn't
> guarantee that in the end, the code will have better quality […] developers may be tempted to write
> fake/useless comments "because Sonar ask it" to get a green quality gate.

The one large measurement of real ratios (Arafat & Riehle, 5,229 OSS projects) found mean 18.7%, median
16.7%, **standard deviation 0.109** — a spread over half the mean. Published studies across the field range
from 0.09% to 50%. There is no central tendency to prescribe from, and the authors flagged the link to
maintainability as an *assumption* they had not tested. No major style guide mandates a ratio.

**The real argument for brevity is rot, and it is measured.** Wen et al. (ICPC 2019) mined 1.3 billion
AST-level changes across 1,500 systems and found code and comments co-evolve in only **7% of cases for
method comments** (13% for class comments). So roughly nine in ten code changes leave the comment
untouched. Every comment line is a line that will silently drift out of sync with the code it describes.
That is why you write fewer and shorter ones — not because a percentage said so.

Use these as smells, and never as gates:

- A comment block **longer than the code it introduces**. Kernighan & Pike: *"when the comment outweighs
  the code, the code probably needs fixing."*
- A block **covering 3+ unrelated topics**. Ousterhout §16.2: **push each comment down to the narrowest
  scope covering the code it refers to**; the farther a comment sits from what it describes, the more
  abstract it should be. A stack of unrelated notes above one statement is the commonest form.
- If documentation for a thing **has to be long to be complete**, that is a design smell rather than a
  comment smell — comments are *"a canary in the coal mine of complexity"*.
- If you want a lint number for block length, PMD's `CommentSize` defaults to **6 lines**. It is a tool
  convention with no empirical backing, it is opt-in, and it exempts headers. Treat it as a nudge.

Measuring is still useful for *finding* the outliers to read; just do not turn the number into a target:

```bash
awk '/^[[:space:]]*(\/\/|\/\*|\*)/{c++} /^[[:space:]]*[^[:space:]\/*]/{k++} \
  END{printf "%s: %d code, %d comment, %.2f\n", FILENAME, k, c, c/(k?k:1)}' FILE
```

## Promote by scope, not by length

Nothing says "over N lines, write a doc". The trigger is audience and reach:

| Reach | Home |
|---|---|
| One line or block | `//` comment at that line |
| One function or type | Interface docstring |
| Spans modules | One central design note, with short `See …` pointers from each site |
| Needs review, trade-offs, alternatives | Design doc (1–3 pages mini, 10–20 full) |
| Orients a directory | `README.md` |

## Schema docstrings that ship

GraphQL SDL, OpenAPI and public type docs are read by people choosing how to use the thing, often outside
your repo. They carry more weight than an implementation comment and are cut less aggressively. They are
still prose: lead with what it is, then the single non-obvious thing. Background, history and worked
examples belong in a doc, not in every field description.

## Sources

- [Google, What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Google, Writing good CL descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Google C++ Style Guide, Comments](https://google.github.io/styleguide/cppguide.html#Comments)
- [Code Health: To Comment or Not to Comment?](https://testing.googleblog.com/2017/07/code-health-to-comment-or-not-to-comment.html)
- [Linux kernel coding style, Commenting](https://docs.kernel.org/process/coding-style.html)
- [Linux kernel, Describe your changes](https://docs.kernel.org/process/submitting-patches.html) — the WHY
  belongs in the commit, written for someone reading it years later
- Kernighan & Pike, *The Practice of Programming* §1.6 — don't belabour the obvious; don't comment bad
  code, rewrite it; don't contradict the code
- Fowler & Beck, *Refactoring* — the Comments smell, and comments as deodorant
- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)
- Ousterhout, *A Philosophy of Software Design*, ch. 12–13 — the different-level-of-detail rule and the
  "Comment Repeats Code" red flag
- [Ousterhout vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code) — the cost asymmetry,
  and the counterweight against cutting too far
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) — the code-review test and
  the `TODO: <bug link> -` format
- [Chesterton's fence and code comments](https://spin.atomicobject.com/chestertons-fence-code-comments/)
- [SonarSource, deprecating the comment-density rule](https://community.sonarsource.com/t/deprecation-of-common-server-rules-sonar-16051/71088)
  — the decisive case against ratio gates
- [Wen et al., Code-Comment Inconsistencies, ICPC 2019](https://www.inf.usi.ch/lanza/Downloads/Wen2019a.pdf)
  — comments co-evolve with code in only 7% of method changes
- [Arafat & Riehle, Comment Density of OSS Code](https://dirkriehle.com/wp-content/uploads/2009/02/icse-2009-nier-for-web.pdf)
- [PMD CommentSize](https://docs.pmd-code.org/latest/pmd_rules_java_documentation.html)
