---
name: vibecheck
description: Audit AI-generated code before shipping. Use when the user wants to check code quality, security review of generated code, "vibe check" a project, scan for hardcoded secrets, SQL injection, eval/exec risks, or asks whether AI-written code is safe to deploy. Zero-dependency Python CLI.
---

# vibecheck

CLI audit code AI-generated: chấm điểm vibe 0-100, bắt lỗ hổng bảo mật & AI slop.

## Khi nào dùng

- User nhờ review code / kiểm tra bảo mật / "code này ship được chưa"
- Code vừa được sinh bởi AI (vibe coding) cần audit nhanh trước khi merge
- Cần báo cáo chất lượng code dạng Markdown/JSON cho PR/CI

## Cách chạy

Tool nằm tại `vibecheck.py` trong thư mục skill này (Python 3.8+, zero dependency):

```bash
python3 <skill_dir>/vibecheck.py <path>                    # text output
python3 <skill_dir>/vibecheck.py <path> --format md        # Markdown report
python3 <skill_dir>/vibecheck.py <path> --format json      # JSON
python3 <skill_dir>/vibecheck.py <path> --min-score 80 --fail-on high   # CI mode
```

- `<path>`: file hoặc thư mục cần quét (mặc định `.`)
- `--exclude PATTERN`: loại trừ path theo regex (lặp được nhiều lần)
- Exit code: `0` pass, `1` fail, `2` lỗi input

## Diễn giải kết quả

- **Vibe score 90-100**: CLEAN — ship được
- **70-89**: OK — dọn nhẹ trước khi merge
- **50-69**: RISKY — phải fix
- **< 50**: DANGER — đừng ship

Nếu có false positive, dùng suppression: `# vibecheck: disable=<rule-id>` (trailing hoặc dòng trên), hoặc file `.vibecheckignore` (regex mỗi dòng).

## Ghi chú cho agent

- Trả lời user bằng ngôn ngữ của họ, tóm tắt findings theo mức độ nghiêm trọng
- Với finding `critical`/`high`: giải thích rủi ro cụ thể và cách fix (không chỉ trích dẫn output)
- Không tự động sửa code trừ khi user yêu cầu; gợi ý fix trước
- Demo mẫu có tại `<skill_dir>/demo/` để test tool
