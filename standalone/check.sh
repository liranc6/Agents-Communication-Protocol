#!/bin/bash
# Checks that the standalone install in ~/.claude is complete and working. Read-only; changes nothing.
# Exit 0 if every check passes, 1 otherwise.
: "${HOME:?HOME is not set}"
C="$HOME/.claude"
BAD=0
ok()   { echo "PASS  $1"; }
no()   { echo "FAIL  $1"; BAD=1; }

for f in cop/peer.txt cop/peer_hook.py cop/cop_stats.py skills/cop/SKILL.md skills/cop/reference/COP.md; do
  if [ -f "$C/$f" ]; then ok "file ~/.claude/$f"; else no "file ~/.claude/$f missing (run standalone/install.sh)"; fi
done

n=$(grep -c "^<!-- COP:begin -->" "$C/CLAUDE.md" 2>/dev/null); n=${n:-0}
e=$(grep -c "^<!-- COP:end -->" "$C/CLAUDE.md" 2>/dev/null); e=${e:-0}
if [ "$n" = 1 ] && [ "$e" = 1 ]; then ok "CLAUDE.md has one COP block"
elif [ "$n" = 0 ]; then no "CLAUDE.md has no COP block"
else no "CLAUDE.md has $n begin / $e end markers (expected 1 / 1)"; fi

if python3 - "$C/settings.json" <<'PY'
import json, sys
try:
    s = json.load(open(sys.argv[1], encoding="utf-8"))
    pre = s["hooks"]["PreToolUse"]
    n = sum(1 for e in pre for x in e.get("hooks", [])
            if ".claude/cop/peer_hook.py" in x.get("command", "") and "Agent" in str(e.get("matcher", "")))
    sys.exit(0 if n == 1 else 1)
except Exception:
    sys.exit(1)
PY
then ok "settings.json registers the subagent hook once"
else no "settings.json does not register the subagent hook exactly once"; fi

if [ -f "$C/cop/peer_hook.py" ] \
   && echo '{"tool_input":{"prompt":"hi"}}' | python3 "$C/cop/peer_hook.py" 2>/dev/null | grep -q "COP:"; then
  ok "hook adds the COP block to a subagent prompt"
else no "hook did not add the COP block"; fi

if [ "$BAD" = 0 ]; then
  echo "All checks passed."
  echo "Next: open a NEW local Claude Code session (terminal 'claude', or a local session in the desktop app) and type /cop."
  echo "Sessions open during install, chat, and cloud sessions do not read ~/.claude."
else
  echo "Some checks failed."; exit 1
fi
