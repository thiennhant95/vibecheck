"""Clean: a rule table like vibecheck's own. Expected: ZERO findings.

Every dangerous string below is DATA — titles, docs, regex sources.
"""
RULES = [
    {"id": "shell-true", "title": "subprocess with shell=True", "advice": "shell=True enables command injection."},
    {"id": "verify-false", "advice": "verify=False allows MITM. Fix the cert chain."},
    {"id": "eval-exec", "pattern": r"\b(eval|exec)\s*\(", "advice": "eval/exec on untrusted input = RCE."},
    {"id": "except-pass", "advice": "Silent failures hide bugs."},
]
DOC = "usage: eval(x) / exec(y) are dangerous; use safe_eval instead."
PASSWORDS = ["password123_example", "not-a-real-changeme-secret"]  # noqa: demo data


def get_rule(rule_id):
    for r in RULES:
        if r["id"] == rule_id:
            return r
    return None
