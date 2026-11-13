#!/bin/bash
# Exercises standalone install/uninstall against a throwaway HOME. Never touches the real ~/.claude.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T"; C="$T/.claude"; mkdir -p "$C"
fail() { echo "FAIL: $*"; exit 1; }

printf 'my rules\n' > "$C/CLAUDE.md"
echo '{"model":"x","hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"echo hi"}]}]}}' > "$C/settings.json"
cp "$C/CLAUDE.md" "$T/md.orig"; cp "$C/settings.json" "$T/st.orig"

bash "$ROOT/standalone/install.sh" >/dev/null
grep -q "COP:begin" "$C/CLAUDE.md" || fail "block missing"
! grep -q "@REF@\|@PEER@\|@STATS@" "$C/CLAUDE.md" || fail "placeholder left"
grep -q "T3 agent-only" "$C/CLAUDE.md" || fail "T3 missing"
[ -f "$C/skills/cop/SKILL.md" ] && [ -f "$C/skills/cop/reference/COP.md" ] && [ -f "$C/cop/peer.txt" ] && [ -f "$C/cop/cop_stats.py" ] || fail "files missing"
grep -q "COP files: ref=$C/skills/cop/reference/COP.md" "$C/CLAUDE.md" || fail "paths line missing"
python3 -c "import json;s=json.load(open('$C/settings.json'));p=s['hooks']['PreToolUse'];assert len(p)==2 and s['model']=='x'" || fail "settings"

# hook works from installed location
OUT=$(echo '{"tool_input":{"prompt":"hi"}}' | python3 "$C/cop/peer_hook.py")
echo "$OUT" | grep -q "COP:" || fail "installed hook"

# check.sh passes on a good install
bash "$ROOT/standalone/check.sh" >/dev/null || fail "check.sh failed after install"

# skill zip has the skill at cop/ and no ownership marker
bash "$ROOT/standalone/build-skill-zip.sh" "$T/cop.zip" >/dev/null
python3 -c "
import zipfile
n=zipfile.ZipFile('$T/cop.zip').namelist()
assert 'cop/SKILL.md' in n and 'cop/reference/COP.md' in n and not any('.cop-managed' in x for x in n), n" || fail "skill zip"

# idempotent, and first backup survives
bash "$ROOT/standalone/install.sh" >/dev/null
[ "$(grep -c 'COP:begin' "$C/CLAUDE.md")" = 1 ] || fail "duplicate block"
python3 -c "import json;assert len(json.load(open('$C/settings.json'))['hooks']['PreToolUse'])==2" || fail "duplicate hook"
for b in "$C"/CLAUDE.md.bak-cop-*; do cmp -s "$b" "$T/md.orig" || fail "md backup not original"; done
for b in "$C"/settings.json.bak-cop-*; do cmp -s "$b" "$T/st.orig" || fail "settings backup not original"; done

bash "$ROOT/standalone/uninstall.sh" >/dev/null
diff <(cat "$T/md.orig") "$C/CLAUDE.md" >/dev/null || fail "CLAUDE.md not restored"
python3 -c "
import json
a=json.load(open('$C/settings.json')); b=json.load(open('$T/st.orig'))
assert a==b, (a,b)" || fail "settings not restored"
[ ! -e "$C/cop" ] && [ ! -e "$C/skills/cop" ] || fail "leftovers"
! bash "$ROOT/standalone/check.sh" >/dev/null 2>&1 || fail "check.sh passed after uninstall"

# fresh HOME with no files at all
rm -rf "$C"; mkdir -p "$C"
bash "$ROOT/standalone/install.sh" >/dev/null && bash "$ROOT/standalone/uninstall.sh" >/dev/null
[ ! -s "$C/CLAUDE.md" ] || fail "fresh CLAUDE.md not empty"
echo "install tests OK"
