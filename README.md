# 🔍 vibecheck

**Audit AI-generated code before it ships.** — Chấm điểm "vibe" 0-100 cho code AI sinh ra: bắt lỗ hổng bảo mật, anti-pattern, và "AI slop" phổ biến. Zero dependency, chạy ngay với Python 3.

> Vibe coding ai cũng làm được. Nhưng ship code vibe mà không audit thì không ai cứu được bạn. 😅

## Tại sao cần?

- **Trend vibe coding** bùng nổ → code AI sinh ra đầy rác: secret hardcode, `eval()`, `except: pass`, SQL injection...
- Dev có kinh nghiệm không chê code AI "sai thuật toán" — họ chê **bảo mật và chất lượng**
- `vibecheck` = 1 lệnh, 10 giây, biết ngay code đó ship được hay chưa

## Cài đặt

Không cần cài gì cả — chỉ cần Python 3.8+:

```bash
git clone <repo> && cd vibecheck
python3 vibecheck.py --help
```

Hoặc copy mỗi file `vibecheck.py` vào dự án của bạn. Xong.

## Sử dụng

```bash
# Quét 1 thư mục, output text
python3 vibecheck.py ./src

# Quét 1 file cụ thể
python3 vibecheck.py app.py

# Output Markdown (nhét vào PR comment)
python3 vibecheck.py ./src --format md > report.md

# Output JSON (tích hợp tool khác)
python3 vibecheck.py ./src --format json

# Chế độ CI: fail nếu điểm < 80 hoặc có finding >= high
python3 vibecheck.py ./src --min-score 80 --fail-on high

# Loại trừ thư mục test
python3 vibecheck.py . --exclude "test" --exclude "generated"
```

**Exit codes:** `0` = pass · `1` = fail (dưới min-score hoặc có finding nặng) · `2` = lỗi input

### Điểm bị chặn theo mức nặng

Không thể "90 điểm CLEAN" khi còn lỗi bảo mật:

| Còn finding | Score tối đa | Verdict |
|---|---|---|
| CRITICAL | 30 | DANGER — do not ship |
| HIGH | 69 | RISKY — fix before merge |

Nhờ vậy một lỗi tắt kiểm chứng TLS hay SQL injection không bao giờ bị báo là "production ready".

## Những gì nó bắt được

| Rule | Severity | Mô tả |
|---|---|---|
| `private-key` | 🔴 critical | Private key commit vào source |
| `secret-aws` | 🔴 critical | AWS access key hardcode |
| `secret-token` | 🟠 high | OpenAI/GitHub/Slack/Google token hardcode |
| `secret-assignment` | 🟠 high | password/secret gán thẳng trong code |
| `env-secret` | 🟠 high | Secret thật trong file `.env` (kể cả không quote) |
| `eval-exec` / `js-eval` | 🟠 high | eval/exec/new Function = RCE |
| `shell-true` | 🟠 high | subprocess bật shell → command injection |
| `os-shell` | 🟠 high | os.system/os.popen chạy qua shell |
| `sql-injection` | 🟠 high | SQL ghép chuỗi (f-string/.format/%) |
| `verify-false` | 🟠 high | Tắt kiểm chứng TLS |
| `cors-wildcard` | 🟡 medium | CORS cho phép mọi origin |
| `weak-hash` | 🟡 medium | MD5/SHA1 |
| `pickle-load` | 🟡 medium | Deserialize không an toàn |
| `yaml-unsafe-load` | 🟡 medium | yaml.load thiếu safe Loader |
| `except-pass` | 🟡 medium | Nuốt exception im lặng |
| `debug-log` | 🔵 low | console.log thừa |
| `file-too-long` / `long-function` / `long-lines` | 🔵 low | Code smell cấu trúc |
| `todo-fixme` | ⚪ info | TODO/FIXME AI để lại |

## Scope-aware matching (v0.2) — không false positive

Mỗi rule chỉ match đúng nơi nó cần tìm:

| Scope | Match ở đâu | Ví dụ rule |
|---|---|---|
| `raw` | Toàn bộ text (secret/SQL sống trong string) | secret-*, sql-injection, cors |
| `code` | Chỉ phần code — string & comment bị che | eval/exec, shell-true, TLS-off, except:pass |
| `comment` | Chỉ trong comment | todo-fixme |

Nhờ vậy quét chính vibecheck.py (bảng định nghĩa rule toàn regex!) vẫn sạch findings bảo mật — dogfood thật. (Điểm thấp nhất có thể gặp chỉ là cảnh báo cấu trúc `file-too-long` khi file lớn — và đó là hành vi đúng.)

## Nén lỗi có chủ đích (suppression)

```python
# vibecheck: disable=eval-exec      # dòng dưới bị bỏ qua rule này
dangerous_call(trusted_input)

risky_call(arg)  # vibecheck: disable=eval-exec   # trailing: áp dụng cho chính dòng này

# vibecheck: ignore                  # dòng đầu file: bỏ qua toàn bộ file
```

Hoặc tạo `.vibecheckignore` ở thư mục gốc (mỗi dòng 1 regex):

```
# bỏ qua file sinh tự động
^generated/
legacy_.*
```

## Demo

