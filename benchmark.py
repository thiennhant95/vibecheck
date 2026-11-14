"""Ground truth benchmark corpus for vibecheck.

Each file declares its expected findings in EXPECTED below.
Rules:
  - vuln_* files: planted flaws; every expected (file, rule) must be found (recall)
  - clean_* files: zero findings allowed (precision)
Run: python3 benchmark.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "vibecheck.py"
CORPUS = HERE / "corpus"

EXPECTED = {
    "vuln_01_secrets.py": ["secret-aws", "secret-token", "secret-assignment"],
    "vuln_02_injection.py": ["shell-true", "sql-injection"],
    "vuln_03_dynamic.py": ["pickle-load", "yaml-unsafe-load", "eval-exec"],
    "vuln_04_ast_only.py": ["eval-exec", "except-pass"],
    "vuln_05_tls_hash.py": ["verify-false", "weak-hash"],
    "vuln_06_web.js": ["cors-wildcard", "js-eval", "debug-log"],
    "clean_01_api.py": [],
    "clean_02_frontend.js": [],
    "clean_03_ruletable.py": [],
}


def run():
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    p = subprocess.run(
        [sys.executable, str(TOOL), str(CORPUS), "--format", "json",
         "--min-score", "0", "--fail-on", "info"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=120, env=env,
    )
    data = json.loads(p.stdout)
    found = {(f["file"], f["rule"]) for f in data["findings"]}
    expected = {(f, r) for f, rules in EXPECTED.items() for r in rules}

    tp = found & expected
    fp = found - expected
    fn = expected - found
    precision = len(tp) / (len(tp) + len(fp)) if (tp or fp) else 1.0
    recall = len(tp) / (len(tp) + len(fn)) if (tp or fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    print("== vibecheck benchmark (ground-truth corpus) ===========")
    print(f"files: {len(EXPECTED)}   expected pairs: {len(expected)}   found pairs: {len(found)}")
    print(f"TP {len(tp)}   FP {len(fp)}   FN {len(fn)}")
    print(f"precision {precision:.3f}   recall {recall:.3f}   F1 {f1:.3f}")
    if fp:
        print("\nFALSE POSITIVES:")
        for f, r in sorted(fp):
            print(f"  {f}: {r}")
    if fn:
        print("\nFALSE NEGATIVES:")
        for f, r in sorted(fn):
            print(f"  {f}: {r}")

    report = {
        "corpus_files": len(EXPECTED),
        "expected_pairs": len(expected),
        "tp": len(tp), "fp": len(fp), "fn": len(fn),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positives": sorted(map(list, fp)),
        "false_negatives": sorted(map(list, fn)),
    }
    (HERE / "BENCHMARK.json").write_text(json.dumps(report, indent=2) + "\n")
    return precision, recall


if __name__ == "__main__":
    precision, recall = run()
    sys.exit(0 if precision >= 0.95 and recall >= 0.95 else 1)
