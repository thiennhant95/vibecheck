# vibecheck report

**Vibe score: 0/100** — DANGER — do not ship

| Severity | Count |
|---|---|
| critical | 1 |
| high | 8 |
| medium | 4 |
| low | 1 |
| info | 2 |

| Severity | File:Line | Rule | Snippet |
|---|---|---|---|
| critical | `vulnerable_app.py:8` | secret-aws | `AWS_ACCESS_KEY_ID = "AKIAEXAMPLEEXAMPLE12"` |
| high | `vulnerable_app.js:12` | js-eval | `const result = eval(req.query.code);` |
| high | `vulnerable_app.js:18` | secret-assignment | `const password = "admin12345678";` |
| high | `vulnerable_app.py:9` | secret-token | `OPENAI_API_KEY = "sk-proj-abc123def456ghi789jkl012mno345pqr678"` |
| high | `vulnerable_app.py:10` | secret-assignment | `password = "SuperSecretPassword123"` |
| high | `vulnerable_app.py:15` | shell-true | `subprocess.run("ls " + user_input, shell=True)` |
| high | `vulnerable_app.py:19` | sql-injection | `query = f"SELECT * FROM users WHERE name = '{username}'"` |
| high | `vulnerable_app.py:33` | verify-false | `return requests.get(url, verify=False)` |
| high | `vulnerable_app.py:38` | eval-exec | `result = eval(data)` |
| medium | `vulnerable_app.js:6` | cors-wildcard | `res.setHeader("Access-Control-Allow-Origin", "*");` |
| medium | `vulnerable_app.py:25` | pickle-load | `return pickle.load(f)` |
| medium | `vulnerable_app.py:29` | weak-hash | `return hashlib.md5(pw.encode()).hexdigest()` |
| medium | `vulnerable_app.py:40` | except-pass | `except Exception:` |
| low | `vulnerable_app.js:13` | debug-log | `console.log("result", result);` |
| info | `vulnerable_app.js:11` | todo-fixme | `// FIXME: sanitize input later` |
| info | `vulnerable_app.py:45` | todo-fixme | `# TODO: refactor this monster` |
