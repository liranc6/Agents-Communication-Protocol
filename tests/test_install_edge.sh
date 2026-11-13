#!/bin/bash
# Edge cases for standalone install/uninstall, run against a throwaway HOME.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T"; C="$T/.claude"
fail() { echo "FAIL: $*"; exit 1; }
reset() { rm -rf "$C"; mkdir -p "$C"; }
inst() { bash "$ROOT/standalone/install.sh" >"$T/out" 2>&1; }
uninst() { bash "$ROOT/standalone/uninstall.sh" >"$T/out" 2>&1; }

# a user-owned skills/cop is never overwritten or deleted
reset; mkdir -p "$C/skills/cop"; echo mine > "$C/skills/cop/SKILL.md"
uninst; [ "$(cat "$C/skills/cop/SKILL.md")" = mine ] || fail "uninstall deleted user skill"
inst && fail "install accepted a user-owned skills/cop"
[ "$(cat "$C/skills/cop/SKILL.md")" = mine ] || fail "install clobbered user skill"
[ ! -e "$C/CLAUDE.md" ] && [ ! -e "$C/cop" ] || fail "install changed things before aborting"

# invalid settings.json: abort before any write
reset; echo '{bad' > "$C/settings.json"; printf 'x\n' > "$C/CLAUDE.md"
inst && fail "accepted malformed settings"
[ "$(cat "$C/CLAUDE.md")" = x ] && [ ! -e "$C/cop" ] || fail "partial install on bad settings"
for bad in '{"hooks":{"PreToolUse":{}}}' '[1]'; do
  reset; echo "$bad" > "$C/settings.json"
  inst && fail "accepted $bad"; [ ! -e "$C/cop" ] || fail "partial install for $bad"
done
reset; echo '{"hooks":null}' > "$C/settings.json"; inst || fail "hooks:null should install"

# the COP hook sharing an entry with another hook is removed; the other stays
reset
echo '{"hooks":{"PreToolUse":[{"matcher":"Agent|Task","hooks":[{"type":"command","command":"echo other"},{"type":"command","command":"python3 ~/.claude/cop/peer_hook.py"}]}]}}' > "$C/settings.json"
inst; uninst
grep -q "peer_hook" "$C/settings.json" && fail "orphaned hook left in settings"
grep -q "echo other" "$C/settings.json" || fail "other hook lost"
[ ! -e "$C/cop" ] || fail "files left"

# a hook that cannot be removed makes uninstall refuse and delete nothing
reset; inst
python3 - "$C/settings.json" <<'EOF'
import json, sys
p = sys.argv[1]; s = json.load(open(p))
s["hooks"] = {"Other": [{"hooks": [{"type": "command", "command": "python3 ~/.claude/cop/peer_hook.py"}]}]}
json.dump(s, open(p, "w"))
EOF
uninst && fail "uninstall should refuse while a hook references the script"
[ -e "$C/cop/peer_hook.py" ] || fail "files deleted despite live hook"

# unrelated hooks that merely end in cop/peer_hook.py are left alone
reset; echo '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"python3 /opt/my-cop/peer_hook.py"}]}]}}' > "$C/settings.json"
inst; uninst; grep -q "my-cop/peer_hook.py" "$C/settings.json" || fail "unrelated hook removed"

# non-dict hook entries: clear error, nothing changed (install and uninstall)
reset; echo '{"hooks":{"PreToolUse":["junk"]}}' > "$C/settings.json"; cp "$C/settings.json" "$T/junk.orig"
inst && fail "install accepted junk entries"; [ ! -e "$C/cop" ] || fail "partial install for junk entries"
uninst && fail "uninstall accepted junk entries"; grep -q Traceback "$T/out" && fail "traceback on junk entries"
cmp -s "$C/settings.json" "$T/junk.orig" || fail "settings changed"

# installed hook command exits 0 even when the script is gone
reset; inst; rm "$C/cop/peer_hook.py"
CMD=$(python3 -c "import json;print(json.load(open('$C/settings.json'))['hooks']['PreToolUse'][0]['hooks'][0]['command'])")
bash -c "$CMD" </dev/null || fail "hook command fails when script is missing"

# marker text inside a user line, CRLF, no trailing newline, non-ASCII settings
reset
printf 'Docs: wrap in <!-- COP:begin --> and <!-- COP:end --> markers.\r\nline2' > "$C/CLAUDE.md"; cp "$C/CLAUDE.md" "$T/crlf.orig"
printf '{"note":"\xd7\xa9\xd7\x9c\xd7\x95\xd7\x9d"}' > "$C/settings.json"
inst; uninst
cmp -s "$C/CLAUDE.md" "$T/crlf.orig" || fail "CLAUDE.md not byte-identical after round trip"
grep -q "שלום" "$C/settings.json" || fail "non-ASCII escaped in settings.json"

# every modifying install gets its own backup, so edits between runs are not lost
reset; printf 'a\n' > "$C/CLAUDE.md"; inst; uninst; printf 'b\n' > "$C/CLAUDE.md"; sleep 1; inst
n=$(ls "$C"/CLAUDE.md.bak-cop-* | wc -l | tr -d ' '); [ "$n" = 2 ] || fail "expected 2 backups, got $n"
grep -q '^b$' "$(ls -t "$C"/CLAUDE.md.bak-cop-* | head -1)" || fail "latest backup is stale"

# HOME unset
env -u HOME bash "$ROOT/standalone/install.sh" >/dev/null 2>&1 && fail "install ran without HOME"

echo "install edge tests OK"
