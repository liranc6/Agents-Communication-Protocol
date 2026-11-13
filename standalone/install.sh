#!/bin/bash
# Standalone COP install into ~/.claude (macOS/Linux; needs bash and python3). Safe to re-run.
# Plugin users do not need this: see README.
set -euo pipefail
: "${HOME:?HOME is not set}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
C="$HOME/.claude"
BEGIN="<!-- COP:begin -->"
END="<!-- COP:end -->"
MARK=".cop-managed"
HOOKCMD='[ -f "$HOME/.claude/cop/peer_hook.py" ] && python3 "$HOME/.claude/cop/peer_hook.py" || true'
TS="$(date +%Y%m%d-%H%M%S)"

# 0) preflight: change nothing unless everything below can succeed
for d in "$C/cop" "$C/skills/cop"; do
  if [ -e "$d" ] && [ ! -e "$d/$MARK" ]; then
    echo "error: $d already exists and was not installed by COP; move it away first" >&2; exit 1
  fi
done
python3 - "$C/settings.json" <<'PY'
import json, os, sys
p = sys.argv[1]
if not os.path.exists(p): sys.exit(0)
try:
    s = json.load(open(p, encoding="utf-8"))
    assert isinstance(s, dict)
    h = s.get("hooks")
    assert h is None or isinstance(h, dict)
    pre = (h or {}).get("PreToolUse")
    assert pre is None or isinstance(pre, list)
    for e in pre or []:
        assert isinstance(e, dict) and isinstance(e.get("hooks", []), list)
        assert all(isinstance(x, dict) for x in e.get("hooks", []))
except Exception:
    sys.exit(f"error: {p} is not valid settings JSON (or hooks.PreToolUse has an unexpected shape); fix it first")
PY

# 1) files
mkdir -p "$C/cop" "$C/skills/cop/reference"
cp "$ROOT/hooks/peer.txt" "$ROOT/hooks/peer_hook.py" "$ROOT/tools/cop_stats.py" "$C/cop/"
cp "$ROOT/skills/cop/SKILL.md" "$C/skills/cop/SKILL.md"
cp "$ROOT/skills/cop/reference/COP.md" "$C/skills/cop/reference/COP.md"
touch "$C/cop/$MARK" "$C/skills/cop/$MARK"

# 2) always-on rules, between markers (uninstall removes exactly this block)
touch "$C/CLAUDE.md"
if grep -q "^$BEGIN" "$C/CLAUDE.md"; then
  echo "CLAUDE.md already has the COP block, skipping"
elif grep -q "^# COP (machine-only" "$C/CLAUDE.md"; then
  echo "CLAUDE.md has an unmarked COP block; leaving it alone (remove it by hand to re-install)"
else
  cp "$C/CLAUDE.md" "$C/CLAUDE.md.bak-cop-$TS"
  {
    echo; echo "$BEGIN"; cat "$ROOT/standalone/COP-rules.md"
    echo "COP files: ref=$C/skills/cop/reference/COP.md peer=$C/cop/peer.txt stats=$C/cop/cop_stats.py"
    echo "$END"
  } >> "$C/CLAUDE.md"
  echo "appended COP block to $C/CLAUDE.md (backup: CLAUDE.md.bak-cop-$TS)"
fi

# 3) subagent hook
python3 - "$C/settings.json" "$HOOKCMD" "$TS" <<'PY'
import json, os, shutil, sys
p, cmd, ts = sys.argv[1:4]
raw = open(p, encoding="utf-8", newline="").read() if os.path.exists(p) else ""
s = json.loads(raw) if raw.strip() else {}
h = s.get("hooks") or {}
pre = h.get("PreToolUse") or []
if any(".claude/cop/peer_hook.py" in x.get("command", "") for e in pre for x in e.get("hooks", [])):
    print("hook already registered"); sys.exit(0)
if raw:
    shutil.copy(p, f"{p}.bak-cop-{ts}")
pre.append({"matcher": "Agent|Task", "hooks": [{"type": "command", "command": cmd}]})
h["PreToolUse"] = pre
s["hooks"] = h
with open(p, "w", encoding="utf-8") as f:
    f.write(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
print("hook registered in", p)
PY
echo "Done. Restart your agent session, then try: /cop"
