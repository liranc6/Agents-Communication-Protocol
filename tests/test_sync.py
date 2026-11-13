"""The snippet (dense, always-on) and the reference must not drift apart."""
import os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rd(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


CODES = ["CFM", "PTAL", "ACK", "WIP", "DONE", "BLOCK(reason)", "Q?", "FYI", "NI", "ND", "TP/TF", "VRF", "UNV"]
OPS = ["$", "->", "=>", "@", "!", "+", "-", "^", "~", "!="]
LINE = "STATUS|target|result|evidence|next"
FACTS = ["Think in COP", "T3", "N=15", "peer.txt", "shorthand.md", "cop_stats.py", "obs|inf|?", "Cap 30", "T0", "T1", "T2"]


class SyncTests(unittest.TestCase):
    def test_shared_content(self):
        snippet = rd("standalone", "COP-rules.md")
        ref = rd("skills", "cop", "reference", "COP.md")
        skill = rd("skills", "cop", "SKILL.md")
        for name, text in (("snippet", snippet), ("reference", ref)):
            for tok in CODES + [LINE] + FACTS:
                self.assertIn(tok, text, f"{tok!r} missing from {name}")
        for tok in CODES[:6] + [LINE, "Think in COP"]:
            self.assertIn(tok, skill, f"{tok!r} missing from SKILL.md")

    def test_ops_line_matches(self):
        pat = re.compile(r"Ops: (.+)")
        a = pat.search(rd("standalone", "COP-rules.md")).group(1)
        b = pat.search(rd("skills", "cop", "reference", "COP.md")).group(1)
        for op in OPS:
            self.assertIn(op, a)
            self.assertIn(op, b)

    def test_skill_frontmatter_and_paths(self):
        s = rd("skills", "cop", "SKILL.md")
        self.assertTrue(s.startswith("---\nname: cop\n"))
        self.assertIn("description:", s.split("---")[1])
        self.assertTrue(os.path.exists(os.path.join(ROOT, "skills", "cop", "reference", "COP.md")))

    def test_no_local_paths_or_denylisted_terms(self):
        deny = [t.strip().lower() for t in os.environ.get("COP_DENYLIST", "").split(",") if t.strip()]
        for dirpath, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                if f != "test_sync.py" and f.endswith((".md", ".py", ".sh", ".json", ".txt", ".yml")):
                    rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                    text = rd(rel).lower()
                    self.assertNotIn("/users/", text, rel)
                    for t in deny:
                        self.assertNotIn(t, text, rel)

    def test_no_older_version_mentions_outside_changelog(self):
        for rel in ["README.md", "skills/cop/SKILL.md", "skills/cop/reference/COP.md", "standalone/COP-rules.md"]:
            self.assertNotRegex(rd(rel), r"\bv[0-9]\b|legacy", rel)

    def test_irreversible_actions_require_confirmation(self):
        for rel in ["standalone/COP-rules.md", "skills/cop/reference/COP.md", "skills/cop/SKILL.md"]:
            self.assertRegex(rd(rel), r"confirmation unless", rel)
        self.assertIn("do NOT do them unless", rd("hooks", "peer.txt"))

    def test_plugin_files_valid(self):
        import json
        m = json.loads(rd(".claude-plugin", "plugin.json"))
        self.assertEqual(m["name"], "cop")
        self.assertRegex(m["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(m["author"]["name"], "liranc6")
        h = json.loads(rd("hooks", "hooks.json"))
        entry = h["hooks"]["PreToolUse"][0]
        self.assertEqual(entry["matcher"], "Agent|Task")
        cmd = entry["hooks"][0]
        self.assertEqual(cmd["type"], "command")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/peer_hook.py", cmd["command"])
        self.assertTrue(cmd["command"].rstrip().endswith("|| true"))


if __name__ == "__main__":
    unittest.main()
