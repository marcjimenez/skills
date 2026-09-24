#!/usr/bin/env python3
"""Merge path-keyed cache directories into repository-keyed ones.

REPO_KEY used to hash the checkout path, so every git worktree and every Conductor workspace of the
same repository got its own cache: its own integration_test recipe, its own code_review waivers, its
own runs. This folds them back together under the key the current derivation produces.

Dry run by default. Pass --apply to move anything.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "marcjimenez"
REPOS = CONFIG_HOME / "repos"
# Where checkouts live. A stored key can only be resolved directly if its checkout still exists.
SEARCH = [Path.home() / "conductor" / "repos", Path.home() / "conductor" / "workspaces"]


def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def key_from_remote(checkout):
    url = run(["git", "config", "--get", "remote.origin.url"], cwd=checkout)
    if not url:
        return ""
    return re.sub(r"[/ ]", "-", re.sub(r"\.git$", "", re.sub(r"^(https?://[^/]+/|git@[^:]+:|ssh://[^/]+/)", "", url)))


def legacy_key(path):
    """The old derivation: basename plus 8 chars of sha1 of the checkout path."""
    p = str(path)
    return f"{Path(p).name}-{hashlib.sha1(p.encode()).hexdigest()[:8]}"


def live_checkouts():
    for root in SEARCH:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if (d / ".git").exists():
                yield d
            elif d.is_dir():
                for sub in sorted(d.iterdir()):
                    if (sub / ".git").exists():
                        yield sub


def recipe_fingerprint(cfg_path):
    """Identical integration_test recipes mean the same repository, re-derived."""
    try:
        recipe = json.loads(cfg_path.read_text()).get("integration_test")
    except Exception:
        return ""
    if not recipe:
        return ""
    return hashlib.sha1(json.dumps(recipe, sort_keys=True).encode()).hexdigest()[:10]


def merge_config(dst_path, src_path, log):
    """Newest file wins per section; waivers are unioned so no accepted divergence is lost."""
    dst = json.loads(dst_path.read_text()) if dst_path.exists() else {}
    src = json.loads(src_path.read_text())
    src_newer = not dst_path.exists() or src_path.stat().st_mtime > dst_path.stat().st_mtime

    seen, waivers = set(), []
    for cfg in (dst, src):
        for w in cfg.get("code_review", {}).get("waivers", []):
            ident = (w.get("area"), w.get("divergence"))
            if ident not in seen:
                seen.add(ident)
                waivers.append(w)

    for section, value in src.items():
        if section not in dst:
            dst[section] = value
        elif dst[section] != value and src_newer:
            log.append(f"      overwrote {section} with the newer copy")
            dst[section] = value
    if waivers:
        dst.setdefault("code_review", {})["waivers"] = waivers
    return dst, len(waivers)


def cited_slugs(d):
    """owner/repo slugs mentioned in this directory's run artifacts, by citation count."""
    urls = {}
    for f in d.rglob("*.md"):
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r"github\.com[/:]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", text):
            slug = re.sub(r"\.git$", "", m.group(1))
            urls[slug] = urls.get(slug, 0) + 1
    return urls


def guess_repo(d, known_repos):
    """Most-cited GitHub repo in this directory's artifacts. A hint only, never applied.

    It is wrong often enough to matter: a run that troubleshoots a dependency cites the dependency,
    and a run in one repo that references a sibling can cite the sibling more than its own. So flag
    the case we CAN detect, where the directory is named after a repo that exists and the citations
    point somewhere else.
    """
    urls = cited_slugs(d)
    if not urls:
        return "", ""
    slug, count = max(urls.items(), key=lambda kv: kv[1])
    key = slug.replace("/", "-")
    note = f"  ({count} citation{'s' if count > 1 else ''})"
    stem = re.sub(r"-[0-9a-f]{8}$", "", d.name)
    if stem in known_repos and not key.endswith("-" + stem):
        note += f"  ** but this directory is named '{stem}', which is itself a repo **"
    return key, note


