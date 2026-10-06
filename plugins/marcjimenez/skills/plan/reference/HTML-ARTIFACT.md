# HTML artifacts — plans, research, and the questions page

## Contents

What this owns · Render it, do not assemble it · The body you write · The classes ·
The questions page · Where it goes and how it is seen · Why the shell is vendored

## What this owns

Four skills produce documents a person reads: `plan`, `research`, `brainstorm`, `requirements`. Each writes
its markdown as the source of record, then renders an HTML page beside it for reading. The markdown is what
`/marcjimenez:implement` and `grep` consume; the HTML is what you actually look at.

This file owns the shell both document types share. The skills own their own content.

## Render it, do not assemble it

```bash
"${CLAUDE_PLUGIN_ROOT}"/skills/plan/assets/render.py \
  --title "Plan — <slug>" --body /tmp/body.html --out "$RUN_DIR/plan.html" --open
```

**Never hand-assemble the page.** The script owns the mermaid loader, and that loader is the part that
keeps breaking: the stylesheet was vendored from a sample that loads its renderer from
`/_runtime/mermaid-11.16.1.min.js`, a path that resolves only inside the claude.ai artifact iframe. A
hand-built copy silently produced a page with no diagrams twice, because the house script checks
`typeof mermaid`, finds no global, and returns without complaint.

The script guarantees four things a hand-built page kept getting wrong: the public CDN rather than the
runtime path, the global published before the house script runs, both inside one module because a classic
script executes before an import resolves, and a `<details>` source block under every diagram that opens
itself when the renderer fails. It exits non-zero if a diagram ends up without its fallback.

## The body you write

A fragment: the inside of `<div class="wrap">`, no `<html>`, `<head>` or `<body>`. A `<nav class="toc">`
with anchors, then `<main>` with a `<header class="top">` and one `<section id="…">` per heading.

Diagrams are `<pre class="mermaid">` holding mermaid source. The script adds the fallback; do not write one.

## The classes

Vendored from the house sample, so a page written from them matches everything else:

| Class | Use |
|---|---|
| `eyebrow` `lede` `meta` `chip` | the header block; `chip` takes `ok`, `warn` or `risk` |
| `toc` | the sticky contents rail |
| `callout` `evidence` | a finding worth stopping on; `evidence` for a measured one |
| `tbl` | wraps a `<table>` |
| `qs` | the open-questions list |
| `tasks` | an ordered task list; `done` on a finished `<li>`, `.v` for its verify line |
| `cap` | a caption or an aside |

## The questions page

When a phase has **three or more** open assumptions, write one page instead of asking in sequence. Below
three, `AskUserQuestion` is lighter than a page deserves.

Every question carries what is needed to decide it: a diagram where the shape is the question, a code
sample where the difference is in the code. Single-answer questions render as radios, multi-answer as
checkboxes, with the recommendation preselected. A **Copy answers** button serialises the selections:

```html
<form id="qs">
  <fieldset data-n="1"><legend>Which reconvergence shape?</legend>
    <label><input type="radio" name="q1" value="a" checked> Independent PRs</label>
    <label><input type="radio" name="q1" value="b"> One integration branch</label>
  </fieldset>
</form>
<button onclick="navigator.clipboard.writeText(collect(document.getElementById('qs')))">Copy answers</button>
<script>
function collect(form) {
  return [...form.querySelectorAll("fieldset[data-n]")].map(q => {
    const picked = [...q.querySelectorAll("input:checked")].map(i => i.value);
    return `${q.dataset.n}=${picked.join("+") || "skip"}`;      // "1=b, 2=a+c, 3=skip"
  }).join(", ");
}
</script>
```

Also select the text on click, because `navigator.clipboard` needs a user gesture and can fail silently on
a `file://` URL. One click-through, one paste, no sequencing.

## Where it goes and how it is seen

Beside the markdown, in the run directory: `plan.html`, `research.html`, `questions.html`.

`--open` launches the default browser, which works in Conductor, in Claude Desktop and from the CLI, because
all three have a shell. **Where an Artifact tool is available, publish the same HTML to it as well**: that
is the better reading experience on Claude Desktop and claude.ai, and it is additive rather than a
replacement. Conductor has no Artifact tool, so the file is the only thing guaranteed to exist everywhere.

Print the path either way. A page nobody is told about is a page nobody opens.

## Why the shell is vendored

`artifact-design`, the built-in that produced the original sample, is not on disk and does not exist inside
Conductor. It cannot be reused by reference, so `assets/shell.css` and `assets/shell.js` are copies and this
repo owns them. Refresh them deliberately from a newer sample rather than letting them drift; nothing keeps
them in step automatically.
