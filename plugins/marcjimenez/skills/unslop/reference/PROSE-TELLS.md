# Prose slop tells

Signal strength: S (strong), M (medium), W (weak, also common in good human writing). "Greppable" means a
regex or word-list catches it mechanically; the rest need judgment. Weigh every tell by density (SKILL.md
doctrine): a lone tell is rarely slop, a cluster is, and S tells count more per occurrence than W tells, so
fewer of them tip a passage over. A few tells are genuine flag-on-sight because they almost never appear in
earnest human writing; those are marked "flag on sight" inline below.

## Vocabulary (S, greppable)

Inflated words that spike in model output. Flag when several cluster; a lone one may be fine.

| Tell | Bad | Rewrite |
| --- | --- | --- |
| delve | "Let's delve into the config." | "Let's look at the config." |
| leverage (verb) | "We leverage caching." | "We use caching." |
| utilize / facilitate / commence / endeavor | "utilize the helper" | use / help / start / try |
| seamless / seamlessly | "seamless integration" | "integrates with no extra config" or delete |
| robust | "a robust solution" | name the property: "handles retries and partial failures" |
| boasts / features / offers (for "has") | "the API boasts three endpoints" | "the API has three endpoints" |
| testament to | "a testament to clean design" | delete, or state the fact |
| realm / landscape | "in the realm of testing" | "in testing" |
| tapestry | "a rich tapestry of services" | "several services" |
| underscore(s) | "this underscores the need" | "this shows we need" |
| pivotal / crucial / vital | "a pivotal step" | drop the adjective or quantify |
| elevate | "elevate the experience" | "improve the setup" |
| garner | "garner feedback" | "collect feedback" |
| foster | "foster collaboration" | "make it easier to collaborate" |
| myriad / plethora | "a myriad of options" | "many options" |
| nuanced / multifaceted / intricate | "a nuanced tradeoff" | state the actual tradeoff |

## Openers and filler (S, greppable)

- Era opener (flag on sight): "In today's fast-paced world...", "In an era where..." Delete the sentence;
  start with the point.
- "It's worth noting that" / "It's important to note that". The note is the sentence; drop the frame.
- "Let's dive in" / "deep dive". Delete; show the thing.
- Sycophantic opener (flag on sight): "Great question!", "Absolutely!", "I'd be happy to help." Delete;
  answer directly.

## Constructions (S/M, needs pattern match)

- "It's not just X, it's Y" (S, flag on sight). The single most notorious construction. Rewrite as a
  direct statement: "It's a linter that also enforces style."
- "not X, but Y" / "not only... but also" (M, flag on repetition of 3+). Rewrite to a plain declarative.
- Copula avoidance (S, greppable): "serves as / stands as / functions as / acts as" replacing "is/are".
  Restore the copula.
- Dangling-participle significance filler (S, greppable pattern `, highlighting the`): "...refactored the
  parser, highlighting the importance of clean code." Delete the participial tail.

## Rhythm and structure (W on density)

- Rule of three: "fast, scalable, and reliable." Autopilot triads. Keep the one true attribute. Classical
  rhetoric uses triads too, so flag only when they recur.
- Transitional-adverb stacking: paragraphs opening "Moreover,", "Furthermore,", "Additionally,". Flag when
  more than half of paragraphs open with a formal connector; vary or drop.
- Hedge stacking: "this might perhaps arguably be slightly faster." Multiple hedges in one sentence.
  Replace with the measured fact: "this is ~10% faster in the benchmark."
- Over-hedged modal stack: "this could potentially possibly break." Say when: "this breaks when the token
  is null."

## Closers (S, greppable)

- "In conclusion, ..." restating the obvious. Delete; a good doc needs no wrap-up.
- "Despite challenges, the future is bright." Outline-formula closer. State the concrete limitation and
  next step.
- Pseudo-wisdom: "At its core, good code is about good decisions." Profound-sounding, says nothing. Apply
  the deletion test.

## Attribution (M, greppable openers)

- "Experts agree that...", "Studies show...", "Research indicates..." with no name, link, or number. Cite
  the source or cut the claim.

## Tone (S/M)

- Promotional puffery in docs: "nestled in the heart of the stack", "a vibrant ecosystem". Neutral,
  factual description instead.

## Formatting (S/M, mostly greppable)

- Title Case Headings Everywhere: "## Getting Started And Setup". Use sentence case: "## Getting started".
- Emoji as bullets or section markers. Plain bullets or a short sentence.
- Bold-label fragment openers: "**Key takeaway:** always validate input." Write the sentence: "Always
  validate input." (Also a CLAUDE.md house rule.)
- Every bullet as "**Term**: gloss". Mechanical list scaffolding; use prose or plain bullets.
- Em-dash overuse (W): models emit them heavily, but many good writers use the dash and models were tuned
  to drop it, so absence proves nothing and presence proves little. Flag only on density. (Note: CLAUDE.md
  bans em-dashes and double-hyphens outright in Marc's own writing, so in this repo's prose remove them
  regardless and use commas, colons, periods, or parentheses.)

## The over-correction tell (caveman prose)

The opposite of slop is also detectable and also wrong. Stripping articles, conjunctions, dashes, and
connectors to sound un-AI produces clipped, telegraphic text with trailing fragments: "Fixed bug. Cache
broke. Now works." Removing a dash mechanically often leaves a sentence fragment where the clause was.
Reject this too. The target is natural, varied prose with normal grammar, not maximal terseness.

## Weak tells (do not flag alone)

Em-dashes, rule-of-three, "however / moreover" and academic connectors, a single hedge, and semicolons all
appear frequently in strong human writing. Flag these only on clustering or measurable density. When in
doubt, leave them and flag the stronger tells instead.

## Sources

Wikipedia "Signs of AI writing"; slopdetector.org (reproducible thresholds); slop-cop
(github.com/awnist/slop-cop, 36 rules with open word lists); em-dash counter-literature (PlagiarismToday,
The Ringer) for the over-correction failure mode; detector-unreliability evidence (PopSci, the Stanford
non-native-speaker study).
