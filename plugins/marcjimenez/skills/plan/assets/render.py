#!/usr/bin/env python3
"""Wrap a body fragment in the house HTML shell and write a self-contained page.

The shell is a script rather than instructions because the loader is the part that keeps breaking. The
sample this was vendored from loads mermaid over a claude.ai-only path, and a hand-assembled copy silently
produced a page with no diagrams twice. Nothing here is re-derived per run.

    render.py --title "Plan — slug" --body body.html --out plan.html [--open]

Body is a fragment: the content of <div class="wrap">, no html/head/body. Diagrams are <pre class="mermaid">.
"""
import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
FONTS = ("https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700"
         "&family=JetBrains+Mono:wght@400;500&display=swap")
# Public CDN, never a /_runtime/ path: that resolves only inside the claude.ai artifact iframe.
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


def diagram_fallback(body):
    """Every diagram gets its source in a <details>, so a failed CDN degrades to readable text.

    Without it the failure is invisible: the house script finds no global, returns, and leaves a blank.
    """
    def wrap(m):
        src = html.escape(m.group(1).strip())
        return (f'{m.group(0)}\n<details class="dsrc"><summary>diagram source</summary>'
                f'<pre><code>{src}</code></pre></details>')
    return re.sub(r'<pre class="mermaid">(.*?)</pre>', wrap, body, flags=re.S)


def build(title, body):
    css = (ASSETS / "shell.css").read_text()
    house = (ASSETS / "shell.js").read_text()
    # One module: a classic script would execute before the import resolves, which is the original bug.
    script = (
        '<script type="module">\n'
        'let loaded = false;\n'
        'try {\n'
        f'  const m = await import("{MERMAID}");\n'
        '  window.mermaid = m.default ?? m;   // the house script reads a GLOBAL, not an import\n'
        '  loaded = true;\n'
        '} catch (e) { console.error("mermaid failed to load", e); }\n'
        'if (loaded) {\n' + house + '\n} else {\n'
        '  for (const el of document.querySelectorAll("details.dsrc")) el.open = true;\n'
        '  for (const b of document.querySelectorAll("pre.mermaid")) {\n'
        '    b.insertAdjacentHTML("beforebegin",\n'
        '      \'<p class="cap" style="color:var(--risk)">Diagram renderer unavailable; '
        'source shown below.</p>\');\n'
        '    b.style.display = "none";\n'
        '  }\n'
        '}\n</script>'
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f'<title>{html.escape(title)}</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="{FONTS}">'
        f'<style>{css}</style></head><body><div class="wrap">{diagram_fallback(body)}</div>'
        f'{script}</body></html>'
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", required=True, type=Path, help="body fragment, or - for stdin")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--open", action="store_true", help="open it in the default browser")
    a = ap.parse_args()

    body = sys.stdin.read() if str(a.body) == "-" else a.body.read_text()
    out = build(a.title, body)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(out)

    diagrams = out.count('<pre class="mermaid">')
    fallbacks = out.count('details class="dsrc"')
    print(f"{a.out}  {len(out)} bytes, {diagrams} diagram(s), {fallbacks} fallback(s)")
    if diagrams and fallbacks != diagrams:
        print("WARNING: a diagram has no source fallback", file=sys.stderr)
        return 1
    if a.open:
        subprocess.run(["open", str(a.out)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
