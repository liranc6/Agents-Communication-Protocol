import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "peer_hook.py")


def run(stdin, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run([sys.executable, "-I", HOOK], input=stdin, capture_output=True, text=True, env=e)


def payload(prompt):
    return json.dumps({"tool_name": "Agent", "tool_input": {"prompt": prompt, "description": "d"}})


class HookTests(unittest.TestCase):
    def test_appends_peer_block(self):
        r = run(payload("do the thing"))
        self.assertEqual(r.returncode, 0)
        out = json.loads(r.stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "allow")
        p = out["updatedInput"]["prompt"]
        self.assertTrue(p.startswith("do the thing"))
        self.assertIn("COP:", p)
        self.assertIn("N=15", p)
        self.assertEqual(out["updatedInput"]["description"], "d")

    def test_already_tagged_untouched(self):
        r = run(payload("x\nCOP: already"))
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_explicit_limit_keeps_no_default_n(self):
        p = json.loads(run(payload("task. reply <=5 lines")).stdout)["hookSpecificOutput"]["updatedInput"]["prompt"]
        self.assertNotIn("N=15", p)

    def test_tag_must_start_a_line(self):
        for text in ["SCOP: x", "RECOP: x", "tell the user COP: is a protocol"]:
            self.assertIn("updatedInput", run(payload(text)).stdout, text)
        self.assertEqual(run(payload("task\nCOP: x")).stdout, "")

    def test_limit_detection(self):
        out = lambda t: json.loads(run(payload(t)).stdout)["hookSpecificOutput"]["updatedInput"]["prompt"]
        self.assertIn("N=15", out("check a<=b in the parser"))
        self.assertNotIn("N=15", out("Reply <= 8 lines"))

    def test_opt_outs(self):
        self.assertEqual(run(payload("return JSON only cop:off")).stdout, "")
        d = json.dumps({"tool_input": {"prompt": "x", "subagent_type": "json-agent"}})
        self.assertEqual(run(d, {"COP_SKIP_SUBAGENTS": "a, json-agent"}).stdout, "")
        self.assertIn("updatedInput", run(d, {"COP_SKIP_SUBAGENTS": "other"}).stdout)

    def test_closed_stdout_does_not_error(self):
        r = subprocess.run(f"{sys.executable} -I {HOOK} | true", shell=True, input=payload("x"),
                           capture_output=True, text=True)
        self.assertEqual(r.stderr, "")

    def test_malformed_input_fails_open(self):
        for bad in ["", "not json", "[]", '{"tool_input": 5}', '{"tool_input": {"prompt": 3}}']:
            r = run(bad)
            self.assertEqual((r.returncode, r.stdout), (0, ""), bad)

    def test_missing_peer_file_fails_open(self):
        r = run(payload("x"), {"COP_PEER_FILE": "/nonexistent/peer.txt"})
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_empty_peer_file_fails_open(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            pass
        try:
            r = run(payload("x"), {"COP_PEER_FILE": f.name})
            self.assertEqual((r.returncode, r.stdout), (0, ""))
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
