#!/bin/bash
# Removes what standalone/install.sh added. Leaves your other CLAUDE.md and settings.json content alone.
set -euo pipefail
: "${HOME:?HOME is not set}"
C="$HOME/.claude"
MARK=".cop-managed"

# settings first: files are removed only after no hook points at them
python3 - "$C/CLAUDE.md" "$C/settings.json" <<'PY'
import json, os, re, sys
md, st = sys.argv[1:3]
if os.path.exists(st):
    raw = open(st, encoding="utf-8", newline="").read()
    try:
        s = json.loads(raw)
        h0 = s.get("hooks")
        pre = h0.get("PreToolUse") if isinstance(h0, dict) else None
        if isinstance(pre, list):
            for e in pre:
                assert isinstance(e, dict) and all(isinstance(x, dict) for x in e.get("hooks", []))
    except Exception:
        sys.exit("error: " + st + " is not valid settings JSON or has an unexpected hooks shape; nothing changed")
    if isinstance(pre, list):
        before = json.dumps(pre, sort_keys=True)
        keep = []
        for e in pre:
            hs = e.get("hooks", [])
            kept = [h for h in hs if ".claude/cop/peer_hook.py" not in h.get("command", "")]
            if len(kept) != len(hs):
                e["hooks"] = kept
            if kept or len(kept) == len(hs):
                keep.append(e)
        if json.dumps(keep, sort_keys=True) != before:
            if keep:
                s["hooks"]["PreToolUse"] = keep
            else:
                s["hooks"].pop("PreToolUse")
                if not s["hooks"]:
                    s.pop("hooks")
            with open(st, "w", encoding="utf-8") as f:
                f.write(json.dumps(s, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") or not raw else ""))
            print("removed hook from", st)
    if ".claude/cop/peer_hook.py" in open(st, encoding="utf-8").read():
        sys.exit("error: a hook still references .claude/cop/peer_hook.py in " + st + "; remove it by hand, nothing deleted")
if os.path.exists(md):
    t = open(md, encoding="utf-8", newline="").read()
    n = re.sub(r"\n<!-- COP:begin -->\r?\n.*?\n<!-- COP:end -->\r?\n?", "", t, flags=re.S)
    if n == t:
        n = re.sub(r"^<!-- COP:begin -->\r?\n.*?\n<!-- COP:end -->\r?\n?", "", t, flags=re.S)
    if n != t:
        with open(md, "w", encoding="utf-8", newline="") as f:
            f.write(n)
        print("removed COP block from", md)
PY
for d in "$C/cop" "$C/skills/cop"; do
  if [ -e "$d/$MARK" ]; then rm -rf "$d"; elif [ -e "$d" ]; then echo "left $d alone (not installed by COP)"; fi
done
echo "Uninstalled. Backups (*.bak-cop-*) were left in place; delete them if you no longer need them."
