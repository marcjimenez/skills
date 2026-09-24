#!/usr/bin/env python3
"""Merge path-keyed cache directories into repository-keyed ones.

REPO_KEY used to hash the checkout path, so every git worktree and every Conductor workspace of the
same repository got its own cache: its own integration_test recipe, its own code_review waivers, its
own runs. This folds them together under the key the current derivation produces.

Dry run by default. Pass --apply to move anything.
"""
import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "marcjimenez"
REPOS = CONFIG_HOME / "repos"
DEFAULT_SEARCH = [Path.home() / "conductor" / "repos", Path.home() / "conductor" / "workspaces"]
# Dropped into every destination. Without it a second run finds no live checkout for a hand-mapped
# directory, lists the destination it just built as unresolved, and invites you to re-map it.
MARKER = ".migrated-into"
# The single source of truth for the key, lifted from the skills at runtime. A second copy here is
# what let the two drift apart once already: the shell block gained insteadOf handling, lowercasing and
# a local-path guard, and the Python copy silently kept computing a different key.
BLOCK_SOURCE = Path(__file__).resolve().parent.parent / (
    "plugins/marcjimenez/skills/setup/reference/CONFIG-SCHEMA.md"
)
BLOCK_RE = re.compile(
    r"^# One cache per REPOSITORY.*?^\[ -n \"\$REPO_KEY\" \] \|\| \{ echo \"not in a git repository\".*?$",
    re.S | re.M,
)


def key_block():
    try:
        text = BLOCK_SOURCE.read_text()
    except OSError as exc:
        sys.exit(f"cannot read the REPO_KEY block from {BLOCK_SOURCE}: {exc}")
    m = BLOCK_RE.search(text)
    if not m:
        sys.exit(f"could not find the REPO_KEY block in {BLOCK_SOURCE}")
    return m.group(0) + '\nprintf "%s" "$REPO_KEY"\n'


