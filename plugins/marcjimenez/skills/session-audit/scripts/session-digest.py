#!/usr/bin/env python3
"""Reduce local Claude Code transcripts to a compact digest for the skill audit.

The transcripts run to gigabytes, so everything mechanical happens here and the model reads only the
digest. Deterministic and read-only: it opens nothing but the JSONL files and prints JSON.
"""
import argparse
import collections
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

# A user message that pushes back on what just happened. Tuned for recall: the audit reads every hit and
# judges it, so a false positive costs a glance while a miss costs a finding entirely.
CORRECTION = re.compile(
    r"(?:^\s*(?:no\b|nope|stop\b|revert\b|undo\b))"
    r"|^\s*(?:try again|redo|rewrite|do (?:it )?again)\b"
    r"|\byou (?:missed|forgot|skipped|didn'?t|broke|shouldn'?t have)\b"
    r"|\b(?:that|this|it) (?:doesn'?t|does not) (?:feel|look|seem) right\b"
    r"|\b(?:that'?s|this is) (?:wrong|not right|incorrect)\b"
    r"|\bnot what i (?:asked|wanted|said|meant)\b"
    r"|\bi (?:said|asked for|told you)\b"
    r"|\bi don'?t (?:think|want|like)\b"
    r"|\bwhy did you\b"
    r"|\btake a step back\b"
    r"|\b(?:don'?t|do not|never) (?:use|do|add|create|write|make|change|remove|delete|touch|"
    r"commit|push|run|put|include|start|open|edit|rename)\b", re.I)

# Pasted logs, alerts and code trip the detector on their first word. Their opening line gives them away.
PASTED = re.compile(r"^\s*(?:[#/{]|:[a-z_]+:|\[\d{1,2}:\d{2})")

SLASH = re.compile(r"<command-name>\s*/?([\w.-]+:[\w-]+)\s*</command-name>")
INTERRUPT = "[Request interrupted by user"
SKILL_LOAD = "Base directory for this skill:"
PUSH = re.compile(r"\b(git push|gh pr create)\b")
# A review is usually dispatched as subagents rather than invoked as a skill; a gate check that ignores
# that reports every careful session as a violation.
REVIEW_AGENT = re.compile(r"code[- ]review|reviewing this (?:diff|change)|unit audit", re.I)


def positive(kind, allow_zero=False):
    def check(raw):
        v = kind(raw)
        if v < 0 or (v == 0 and not allow_zero):
            raise argparse.ArgumentTypeError(f"must be > 0, got {raw}")
        return v
    return check


def iter_records(path):
    try:
        with path.open(errors="ignore") as fh:
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


def record_id(rec, line_no, path):
    """A resumed conversation is rewritten into a new file carrying the original records and uuids, so
    over half of all records appear more than once. Everything is counted by identity, not by line."""
    uid = rec.get("uuid")
    if uid:
        return uid
    return hashlib.sha1(f"{path.name}:{line_no}:{rec.get('type')}".encode()).hexdigest()


