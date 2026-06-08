#!/usr/bin/env python3
"""简单生成 reports/index.md，列出所有分析报告（按日期倒序）。"""
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT = REPORTS / "index.md"

def extract_title_and_summary(md_path: Path):
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    title = None
    summary = None
    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        if line.strip().startswith("> 摘要：") or line.strip().startswith("> 摘要:"):
            summary = line.strip()[4:].strip()
            break
    return title or md_path.stem, summary or ""

def main():
    files = sorted(
        [p for p in REPORTS.glob("*-ai-heavyweight-analysis.md")],
        key=lambda p: p.stem,
        reverse=True
    )

    lines = ["# AI 重量级动态报告索引\n\n", "按日期倒序。\n\n"]
    for p in files:
        date = p.stem.split("-")[0] + "-" + p.stem.split("-")[1] + "-" + p.stem.split("-")[2]
        title, summary = extract_title_and_summary(p)
        lines.append(f"## [{date}]({p.name})\n")
        if summary:
            lines.append(f"{summary}\n\n")
        lines.append(f"[阅读全文 →]({p.name})\n\n---\n\n")

    if len(files) == 0:
        lines.append("_暂无报告，请先运行 daily.ps1 生成。_\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"已更新 {OUT}")

if __name__ == "__main__":
    main()
