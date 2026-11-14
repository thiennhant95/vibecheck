---
name: vibecheck
description: Audit AI-generated code before shipping. Static + AST scan for hardcoded secrets, SQL injection, eval/exec, shell injection, unsafe deserialization and TLS issues, with severity-capped 0-100 scoring and SARIF/JSON/Markdown reports. Optional autofix — every current fix changes behavior and requires the explicit --fix-unsafe opt-in; baseline export for legacy code. Zero-dependency Python CLI.
allowed-tools: Read, Bash(python3:*)
permissions: [file_read, file_write, env]
---

# vibecheck v1.0.7

CLI audit code AI-generated: chấm điểm vibe 0-100, bắt lỗ hổng bảo mật & AI slop. Zero dependency, chỉ cần Python 3.8+.

## Khi nào dùng

- User nhờ review code / kiểm tra bảo mật / "code này ship được chưa"
- Code vừa được sinh bởi AI (vibe coding) cần audit nhanh trước khi merge
- Cần báo cáo chất lượng code dạng Markdown/JSON/SARIF cho PR/CI

## Cách chạy

Tool nằm tại `vibecheck.py` trong thư mục skill này:

```bash
python3 <skill_dir>/vibecheck.py <path>                       # text output
python3 <skill_dir>/vibecheck.py <path> --format md           # Markdown report
python3 <skill_dir>/vibecheck.py <path> --format json         # JSON
python3 <skill_dir>/vibecheck.py <path> --format sarif        # GitHub code scanning
python3 <skill_dir>/vibecheck.py <path> --min-score 80 --fail-on high   # CI mode
python3 <skill_dir>/vibecheck.py <path> --fix --fix-unsafe     # autofix đổi hành vi (opt-in, review diff)
```

- `<path>`: file hoặc thư mục cần quét (mặc định `.`)
- `--exclude PATTERN`: loại trừ path theo regex (lặp được nhiều lần)
- `--baseline FILE` / `--write-baseline FILE`: nhận nuôi code legacy, chỉ fail lỗi mới
- Exit code: `0` pass, `1` fail, `2` lỗi input

## Quyền & phạm vi

- `file_read`: đọc file/thư mục được quét.
- `file_write`: chỉ xảy ra khi dùng `--fix`, `--fix-unsafe`, hoặc `--write-baseline`; mọi thay đổi giới hạn trong thư mục quét, bỏ qua symlink/đường dẫn ra ngoài.
- `env`: chỉ đọc biến môi trường của tiến trình Python (không gọi mạng, không upload dữ liệu).
- Công cụ **không thực thi code được quét**; chỉ parse tĩnh (regex + AST).
- Report/SARIF/baseline đã redact giá trị secret; vẫn nên coi report là tài liệu nội bộ.

## Diễn giải kết quả

- **Vibe score 90-100**: CLEAN — ship được
- **70-89**: OK — dọn nhẹ trước khi merge
- **50-69**: RISKY — phải fix
- **< 50**: DANGER — đừng ship

Điểm bị chặn theo mức nặng: còn finding **HIGH** thì tối đa 69 (RISKY); còn **CRITICAL** thì tối đa 30 (DANGER). Không bao giờ báo "production ready" khi còn lỗi HIGH/CRITICAL.

## False positive & giới hạn

- Suppression: `# vibecheck: disable=<rule-id>` (trailing hoặc dòng trên), `# vibecheck: ignore` (đầu file), hoặc `.vibecheckignore` (regex mỗi dòng, dùng path kiểu POSIX trên mọi OS).
- Giới hạn: phân tích tĩnh + AST một lớp alias; không theo dõi luồng dữ liệu xuyên file; secret dạng `KEY=value` không quote chỉ được bắt trong file `.env*`. Không thay thế Semgrep/Bandit cho audit chuyên sâu.
- Report đã redact giá trị secret (AWS key/token/password) nhưng vẫn chứa ngữ cảnh source: coi là tài liệu nội bộ, không đăng lên step summary/PR comment công khai.
- Autofix là opt-in, ghi file trong thư mục quét (bỏ qua symlink); luôn `--fix-dry-run` và review diff trước khi dùng.

## Ghi chú cho agent

- Trả lời user bằng ngôn ngữ của họ, tóm tắt findings theo mức độ nghiêm trọng
- Với finding `critical`/`high`: giải thích rủi ro cụ thể và cách fix (không chỉ trích dẫn output)
- Không tự động sửa code trừ khi user yêu cầu; gợi ý fix trước (`--fix-dry-run` để xem trước)
- Source + test harness + benchmark: https://github.com/thiennhant95/vibecheck

License: MIT.
