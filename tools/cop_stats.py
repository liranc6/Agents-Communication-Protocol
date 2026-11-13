#!/usr/bin/env python3
"""Per-session token breakdown from Claude Code transcripts, to measure COP impact.

Usage:
  python3 cop_stats.py                              # last 15 sessions, all projects
  python3 cop_stats.py -p myproject -n 30           # project dir name contains "myproject"
  python3 cop_stats.py --split "2026-09-29 00:00" --main   # before/after averages (UTC)

--split takes "YYYY-MM-DD" or "YYYY-MM-DD HH:MM" (UTC; compared as a string against session start).
Reads Claude Code's local transcript files (~/.claude/projects, override with COP_PROJECTS_DIR).
The transcript format is not a documented API, so unrecognised lines are skipped.
"""
import argparse
import glob
import json
import os
import re
import sys
import statistics
from collections import Counter

ROOT = os.environ.get("COP_PROJECTS_DIR") or os.path.expanduser("~/.claude/projects")


def text_len(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(b["text"]) if isinstance(b, dict) and isinstance(b.get("text"), str) else
                   (len(b) if isinstance(b, str) else 0) for b in content)
    return 0


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def parse(path):
    s = dict(path=path, kind="sub" if "/subagents/" in path else "main", start=None, reqs=0, out=0, think=0, ctx=0,
             tool_chars=0, bad_lines=0)
    seen, tool_names, per_tool = set(), {}, Counter()
    with open(path, errors="ignore") as f:
        for lineno, line in enumerate(f):
            try:
                d = json.loads(line)
            except ValueError:
                s["bad_lines"] += 1
                continue
            if not isinstance(d, dict):
                s["bad_lines"] += 1
                continue
            ts = d.get("timestamp")
            if isinstance(ts, str) and ts and not s["start"]:
                s["start"] = ts[:16].replace("T", " ")
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            content = m.get("content") if isinstance(m.get("content"), list) else []
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    tool_names[b.get("id")] = b.get("name")
                elif b.get("type") == "tool_result":
                    n = text_len(b.get("content"))
                    s["tool_chars"] += n
                    per_tool[tool_names.get(b.get("tool_use_id"), "?")] += n
            u = m.get("usage")
            rid = d.get("requestId")
            if not isinstance(rid, str) or not rid:
                rid = f"line{lineno}"
            if d.get("type") == "assistant" and isinstance(u, dict) and u and rid not in seen:
                seen.add(rid)
                det = u.get("output_tokens_details")
                s["reqs"] += 1
                s["out"] += num(u.get("output_tokens"))
                s["think"] += num(det.get("thinking_tokens")) if isinstance(det, dict) else 0
                s["ctx"] += (num(u.get("input_tokens")) + num(u.get("cache_read_input_tokens"))
                             + num(u.get("cache_creation_input_tokens")))
    s["visible"] = s["out"] - s["think"]
    s["tool_tok"] = int(s["tool_chars"] // 4)  # rough: ~4 chars/token
    s["top_tool"] = ",".join(f"{k}:{int(v // 4000)}k" for k, v in per_tool.most_common(2))
    return s


def row(s):
    r = max(s["reqs"], 1)
    return (f"{s['start'] or '?':16} {s['kind']:4} {s['reqs']:5} {s['out']:8} {s['think']:8} {s['visible']:8} "
            f"{s['tool_tok']:8} {s['ctx'] // r:8}  {s['top_tool']}")


def summary(label, ss):
    if not ss:
        print(f"{label}: no sessions")
        return
    avg = lambda k: statistics.mean(x[k] / max(x["reqs"], 1) for x in ss)
    print(f"{label:6} n={len(ss):3}  per request: out={avg('out'):.0f} think={avg('think'):.0f} "
          f"visible={avg('visible'):.0f} tool_tok={avg('tool_tok'):.0f} ctx={avg('ctx'):.0f}")


def split_arg(v):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?", v):
        raise argparse.ArgumentTypeError('expected "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"')
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--project", default="", help="substring of project dir name")
    ap.add_argument("-n", type=int, default=15, help="sessions to list")
    ap.add_argument("--split", type=split_arg, help="\"YYYY-MM-DD[ HH:MM]\" UTC: compare sessions before vs on/after")
    ap.add_argument("--min-reqs", type=int, default=3, help="skip tiny sessions")
    ap.add_argument("--main", action="store_true", help="exclude subagent transcripts")
    a = ap.parse_args()

    files = set(glob.glob(f"{ROOT}/*{a.project}*/**/*.jsonl", recursive=True))
    parsed, skipped = [], 0
    for f in sorted(files):
        try:
            parsed.append(parse(f))
        except Exception:
            skipped += 1
    bad = sum(x["bad_lines"] for x in parsed)
    if skipped:
        print(f"skipped {skipped} unreadable files", file=sys.stderr)
    if bad:
        print(f"skipped {bad} malformed lines", file=sys.stderr)
    ss = [s for s in parsed if s["reqs"] >= a.min_reqs and s["start"]
          and not (a.main and s["kind"] == "sub")]
    ss.sort(key=lambda s: s["start"])

    if a.split:
        summary("before", [s for s in ss if s["start"] < a.split])
        summary("after", [s for s in ss if s["start"] >= a.split])
        return
    print(f"{'start':16} kind {'reqs':>5} {'out':>8} {'think':>8} {'visible':>8} {'tool_tok':>8} {'ctx/req':>8}  top tools")
    for s in ss[-a.n:]:
        print(row(s))


if __name__ == "__main__":
    main()
