#!/usr/bin/env python3
"""PreToolUse hook (Agent|Task): append the COP PEER block to subagent prompts.

Fail-open: on any problem (bad input, missing peer.txt) print nothing and exit 0,
so the original prompt goes through unchanged and the hook never blocks a subagent call.

Skipped when the prompt already has a line starting with "COP:", contains "cop:off",
or the subagent_type is listed in COP_SKIP_SUBAGENTS (comma separated).
Use these opt-outs for subagents that must return a fixed or structured format.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
PEER_FILE = os.environ.get("COP_PEER_FILE") or os.path.join(HERE, "peer.txt")
TAGGED = re.compile(r"(?m)^COP:")
HAS_LIMIT = re.compile(r"reply\s*<=\s*\d+", re.I)


def skipped_types():
    return {t.strip() for t in os.environ.get("COP_SKIP_SUBAGENTS", "").split(",") if t.strip()}


def build(data):
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        return None
    p = ti.get("prompt")
    if not isinstance(p, str) or TAGGED.search(p) or "cop:off" in p.lower():
        return None
    if ti.get("subagent_type") in skipped_types():
        return None
    with open(PEER_FILE, encoding="utf-8") as f:
        peer = f.read().strip()
    if not peer:
        return None
    n = "" if HAS_LIMIT.search(p) else " N=15 unless task needs more."
    ti = dict(ti, prompt=f"{p}\n\n{peer}{n}")
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "updatedInput": ti}}


def main():
    try:
        out = build(json.load(sys.stdin))
        if out:
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()
    except BaseException:
        try:  # e.g. closed pipe: avoid a second error when the interpreter flushes stdout at exit
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
