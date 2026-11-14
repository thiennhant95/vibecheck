# 🔍 vibecheck

**Audit AI-generated code before it ships.** — Scores AI-generated code 0-100 for "vibe": catches security holes, anti-patterns, and common AI slop. Zero dependencies, runs with plain Python 3.

> Anyone can vibe code. But shipping vibe-coded code without an audit? Nobody can save you then. 😅

## Why?

- **Vibe coding is booming** → AI-generated code is full of hardcoded secrets, `eval()`, `except: pass`, SQL injection...
- Experienced devs don't complain that AI "gets algorithms wrong" — they complain about **security and quality**
- `vibecheck` = one command, 10 seconds, know instantly if code is shippable

## Install

Nothing to install — just Python 3.8+:

```bash
git clone <repo> && cd vibecheck
python3 vibecheck.py --help
```

Or copy the single `vibecheck.py` file into your project. Done.

## Usage

```bash
python3 vibecheck.py ./src                          # scan a directory
python3 vibecheck.py ./src --format md > report.md  # Markdown for PR comments
python3 vibecheck.py ./src --format sarif > out.sarif  # GitHub code scanning
python3 vibecheck.py ./src --fix                    # safe auto-fixes (behavior-preserving)
python3 vibecheck.py ./src --fix --fix-unsafe       # include behavior-changing fixes
python3 vibecheck.py ./src --min-score 80 --fail-on high  # CI gate

# Adopt on legacy code: record known issues, only fail on NEW ones
python3 vibecheck.py ./src --write-baseline .vibecheck-baseline.json
python3 vibecheck.py ./src --baseline .vibecheck-baseline.json
```

**Exit codes:** `0` pass · `1` fail (below min-score or blocking finding) · `2` bad input

## What it catches

16 rules across 3 scopes — secrets & SQL injection (raw text), code execution & TLS issues (code only, strings/comments masked so **no false positives on rule-definition strings**), TODO markers (comments only). See the Vietnamese README for the full rule table.

## Suppression

```python
result = eval(x)  # vibecheck: disable=eval-exec
# vibecheck: ignore   (first line of file = skip whole file)
```

Plus `.vibecheckignore` (one regex per line).

## Tested with evidence

27 automated tests (`tests/test_vibecheck.py -v`), 15s, zero deps — covering exact-line detection, regression tests for bugs found in dogfood, false-positive guarantees, baseline, SARIF, 1MB minified files, binaries, Unicode, and a real production codebase scan (0 false positives).

## Integrations

- `examples/github-action.yml` — GitHub Actions + SARIF upload to code scanning
- `examples/pre-commit-config.yaml` — pre-commit hook

## License

MIT.

---

*Built by a 10-year dev/devops veteran who got tired of reviewing AI slop.* 🫡
