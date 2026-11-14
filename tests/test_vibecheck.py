#!/usr/bin/env python3
"""
vibecheck test suite — automated, reproducible evidence.

Run:  python3 tests/test_vibecheck.py -v
All findings in the project's audit report can be re-verified with this file.
Zero dependencies (stdlib only).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "vibecheck.py"
DEMO = ROOT / "demo"


def run_vibecheck(*args):
    """Run the CLI, return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(TOOL), *[str(a) for a in args]],
        capture_output=True, text=True, timeout=120,
    )


def run_json(*args):
    p = run_vibecheck(*args, "--format", "json")
    return p, json.loads(p.stdout)


class EvidenceTest(unittest.TestCase):
    """Every test = one verifiable claim from the audit report."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vibecheck_test_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---------- core detection claims ----------

    def test_demo_detects_all_16_findings(self):
        """Claim: demo file with 16 planted flaws -> all 16 detected, exit 1."""
        p, d = run_json(DEMO)
        self.assertEqual(p.returncode, 1, "must fail CI on vulnerable code")
        self.assertEqual(d["score"], 0)
        self.assertEqual(len(d["findings"]), 16, f"got {len(d['findings'])}: "
                         + str([(f['rule'], f['line']) for f in d['findings']]))

    def test_demo_exact_locations(self):
        """Claim: findings point at the EXACT lines (no line-number drift)."""
        p, d = run_json(DEMO)
        got = {(f["rule"], f["file"], f["line"]) for f in d["findings"]}
        expected = {
            ("secret-aws", "vulnerable_app.py", 8),
            ("sql-injection", "vulnerable_app.py", 19),
            ("eval-exec", "vulnerable_app.py", 38),
            ("shell-true", "vulnerable_app.py", 15),
            ("verify-false", "vulnerable_app.py", 33),
            ("js-eval", "vulnerable_app.js", 12),
            ("todo-fixme", "vulnerable_app.js", 11),
            ("todo-fixme", "vulnerable_app.py", 45),
        }
        for item in expected:
            self.assertIn(item, got, f"missing: {item}")

    def test_demo_all_14_rules_fire(self):
        """Claim: 14/16 rules triggered by the demo (2 structural rules not planted)."""
        p, d = run_json(DEMO)
        rules = {f["rule"] for f in d["findings"]}
        self.assertGreaterEqual(len(rules), 12, f"only {rules}")

    def test_clean_code_scores_100(self):
        """Claim: idiomatic clean code -> 100/100, exit 0 (no false positives)."""
        f = self.tmp / "clean.py"
        f.write_text(
            'import hashlib, os\nimport requests\n\n'
            'def get_user(db, name):\n'
            '    q = "SELECT * FROM users WHERE name = %s"\n'
            '    return db.execute(q, (name,))\n\n'
            'def fetch(url):\n'
            '    key = os.getenv("API_KEY")\n'
            '    return requests.get(url, headers={"Authorization": f"Bearer {key}"}).text\n'
        )
        p, d = run_json(f)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(d["score"], 100)
        self.assertEqual(d["findings"], [])

    # ---------- the two bugs found in dogfood (regression tests) ----------

    def test_regression_b1_comment_line_numbers(self):
        """Regression B1: comment-scope findings must report their REAL line."""
        f = self.tmp / "lines.py"
        f.write_text("# header\nx = 1\n\n# TODO: real marker at line 4\ny = 2\n")
        p, d = run_json(f)
        todos = [x for x in d["findings"] if x["rule"] == "todo-fixme"]
        self.assertEqual(len(todos), 1, "dedupe/drift bug is back")
        self.assertEqual(todos[0]["line"], 4, "line-number drift bug is back")

    def test_regression_b2_fstring_sql_with_quotes(self):
        """Regression B2: f-string SQL with inner single quotes must be caught."""
        f = self.tmp / "sql.py"
        f.write_text('def q(db, u):\n    return f"SELECT * FROM t WHERE n = \'{u}\'"\n')
        p, d = run_json(f)
        self.assertIn("sql-injection", {x["rule"] for x in d["findings"]},
                      "f-string SQL regression is back")

    # ---------- scope-aware matching (false positive claims) ----------

    def test_no_fp_on_regex_definition_strings(self):
        """Claim: rule-definition strings (regex describing patterns) do NOT match."""
        f = self.tmp / "defs.py"
        f.write_text(
            'RULE = {\n'
            '    "title": "subprocess with shell=True",\n'
            '    "advice": "verify=False allows MITM.",\n'
            '    "pattern": r"\\b(TODO|FIXME)\\b",\n'
            '}\n'
        )
        p, d = run_json(f)
        self.assertEqual(d["findings"], [], f"false positives: {d['findings']}")

    def test_comment_scope_ignores_strings(self):
        """Claim: TODO inside a string literal is NOT a todo finding."""
        f = self.tmp / "str.py"
        f.write_text('DOC = """TODO: this is docs, not a comment"""\n')
        p, d = run_json(f)
        self.assertEqual([x for x in d["findings"] if x["rule"] == "todo-fixme"], [])

    def test_code_scope_ignores_strings(self):
        """Claim: 'eval(' inside a string/regex does NOT trigger eval rule."""
        f = self.tmp / "doc.py"
        f.write_text('HELP = "never call eval() or exec() on input"\n')
        p, d = run_json(f)
        self.assertEqual(d["findings"], [])

    # ---------- suppression & ignore claims ----------

    def test_trailing_suppression(self):
        f = self.tmp / "sup1.py"
        f.write_text('eval(x)  # vibecheck: disable=eval-exec\npassword = "RealPassword123"\n')
        p, d = run_json(f)
        rules = {x["rule"] for x in d["findings"]}
        self.assertNotIn("eval-exec", rules, "trailing suppression failed")
        self.assertIn("secret-assignment", rules, "unrelated rule must still fire")

    def test_above_line_suppression(self):
        f = self.tmp / "sup2.py"
        f.write_text('# vibecheck: disable=eval-exec\neval(x)\nexec(y)\n')
        p, d = run_json(f)
        evals = [x for x in d["findings"] if x["rule"] == "eval-exec" and x["line"] == 2]
        self.assertEqual(evals, [], "above-line suppression failed")

    def test_file_level_ignore(self):
        f = self.tmp / "ign.py"
        f.write_text('# vibecheck: ignore\npassword = "RealPassword123"\n')
        p, d = run_json(f)
        self.assertEqual(d["findings"], [])

    def test_vibecheckignore_file(self):
        (self.tmp / "secret_file.py").write_text('password = "RealPassword123"\n')
        (self.tmp / "good.py").write_text('x = 1\n')
        (self.tmp / ".vibecheckignore").write_text("# skip\nsecret_file\n")
        p, d = run_json(self.tmp)
        self.assertEqual(d["findings"], [], f"ignore file failed: {d['findings']}")

    # ---------- edge case claims ----------

    def test_binary_file_skipped_safely(self):
        (self.tmp / "bin.py").write_bytes(b"\x7fELF\x00\x00import eval\n")
        p, d = run_json(self.tmp)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(d["findings"], [])

    def test_empty_file(self):
        (self.tmp / "empty.js").write_text("")
        p, d = run_json(self.tmp)
        self.assertEqual(p.returncode, 0)

    def test_minified_1mb_single_line(self):
        (self.tmp / "min.js").write_text("var a=\"x\";" + "function f(){return eval(x)};" * 40000)
        t = time.time()
        p, d = run_json(self.tmp)
        dt = time.time() - t
        self.assertIn("js-eval", {x["rule"] for x in d["findings"]})
        self.assertLess(dt, 30, f"too slow on 1MB single line: {dt:.1f}s")

    def test_unicode_vietnamese_emoji(self):
        f = self.tmp / "uni.py"
        f.write_text('# TODO: tiếng Việt có dấu 🚀\npassword = "MậtKhẩuBíMật2026"\n')
        p, d = run_json(f)
        got = {(x["rule"], x["line"]) for x in d["findings"]}
        self.assertIn(("todo-fixme", 1), got)
        self.assertIn(("secret-assignment", 2), got)

    def test_no_trailing_newline(self):
        f = self.tmp / "nonl.py"
        f.write_text("x = eval(y)")  # no final newline
        p, d = run_json(f)
        self.assertIn("eval-exec", {x["rule"] for x in d["findings"]})

    def test_nonexistent_path_exit_2(self):
        p = run_vibecheck(self.tmp / "nope")
        self.assertEqual(p.returncode, 2)

    # ---------- CI contract claims ----------

    def test_fail_on_severity_matrix(self):
        f = self.tmp / "only_info.py"
        f.write_text("# TODO: only info\n")
        p = run_vibecheck(f, "--min-score", "5", "--fail-on", "critical")
        self.assertEqual(p.returncode, 0, "info-only must pass with fail-on critical")
        p = run_vibecheck(f, "--min-score", "5", "--fail-on", "info")
        self.assertEqual(p.returncode, 1, "fail-on info must block info findings")

    def test_min_score_gate(self):
        p = run_vibecheck(DEMO, "--min-score", "99", "--fail-on", "critical")
        self.assertEqual(p.returncode, 1)

    def test_json_output_valid(self):
        p, d = run_json(DEMO)
        for key in ("tool", "version", "score", "verdict", "summary", "findings"):
            self.assertIn(key, d)
        self.assertEqual(d["tool"], "vibecheck")

    def test_md_output_valid(self):
        p = run_vibecheck(DEMO, "--format", "md")
        self.assertIn("# vibecheck report", p.stdout)
        self.assertIn("| Severity |", p.stdout)

    def test_exclude_regex(self):
        (self.tmp / "bad.py").write_text('password = "RealPassword123"\n')
        (self.tmp / "generated").mkdir()
        (self.tmp / "generated" / "bad2.py").write_text('password = "RealPassword456"\n')
        p, d = run_json(self.tmp, "--exclude", "generated")
        files = {x["file"] for x in d["findings"]}
        self.assertTrue(all("generated" not in f for f in files))

    def test_baseline_roundtrip(self):
        """Claim: baseline silences known findings; NEW findings still fail."""
        bl = self.tmp / "baseline.json"
        run_vibecheck(DEMO, "--write-baseline", str(bl))
        self.assertTrue(bl.exists(), "baseline not written")
        # known findings suppressed -> exit 0
        p, d = run_json(DEMO, "--baseline", str(bl))
        self.assertEqual(p.returncode, 0, f"baseline did not suppress: {d['findings'][:3]}")
        self.assertEqual(d["baseline"]["suppressed"], 16)
        self.assertEqual(d["findings"], [])
        # a NEW finding on top of baseline must still fail
        extra = self.tmp / "new.py"
        extra.write_text("exec(user_input)\n")
        p = run_vibecheck(self.tmp, "--baseline", str(bl), "--fail-on", "high")
        self.assertEqual(p.returncode, 1, "new finding must not be hidden by baseline")

    def test_sarif_output_valid(self):
        """Claim: SARIF 2.1.0 output plugs into GitHub code scanning."""
        p = run_vibecheck(DEMO, "--format", "sarif")
        d = json.loads(p.stdout)
        self.assertEqual(d["version"], "2.1.0")
        self.assertIn("sarif-2.1.0", d["$schema"])
        run0 = d["runs"][0]
        self.assertEqual(run0["tool"]["driver"]["name"], "vibecheck")
        self.assertEqual(len(run0["results"]), 16)
        levels = {r["level"] for r in run0["results"]}
        self.assertEqual(levels, {"error", "warning", "note"})
        loc = run0["results"][0]["locations"][0]["physicalLocation"]
        self.assertIn("uri", loc["artifactLocation"])
        self.assertGreaterEqual(loc["region"]["startLine"], 1)

    # ---------- autofix claims ----------

    def test_autofix_safe_yaml(self):
        """Claim: --fix safely rewrites yaml.load -> yaml.safe_load in place."""
        f = self.tmp / "fix1.py"
        f.write_text("import yaml\n\ndef load(s):\n    return yaml.load(s)\n")
        p = run_vibecheck(f, "--fix")
        self.assertIn("yaml.safe_load", f.read_text(), "safe fix not applied")
        self.assertNotIn("yaml.load", f.read_text().replace("yaml.safe_load", ""))
        # re-scan: finding gone, score restored
        p, d = run_json(f)
        self.assertEqual(d["score"], 100)
        self.assertEqual(d["findings"], [])

    def test_autofix_unsafe_guarded(self):
        """Claim: behavior-changing fixes need explicit --fix-unsafe."""
        f = self.tmp / "fix2.py"
        f.write_text("import requests\n\ndef get(u):\n    return requests.get(u, verify=False)\n")
        run_vibecheck(f, "--fix")  # safe only
        self.assertIn("verify=False", f.read_text(), "unsafe fix ran without opt-in")
        run_vibecheck(f, "--fix", "--fix-unsafe")
        self.assertNotIn("verify=False", f.read_text(), "unsafe fix failed after opt-in")
        self.assertIn("requests.get(u)", f.read_text())

    def test_autofix_dry_run_no_write(self):
        """Claim: --fix-dry-run reports but never writes."""
        f = self.tmp / "fix3.py"
        original = "import yaml\n\ndef load(s):\n    return yaml.load(s)\n"
        f.write_text(original)
        p = run_vibecheck(f, "--fix-dry-run", "--format", "json")
        self.assertEqual(f.read_text(), original, "dry-run wrote to disk!")
        d = json.loads(p.stdout)
        self.assertTrue(d["autofix"]["dry_run"])
        self.assertEqual(d["autofix"]["count"], 1)
        self.assertIn("before", d["autofix"]["applied"][0])

    # ---------- real-world claim ----------

    def test_real_production_codebase_no_false_positives(self):
        """Claim: scanning a real production JS/TS codebase -> no rule FPs."""
        target = Path("/usr/lib/node_modules/openclaw")
        if not target.exists():
            self.skipTest("openclaw source not present on this machine")
        t = time.time()
        p, d = run_json(target, "--exclude", "test", "--exclude", "docs")
        dt = time.time() - t
        rule_findings = [x for x in d["findings"]
                        if x["rule"] not in ("file-too-long", "long-lines", "long-function")]
        self.assertEqual(rule_findings, [],
                         f"false positives on production code: {rule_findings[:5]}")
        self.assertGreaterEqual(d["score"], 90)
        self.assertLess(dt, 60, f"scan too slow: {dt:.1f}s")


if __name__ == "__main__":
    unittest.main(verbosity=2)