def main():
    apply = "--apply" in sys.argv
    manual = dict(
        a.split("=", 1)
        for a in sys.argv[1:]
        if a.startswith("--map") is False and "=" in a
    )
    for i, a in enumerate(sys.argv):
        if a == "--map" and i + 1 < len(sys.argv) and "=" in sys.argv[i + 1]:
            k, v = sys.argv[i + 1].split("=", 1)
            manual[k] = v
    if not REPOS.is_dir():
        sys.exit(f"nothing to migrate: {REPOS} does not exist")

    stored = [d for d in sorted(REPOS.iterdir()) if d.is_dir() and not d.name.endswith(".migrated")]

    # Pass 1: a stored key whose checkout still exists resolves directly through that checkout's remote.
    resolved, by_fingerprint = {}, {}
    for checkout in live_checkouts():
        k = legacy_key(checkout)
        d = REPOS / k
        if d.is_dir():
            new = key_from_remote(checkout)
            if new:
                resolved[k] = new
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

    # Pass 3: whatever the operator mapped by hand on the command line.
    for k, v in manual.items():
        if (REPOS / k).is_dir():
            resolved[k] = v
        else:
            print(f"  --map {k}={v}: no such directory, ignored\n")

    unresolved = [d for d in stored if d.name not in resolved and d.name not in resolved.values()]

    print(f"{'APPLYING' if apply else 'DRY RUN'} — {REPOS}\n")
    groups = {}
    for old, new in sorted(resolved.items()):
        groups.setdefault(new, []).append(old)

    for new, olds in sorted(groups.items()):
        print(f"  {new}")
        for old in olds:
            src = REPOS / old
            runs = sorted(p.name for p in (src / "runs").iterdir()) if (src / "runs").is_dir() else []
            print(f"    <- {old:<44} {len(runs)} run(s)")
        print()

    # Repo names we have real evidence for: resolved keys plus every slug cited anywhere.
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
            try:
                keys = ", ".join(json.loads((d / "config.json").read_text()).keys())
            except Exception:
                keys = "no config"
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
            guess, note = guess_repo(d, known_repos)
            print(f"    {d.name:<46} {size // 1024:>5} KB  [{keys}]")
            if guess:
                print(f"    {'':<46} guess: {guess}{note}")
        print()

    if not apply:
        print("Nothing changed. Re-run with --apply to move.")
        return

    for new, olds in sorted(groups.items()):
        dst = REPOS / new
        dst.mkdir(parents=True, exist_ok=True)
        log = []
        for old in olds:
            src = REPOS / old
            if src == dst:
                continue
            if (src / "config.json").exists():
                merged, n = merge_config(dst / "config.json", src / "config.json", log)
                (dst / "config.json").write_text(json.dumps(merged, indent=2) + "\n")
            for sub in sorted((src / "runs").iterdir()) if (src / "runs").is_dir() else []:
                target = dst / "runs" / sub.name
                if target.exists():
                    # Keep both rather than lose one; the suffix says where it came from.
                    target = dst / "runs" / f"{sub.name}--{old}"
                    log.append(f"      run slug {sub.name} collided, kept as {target.name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(sub), str(target))
            for extra in ("utilities.md",):
                if (src / extra).exists() and not (dst / extra).exists():
                    shutil.move(str(src / extra), str(dst / extra))
            # Renamed, never deleted, so a bad merge is reversible.
            shutil.move(str(src), str(src.with_name(src.name + ".migrated")))
        waivers = len(json.loads((dst / "config.json").read_text()).get("code_review", {}).get("waivers", [])) if (dst / "config.json").exists() else 0
        runs = len(list((dst / "runs").iterdir())) if (dst / "runs").is_dir() else 0
        print(f"  {new}: {runs} run(s), {waivers} waiver(s)")
        for line in log:
            print(line)

    print("\nSources kept as <key>.migrated. Delete them once you are satisfied.")


if __name__ == "__main__":
    main()