```bash
python3 vibecheck.py demo
```

```
── vibecheck ──────────────────────────────
Vibe score: 0/100  [DANGER — do not ship]
Findings: 1 critical  8 high  4 medium  1 low  2 info

CRITICAL vulnerable_app.py:8   [secret-aws]    AKIA************REDACTED
HIGH     vulnerable_app.py:19  [sql-injection] query built by interpolation
HIGH     vulnerable_app.py:15  [shell-true]    shell command built from input
... (16 findings total, 14/18 rules triggered; secret values are redacted in reports)
```

Code sạch? 100/100, `CLEAN — production ready`, exit 0. ✅

## Tích hợp CI (GitHub Actions)

```yaml
- name: vibecheck
  run: python3 vibecheck.py ./src --min-score 80 --fail-on high --format sarif > vibecheck.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: vibecheck.sarif
```

> Báo cáo có thể chứa ngữ cảnh source code (secret đã được redact tự động, nhưng vẫn nên coi là tài liệu nội bộ). Đừng đăng thẳng lên PR comment/step summary công khai; dùng artifact riêng hoặc code scanning.

## Autofix — sửa lỗi tự động an toàn

```bash
python3 vibecheck.py ./src --fix-dry-run --fix-unsafe   # xem trước, không ghi gì
python3 vibecheck.py ./src --fix --fix-unsafe           # áp dụng (đổi hành vi, cần opt-in)
```

| Tier | Rule | Fix | Điều kiện |
|---|---|---|---|
| 🟡 unsafe | `yaml-unsafe-load` | `yaml.load` → `yaml.safe_load` (bỏ qua nếu có `Loader=`) | `--fix --fix-unsafe` |
| 🟡 unsafe | `verify-false` | Bỏ tham số tắt kiểm chứng TLS | `--fix --fix-unsafe` |
| 🟡 unsafe | `debug-log` | Xóa dòng `console.log(...)` | `--fix --fix-unsafe` |

Mọi autofix hiện tại đều **đổi hành vi chương trình** (`safe_load` từ chối object tuỳ ý; bỏ `verify`/log thay đổi runtime), nên đều nằm sau `--fix-unsafe` như một consent tường minh. `--fix` một mình chỉ áp dụng tier "safe" (hiện chưa có rule nào), hữu ích cho tương lai. `--fix` **ghi file** và chỉ áp dụng trong thư mục được quét (bỏ qua symlink/đường dẫn ra ngoài). Luôn chạy `--fix-dry-run` và review diff trước; không dùng autofix trong CI mà không commit kết quả.

## Baseline — nhận nuôi code legacy

Dự án cũ đã có sẵn trăm lỗi? Không cần sửa hết ngay — ghi nhận hiện trạng, chỉ fail lỗi mới:

```bash
# lần đầu: ghi nhận toàn bộ findings hiện có
python3 vibecheck.py ./src --write-baseline .vibecheck-baseline.json

# các lần sau (trong CI): chỉ báo lỗi MỚI
python3 vibecheck.py ./src --baseline .vibecheck-baseline.json --fail-on high
```

## SARIF — tích hợp GitHub code scanning

```bash
python3 vibecheck.py ./src --format sarif > vibecheck.sarif
```

Output SARIF 2.1.0 chuẩn — upload thẳng lên GitHub Security tab. Xem mẫu đầy đủ: `examples/github-action.yml`, `examples/pre-commit-config.yaml`.

## Roadmap

- [x] Scope-aware matching (code/string/comment) — chống false positive
- [x] Inline suppression + `.vibecheckignore`
- [x] Baseline cho code legacy
- [x] SARIF 2.1.0 output (GitHub code scanning)
- [x] Ví dụ GitHub Actions + pre-commit
- [x] Autofix (`--fix`) 2 tầng an toàn/không an toàn
- [x] AST hardening: alias, constant propagation, YAML unsafe loader, `os.system`
- [x] Secret trong `.env` + score cap theo severity
- [ ] Rule pack mở rộng (React, Docker, K8s, Terraform)
- [ ] Cross-file data-flow (taint tracking)

## Giới hạn (nói thật)

- Phân tích tĩnh + AST một lớp alias: không theo dõi luồng dữ liệu xuyên file/qua nhiều biến.
- Secret dạng `KEY=value` không quote chỉ bắt trong file `.env*`; secret chia nhỏ/ghép chuỗi có thể lọt.
- SQL injection bắt theo mẫu ghép chuỗi; truy vấn dựng động phức tạp có thể lọt.
- Không thay thế Semgrep/Bandit/CodeQL cho audit chuyên sâu; đây là lớp kiểm tra nhanh trước khi merge.

## Benchmark

`benchmark.py` chạy 9 file corpus (15 cặp ground-truth): precision/recall dùng làm **regression gate**, không phải benchmark toàn ngành. Kết quả hiện tại: 15/15, FP 0, FN 0. Test suite: 44 test (detection, regression, false-positive, Unicode, baseline, SARIF, autofix, v1.0 hardening, redaction).

## License

MIT — dùng thoải mại, share thoải mại.

---

*Built by a 10-year dev/devops veteran who got tired of reviewing AI slop.* 🫡
