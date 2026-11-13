import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = os.path.join(ROOT, "tools", "cop_stats.py")


def write_session(d, name, start, reqs, out):
    os.makedirs(os.path.join(d, "projA"), exist_ok=True)
    with open(os.path.join(d, "projA", name), "w") as f:
        f.write("garbage line\n")
        for i in range(reqs):
            f.write(json.dumps({"type": "assistant", "timestamp": start, "requestId": f"{name}{i}",
                                "message": {"content": [], "usage": {"output_tokens": out, "input_tokens": 10}}}) + "\n")


class StatsTests(unittest.TestCase):
    def run_stats(self, d, *args):
        return subprocess.run([sys.executable, "-I", STATS, *args], capture_output=True, text=True,
                              env=dict(os.environ, COP_PROJECTS_DIR=d))

    def test_list_and_split(self):
        with tempfile.TemporaryDirectory() as d:
            write_session(d, "a.jsonl", "2026-01-01T10:00:00Z", 4, 100)
            write_session(d, "b.jsonl", "2026-02-01T10:00:00Z", 4, 50)
            write_session(d, "tiny.jsonl", "2026-02-02T10:00:00Z", 1, 999)  # below --min-reqs
            r = self.run_stats(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(len([l for l in r.stdout.splitlines() if l.startswith("2026-")]), 2)
            r = self.run_stats(d, "--split", "2026-01-15")
            self.assertIn("before", r.stdout)
            self.assertIn("out=100", r.stdout)
            self.assertIn("out=50", r.stdout)

    def test_average_is_request_weighted(self):
        with tempfile.TemporaryDirectory() as d:
            write_session(d, "small.jsonl", "2026-03-01T10:00:00Z", 3, 10)    # 30 out over 3 requests
            write_session(d, "big.jsonl", "2026-03-02T10:00:00Z", 30, 100)    # 3000 out over 30 requests
            r = self.run_stats(d, "--split", "2026-01-01")
            self.assertIn("out=92 ", r.stdout)  # 3030 / 33, not the mean of 10 and 100 (55)

    def test_project_filter_is_literal(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "proj[1]"))
            with open(os.path.join(d, "proj[1]", "a.jsonl"), "w") as f:
                for i in range(3):
                    f.write(json.dumps({"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "requestId": str(i),
                                        "message": {"content": [], "usage": {"output_tokens": 5}}}) + "\n")
            r = self.run_stats(d, "-p", "proj[1]")
            self.assertEqual(len([l for l in r.stdout.splitlines() if l.startswith("2026-")]), 1, r.stdout)

    def test_subagent_transcripts_detected(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "projA", "sess", "subagents"))
            with open(os.path.join(d, "projA", "sess", "subagents", "x.jsonl"), "w") as f:
                for i in range(3):
                    f.write(json.dumps({"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "requestId": str(i),
                                        "message": {"content": [], "usage": {"output_tokens": 5}}}) + "\n")
            self.assertIn(" sub ", self.run_stats(d).stdout)
            self.assertNotIn("2026-", self.run_stats(d, "--main").stdout)

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_stats(d, "--split", "2026-01-01").returncode, 0)

    def test_malformed_variants(self):
        def a(rid, usage, ts="2026-03-01T10:00:00Z", content=None):
            d = {"type": "assistant", "timestamp": ts, "message": {"content": content if content is not None else [], "usage": usage}}
            if rid != "MISSING":
                d["requestId"] = rid
            return json.dumps(d)
        lines = [
            a("r1", {"output_tokens": 5}),
            a("r2", "notadict"),
            a("r3", {"output_tokens": None, "input_tokens": None, "output_tokens_details": None}),
            a(None, {"output_tokens": 7}),
            a("MISSING", {"output_tokens": 7}),
            a("r4", {"output_tokens": 1}, ts=12345),
            a("r5", {"output_tokens": 1}, content=["str", 5, None, {"type": "tool_result", "content": ["x", {"text": 3}, 7]}]),
            json.dumps({"type": "user", "message": "str"}),
            json.dumps([1, 2]),
            json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": 5}]}}),
        ]
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "p"))
            with open(os.path.join(d, "p", "m.jsonl"), "w") as f:
                f.write("\n".join(lines) + "\n")
            r = self.run_stats(d, "--main")
            self.assertEqual(r.returncode, 0, r.stderr)
            row = [l for l in r.stdout.splitlines() if l.startswith("2026-")][0].split()
            self.assertEqual(row[3], "6")  # r1, r3, two unkeyed (not collapsed), r4, r5; r2 has non-dict usage
            self.assertEqual(row[4], "21")  # 5+0+7+7+1+1

    def test_garbage_file_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            write_session(d, "ok.jsonl", "2026-01-01T10:00:00Z", 4, 10)
            with open(os.path.join(d, "projA", "bad.jsonl"), "wb") as f:
                f.write(b"\xff\xfe\x00garbage\n{{{{\n")
            r = self.run_stats(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("2026-01-01", r.stdout)

    def test_bad_split(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ("garbage", "2026-1-1", "2026-01-01T10:00"):
                self.assertEqual(self.run_stats(d, "--split", bad).returncode, 2, bad)
            for ok in ("2026-01-01", "2026-01-01 10:00"):
                self.assertEqual(self.run_stats(d, "--split", ok).returncode, 0, ok)


if __name__ == "__main__":
    unittest.main()