def when(rec, fallback):
    ts = rec.get("timestamp")
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return fallback


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=positive(float), default=24, help="window to report on (default 24)")
    ap.add_argument("--baseline-days", type=positive(float), default=30,
                    help="wider window used only to decide which skills are going unused")
    ap.add_argument("--max-corrections", type=positive(int, allow_zero=True), default=25,
                    help="cap the quoted corrections so the digest stays small")
    args = ap.parse_args()

    if not PROJECTS.is_dir():
        sys.exit(f"no transcripts at {PROJECTS}")

    now = time.time()
    window_cut = now - args.hours * 3600
    baseline_cut = now - args.baseline_days * 86400

    seen = set()
    win = {"skills": collections.Counter(), "tools": collections.Counter(), "corrections": [],
           "users": 0, "reminders": 0, "interrupts": 0}
    base_skills = collections.Counter()
    # The gate is a property of a conversation, not of a file: a review in one file and the push in its
    # resumed continuation is still a reviewed session.
    sessions = collections.defaultdict(lambda: {"pushed": False, "reviewed": False})
    window_files = 0

    for path in PROJECTS.glob("*/*.jsonl"):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime < baseline_cut:
            continue
        touched_window = False
        last_skill = None

        for line_no, rec in enumerate(iter_records(path)):
            rid = record_id(rec, line_no, path)
            if rid in seen:
                continue
            seen.add(rid)

            in_window = when(rec, mtime) >= window_cut
            touched_window |= in_window
            sid = rec.get("sessionId") or path.stem
            kind = rec.get("type")
            msg = rec.get("message")
            msg = msg if isinstance(msg, dict) else {}

            if kind == "assistant":
                for block in msg.get("content") or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name, a = block.get("name"), block.get("input") or {}
                    if in_window:
                        win["tools"][name] += 1
                    if name == "Skill":
                        slug = a.get("skill", "?")
                        base_skills[slug] += 1
                        last_skill = slug
                        if in_window:
                            win["skills"][slug] += 1
                        if slug == "marcjimenez:code-review":
                            sessions[sid]["reviewed"] = True
                    # Only a push inside the window is this digest's business, but a review anywhere in
                    # the conversation gates it, including before the window opened.
                    elif name == "Bash" and in_window and PUSH.search(str(a.get("command", ""))):
                        sessions[sid]["pushed"] = True
                    elif name in ("Agent", "Task") and REVIEW_AGENT.search(
                            f"{a.get('prompt', '')} {a.get('description', '')}"):
                        sessions[sid]["reviewed"] = True

            elif kind == "attachment" and in_window:
                # Hook output arrives as an attachment, not as part of the user message.
                if "unslop skill is mandatory" in str(rec.get("content") or rec.get("text") or rec):
                    win["reminders"] += 1

            elif kind == "user":
                body = text_of(msg.get("content"))
                if not body:
                    continue
                # A typed slash command is a real invocation and arrives here, not as a Skill tool call.
                m = SLASH.search(body)
                if m:
                    base_skills[m.group(1)] += 1
                    last_skill = m.group(1)
                    if in_window:
                        win["skills"][m.group(1)] += 1
                    continue
                if body.startswith(INTERRUPT):
                    if in_window:
                        win["interrupts"] += 1
                    continue
                if body.startswith("<") or body.startswith("[") or body.startswith(SKILL_LOAD):
                    continue
                if not in_window:
                    continue
                win["users"] += 1
                head = body[:300].replace("\n", " ").strip()
                if not PASTED.match(body) and CORRECTION.search(head):
                    win["corrections"].append({"after_skill": last_skill, "text": head[:200]})

        if touched_window:
            window_files += 1

    installed = sorted(p.name for p in (Path(__file__).resolve().parents[1]).parent.iterdir()
                       if p.is_dir() and (p / "SKILL.md").exists())
    unused = [s for s in installed if not base_skills.get(f"marcjimenez:{s}")]

    corrections = list({c["text"]: c for c in win["corrections"]}.values())
    print(json.dumps({
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "window_hours": args.hours,
        "sessions_in_window": window_files,
        "user_messages": win["users"],
        "interrupts": win["interrupts"],
        "corrections_total": len(corrections),
        "corrections_sampled": corrections[:args.max_corrections],
        "skills_in_window": dict(win["skills"].most_common()),
        "skills_in_baseline": {k: v for k, v in base_skills.most_common()
                               if k.startswith("marcjimenez:")},
        "unused_over_baseline": unused,
        "baseline_days": args.baseline_days,
        "unslop_reminders": win["reminders"],
        "unslop_invocations": win["skills"].get("marcjimenez:unslop", 0),
        "top_tools": dict(win["tools"].most_common(10)),
        "pushed_without_review": sorted(
            sid for sid, s in sessions.items() if s["pushed"] and not s["reviewed"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
