#!/usr/bin/env python3
"""Reduce local Claude Code transcripts to a compact digest for the skill audit.

The transcripts are ~2 GB, so everything mechanical happens here and the model only ever reads the
digest. Deterministic and read-only: it opens nothing but the JSONL files and prints JSON.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

# A user message that pushes back on what just happened. Deliberately broad: the audit reads the hits
# rather than trusting the count, so a false positive costs a glance and a miss costs a finding.
CORRECTION = re.compile(
    r"(?:^\s*(?:no\b|nope|stop\b|wait\b|revert\b|undo\b))"
    r"|\byou (?:missed|forgot|skipped|didn'?t|broke|shouldn'?t have)\b"
    r"|\b(?:that'?s|this is) (?:wrong|not right|incorrect)\b"
    r"|\bnot what i (?:asked|wanted|said|meant)\b"
    r"|\bi (?:said|asked for|told you)\b"
    r"|\bwhy did you\b"
    r"|\b(?:don'?t|do not|never) (?:use|do|add|create|write|make|change|remove|delete|touch|"
    r"commit|push|run|put|include|start|open|edit|rename)\b", re.I)

PUSH = re.compile(r"\b(git push|gh pr create)\b")


def iter_records(path):
    try:
        with open(path, errors="ignore") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except OSError:
        return


def text_of(message):
    """Transcript content is sometimes a string, sometimes a list of typed blocks."""
    if isinstance(message, str):
        return message
    if isinstance(message, list):
        return " ".join(b.get("text", "") for b in message if isinstance(b, dict))
    return ""


def scan(path):
    """One pass per transcript. Returns the facts; all judgement is left to the caller."""
    out = {
        "skills": collections.Counter(),
        "tools": collections.Counter(),
        "corrections": [],
        "user_msgs": 0,
        "unslop_reminders": 0,
        "pushed": False,
        "reviewed": False,
        "bash_errors": collections.Counter(),
    }
    last_skill = None
    for d in iter_records(path):
        kind = d.get("type")
        if kind == "assistant":
            for block in (d.get("message") or {}).get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                args = block.get("input") or {}
                out["tools"][name] += 1
                if name == "Skill":
                    slug = args.get("skill", "?")
                    out["skills"][slug] += 1
                    last_skill = slug
                    if slug.endswith("code-review"):
                        out["reviewed"] = True
                # The review is often dispatched as subagents rather than invoked as a skill, and a
                # gate check that ignores that reports every careful session as a violation.
                if name in ("Agent", "Task") and re.search(
                        r"code[- ]review|reviewing this (?:diff|change)|unit audit",
                        str(args.get("prompt", "")) + str(args.get("description", "")), re.I):
                    out["reviewed"] = True
                if name == "Bash":
                    cmd = str(args.get("command", ""))
                    if PUSH.search(cmd):
                        out["pushed"] = True
        elif kind == "attachment":
            # Hook output arrives as an attachment, not as part of the user message.
            if "unslop skill is mandatory" in json.dumps(d):
                out["unslop_reminders"] += 1
        elif kind == "user":
            body = text_of((d.get("message") or {}).get("content"))
            if not body:
                continue
            if body.startswith("<") or body.startswith("["):
                continue
            out["user_msgs"] += 1
            head = body[:300].replace("\n", " ").strip()
            if CORRECTION.search(head):
                out["corrections"].append({"after_skill": last_skill, "text": head[:200]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=24, help="window to report on (default 24)")
    ap.add_argument("--baseline-days", type=float, default=30,
                    help="wider window used only to decide which skills are going unused")
    ap.add_argument("--max-corrections", type=int, default=25,
                    help="cap the quoted corrections so the digest stays small")
    args = ap.parse_args()

    if not PROJECTS.is_dir():
        sys.exit(f"no transcripts at {PROJECTS}")

    now = time.time()
    window_cut = now - args.hours * 3600
    baseline_cut = now - args.baseline_days * 86400

    window, baseline = [], []
    for f in glob.glob(str(PROJECTS / "*" / "*.jsonl")):
        try:
            mtime = os.path.getmtime(f)
        except OSError:
            continue
        if mtime > baseline_cut:
            baseline.append(f)
        if mtime > window_cut:
            window.append(f)

    agg = {
        "skills": collections.Counter(), "tools": collections.Counter(),
        "corrections": [],
        "user_msgs": 0, "unslop_reminders": 0,
    }
    ungated = []
    for f in window:
        s = scan(f)
        for key in ("skills", "tools"):
            agg[key].update(s[key])
        agg["corrections"].extend(s["corrections"])
        agg["user_msgs"] += s["user_msgs"]
        agg["unslop_reminders"] += s["unslop_reminders"]
        # Pushed without the review gate is the one compliance check worth making mechanical.
        if s["pushed"] and not s["reviewed"]:
            ungated.append(Path(f).parent.name)

    baseline_skills = collections.Counter()
    for f in baseline:
        baseline_skills.update(scan(f)["skills"])

    installed = sorted(
        p.name for p in (Path(__file__).resolve().parent.parent /
                         "plugins/marcjimenez/skills").iterdir() if p.is_dir())
    unused = [s for s in installed
              if not baseline_skills.get(f"marcjimenez:{s}")]

    # A resumed conversation is written to several transcript files, so the same message repeats.
    seen, corrections = set(), []
    for c in agg["corrections"]:
        if c["text"] not in seen:
            seen.add(c["text"])
            corrections.append(c)
    unique_total = len(corrections)
    corrections = corrections[:args.max_corrections]
    print(json.dumps({
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "window_hours": args.hours,
        "sessions_in_window": len(window),
        "user_messages": agg["user_msgs"],
        "corrections_total": unique_total,
        "corrections_sampled": corrections,
        "skills_in_window": dict(agg["skills"].most_common()),
        "skills_in_baseline": {k: v for k, v in baseline_skills.most_common()
                               if k.startswith("marcjimenez:")},
        "unused_over_baseline": unused,
        "baseline_days": args.baseline_days,
        "unslop_reminders": agg["unslop_reminders"],
        "unslop_invocations": agg["skills"].get("marcjimenez:unslop", 0),
        "top_tools": dict(agg["tools"].most_common(10)),
        "pushed_without_review": sorted(set(ungated)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