def key_from_remote(checkout, block):
    """Run the skills' own derivation in the checkout, so there is exactly one definition of the key."""
    r = subprocess.run(["sh", "-c", block], cwd=checkout, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def legacy_key(path):
    """The old derivation: basename plus 8 chars of sha1 of the checkout path."""
    p = str(path)
    return f"{Path(p).name}-{hashlib.sha1(p.encode()).hexdigest()[:8]}"


def live_checkouts(roots):
    for root in roots:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if (d / ".git").exists():
                yield d
            elif d.is_dir():
                for sub in sorted(d.iterdir()):
                    if (sub / ".git").exists():
                        yield sub


def load_config(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        print(f"    skipped unreadable {path}: {exc}")
        return None


def recipe_fingerprint(cfg_path):
    """Identical integration_test recipes mean the same repository, re-derived."""
    cfg = load_config(cfg_path) if cfg_path.exists() else None
    recipe = (cfg or {}).get("integration_test")
    if not recipe:
        return ""
    return hashlib.sha1(json.dumps(recipe, sort_keys=True).encode()).hexdigest()[:10]


def cited_slugs(d):
    """owner/repo slugs mentioned in this directory's run artifacts, by citation count."""
    counts = Counter()
    for f in d.rglob("*.md"):
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r"github\.com[/:]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", text):
            counts[re.sub(r"\.git$", "", m.group(1))] += 1
    return counts


def guess_repo(d, known_repos):
    """Most-cited GitHub repo in this directory's artifacts. A hint only, never applied.

    Wrong often enough to matter: a run that troubleshoots a dependency cites that dependency, and a
    run in one repo that references a sibling can cite the sibling more than its own. So flag the case
    we CAN detect, where the directory is named after a repo that exists and the citations disagree.
    """
    counts = cited_slugs(d)
    if not counts:
        return "", ""
    slug, count = counts.most_common(1)[0]
    key = slug.replace("/", "-")
    note = f"  ({count} citation{'s' if count > 1 else ''})"
    stem = re.sub(r"-[0-9a-f]{8}$", "", d.name)
    if stem in known_repos and not key.endswith("-" + stem):
        note += f"  ** but this directory is named '{stem}', which is itself a repo **"
    return key, note


def merge_configs(dst_path, src_paths):
    """Fold sources into the destination, oldest first, so the newest copy of a section wins.

    Sources are ordered up front rather than compared against the destination as the loop runs: the
    destination is rewritten mid-loop, so comparing against it makes every source after the first look
    older, and the surviving recipe becomes the first one processed instead of the freshest.
    """
    merged, log = {}, []
    if dst_path.exists():
        merged = load_config(dst_path) or {}

    ordered = sorted((p for p in src_paths if p.exists()), key=lambda p: p.stat().st_mtime)
    seen, waivers = set(), []
    for w in merged.get("code_review", {}).get("waivers", []):
        seen.add((w.get("area"), w.get("divergence")))
        waivers.append(w)

    for src_path in ordered:
        src = load_config(src_path)
        if src is None:
            continue
        for w in src.get("code_review", {}).get("waivers", []):
            ident = (w.get("area"), w.get("divergence"))
            if ident not in seen:
                seen.add(ident)
                waivers.append(w)
        for section, value in src.items():
            if section not in merged:
                merged[section] = value
            elif merged[section] != value:
                log.append(f"      {section}: took the copy from {src_path.parent.name}")
                merged[section] = value
    if waivers:
        merged.setdefault("code_review", {})["waivers"] = waivers
    return merged, log


def write_json(path, data):
    """Write via a sibling temp plus os.replace, which POSIX guarantees is atomic.

    Mid-loop this file is the only copy of the accumulated waiver union: the sources merged before it
    have already been renamed .migrated, so a truncated write loses them.
    """
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(json.dumps(data, indent=2) + "\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def free_path(path):
    """shutil.move onto an existing directory moves INTO it, so never hand it a name in use."""
    if not path.exists():
        return path
    n = 2
    while path.with_name(f"{path.name}-{n}").exists():
        n += 1
    return path.with_name(f"{path.name}-{n}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually move; omit for a dry run")
    ap.add_argument("--map", action="append", default=[], metavar="DIR=KEY",
                    help="map a directory the script could not resolve; repeatable")
    ap.add_argument("--search", default=os.environ.get("MIGRATE_SEARCH", ""),
                    metavar="PATHS", help=f"{os.pathsep}-separated roots to scan for checkouts "
                                          f"(default: {os.pathsep.join(str(p) for p in DEFAULT_SEARCH)})")
    args = ap.parse_args()

    roots = [Path(p) for p in args.search.split(os.pathsep) if p] or DEFAULT_SEARCH
    manual = {}
    for entry in args.map:
        if "=" not in entry:
            ap.error(f"--map expects DIR=KEY, got {entry!r}")
        k, v = entry.split("=", 1)
        manual[k] = v

    if not REPOS.is_dir():
        sys.exit(f"nothing to migrate: {REPOS} does not exist")

    block = key_block()
    stored = [
        d for d in sorted(REPOS.iterdir())
        # free_path also produces .migrated-2, .migrated-3 on a later wave; none of them are orphans.
        if d.is_dir() and not re.match(r".*\.migrated(-\d+)?$", d.name) and not (d / MARKER).exists()
    ]

    # Pass 1: a stored key whose checkout still exists resolves through that checkout's remote.
    resolved, by_fingerprint, current_keys = {}, {}, set()
    for checkout in live_checkouts(roots):
        new = key_from_remote(checkout, block)
        if not new:
            continue
        current_keys.add(new)
        d = REPOS / legacy_key(checkout)
        if d.is_dir():
            resolved[d.name] = new
            fp = recipe_fingerprint(d / "config.json")
            if fp:
                by_fingerprint[fp] = new

    # Pass 2: an orphan sharing a resolved directory's recipe is the same repo, re-derived.
    for d in stored:
        if d.name in resolved:
            continue
        fp = recipe_fingerprint(d / "config.json")
        if fp and fp in by_fingerprint:
            resolved[d.name] = by_fingerprint[fp]

    # Pass 3: whatever was mapped by hand.
    for k, v in manual.items():
        if (REPOS / k).is_dir():
            resolved[k] = v
        else:
            print(f"  --map {k}={v}: no such directory, ignored\n")

    # A directory already carrying a correct key is done, not unresolved. Without this the second
    # --apply run invites you to re-map the destination it just built.
    done = set(resolved.values()) | current_keys
    unresolved = [d for d in stored if d.name not in resolved and d.name not in done]

    print(f"{'APPLYING' if args.apply else 'DRY RUN'} — {REPOS}\n")
    groups = {}
    for old, new in sorted(resolved.items()):
        groups.setdefault(new, []).append(old)

    for new, olds in sorted(groups.items()):
        print(f"  {new}")
        for old in olds:
            runs = (REPOS / old / "runs")
            n = len(list(runs.iterdir())) if runs.is_dir() else 0
            print(f"    <- {old:<44} {n} run(s)")
        print()

    known_repos = {k.split("-", 1)[1] for k in resolved.values() if "-" in k}
    for d in stored:
        for slug in cited_slugs(d):
            known_repos.add(slug.split("/", 1)[1])

    if unresolved:
        print("  unresolved — no live checkout and no matching recipe.")
        print("  The guess column reads GitHub URLs out of the run artifacts. It is a hint, not a")
        print("  verdict: a run that discusses another repo more than its own points at the wrong one.")
        print("  Apply one with --map <dir>=<key>.\n")
        for d in unresolved:
            cfg = load_config(d / "config.json") if (d / "config.json").exists() else None
            keys = ", ".join(cfg.keys()) if cfg else "no config"
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
            guess, note = guess_repo(d, known_repos)
            print(f"    {d.name:<46} {size // 1024:>5} KB  [{keys}]")
            if guess:
                print(f"    {'':<46} guess: {guess}{note}")
        print()

    if not args.apply:
        print("Nothing changed. Re-run with --apply to move.")
        return 0

    for new, olds in sorted(groups.items()):
        dst = REPOS / new
        sources = [REPOS / old for old in olds if REPOS / old != dst]
        if not sources:
            continue
        dst.mkdir(parents=True, exist_ok=True)
        (dst / MARKER).write_text(f"merged from: {', '.join(olds)}\n")

        merged, log = merge_configs(dst / "config.json", [s / "config.json" for s in sources])
        if merged:
            write_json(dst / "config.json", merged)

        # Every move registers its own inverse. If anything raises, the stack unwinds and the group is
        # put back; pop_all() discards the inverses once the whole group has landed.
        with contextlib.ExitStack() as undo:
            for src in sources:
                runs = src / "runs"
                for sub in sorted(runs.iterdir()) if runs.is_dir() else []:
                    target = free_path(dst / "runs" / sub.name)
                    if target.name != sub.name:
                        log.append(f"      run slug {sub.name} collided, kept as {target.name}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(sub, target)
                    undo.callback(shutil.move, target, sub)
                if (src / "utilities.md").exists() and not (dst / "utilities.md").exists():
                    shutil.move(src / "utilities.md", dst / "utilities.md")
                    undo.callback(shutil.move, dst / "utilities.md", src / "utilities.md")
                # Renamed, never deleted, so a bad merge is reversible.
                parked = free_path(src.with_name(src.name + ".migrated"))
                shutil.move(src, parked)
                undo.callback(shutil.move, parked, src)
            undo.pop_all()

        n_runs = len(list((dst / "runs").iterdir())) if (dst / "runs").is_dir() else 0
        n_waivers = len(merged.get("code_review", {}).get("waivers", []))
        print(f"  {new}: {n_runs} run(s), {n_waivers} waiver(s)")
        for line in log:
            print(line)

    print("\nSources kept as <key>.migrated. Delete them once you are satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
