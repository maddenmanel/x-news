#!/usr/bin/env python3
"""
x-news 每日准备脚本
用途：根据日期生成精确的 X 搜索查询 + 完整的可直接粘贴给 Grok 的提示词。
运行：python scripts/prepare_daily.py [--date 2026-06-08]
输出：控制台 + data/daily-prompt-YYYY-MM-DD.txt
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
PROMPTS_DIR = ROOT / "prompts"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_target_date(date_str: str | None) -> str:
    if date_str:
        return date_str
    # 默认抓取“昨天”到现在的内容（用户通常早上运行看前一天+今天早上的）
    yesterday = datetime.utcnow() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def build_queries(templates: dict, since: str) -> list[dict]:
    results = []
    for t in templates.get("templates", []):
        q = t["query_template"].replace("{since}", since)
        results.append({
            "id": t["id"],
            "name": t["name"],
            "query": q,
            "mode": t.get("mode", "Latest"),
            "limit": t.get("limit", 10),
            "why": t.get("why", "")
        })
    return results

def build_full_grok_prompt(date: str, queries: list[dict], semantic_queries: list[dict], vip_accounts: list[dict]) -> str:
    analysis_prompt_path = PROMPTS_DIR / "analysis-prompt-zh.md"
    base_analysis = analysis_prompt_path.read_text(encoding="utf-8") if analysis_prompt_path.exists() else ""

    lines = []
    lines.append(f"请帮我执行今天的 AI 重量级动态抓取与分析（日期：{date}）。\n")
    lines.append("## 1. 使用以下精确查询调用你的 x_keyword_search 和 x_semantic_search 工具\n")
    lines.append("优先使用 x_keyword_search（支持高级运算符），必要时补充 semantic_search 获取遗漏的重要内容。\n")
    lines.append("请并行调用多个搜索，抓取 limit 建议按模板设置。抓取后请一并获取重要帖子的 thread（如果有 conversation_id 不同或你觉得需要上下文时使用 x_thread_fetch）。\n\n")

    lines.append("### 推荐 X Keyword Queries（直接复制使用）\n")
    for i, q in enumerate(queries, 1):
        lines.append(f"**{i}. {q['name']}**\n")
        lines.append(f"query: `{q['query']}`\n")
        lines.append(f"mode: {q['mode']}, limit: {q['limit']}\n")
        if q['why']:
            lines.append(f"理由：{q['why']}\n")
        lines.append("\n")

    if semantic_queries:
        lines.append("### 推荐 Semantic Search\n")
        for sq in semantic_queries:
            lines.append(f"- query: `{sq.get('query','')}` (limit {sq.get('limit',5)})\n")
        lines.append("\n")

    lines.append("## 2. 重点 VIP 账号（可额外针对性补抓）\n")
    for acc in vip_accounts:
        pri = acc.get("priority", 5)
        lines.append(f"- @{acc['handle']} ({acc['name']}, {acc.get('lab','')}) 优先级 {pri}\n")
    lines.append("\n")

    lines.append("## 3. 数据收集要求\n")
    lines.append("- 只保留高信号内容：来自 VIP、或 min_faves 较高、或明确包含模型发布/研究突破/重大合作/基础设施新闻。\n")
    lines.append("- 记录每条帖子的：作者、完整文本、engagement（likes/reposts/views）、时间、链接（https://x.com/.../status/ID）、是否引用其他帖。\n")
    lines.append("- 如果看到重要线程，请使用工具获取父帖+回复上下文。\n")
    lines.append("- 去重，合并同一事件的不同讨论。\n\n")

    lines.append("## 4. 生成分析文章\n")
    lines.append("抓取完成后，请严格按照下面模板（已加载）生成一篇高质量中文分析文章，并直接保存到项目内：\n")
    lines.append(f"reports/{date}-ai-heavyweight-analysis.md\n\n")

    lines.append(base_analysis.replace("{date}", date).replace("{generated_at}", datetime.now().isoformat()))
    lines.append("\n\n---\n")
    lines.append("执行完毕后，请把生成的完整 Markdown 文章内容直接输出，并同时写入 reports/ 目录下的对应文件。\n")
    lines.append("如果工具调用受限，请告诉我你实际拿到的数据，我会继续协助迭代分析。\n")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="准备每日 AI X 重量级监控查询和提示")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD，默认昨天", default=None)
    args = parser.parse_args()

    target_date = get_target_date(args.date)
    print(f"[x-news] 目标监控日期范围 since: {target_date} （含今天早盘）")

    templates = load_json(CONFIG_DIR / "search-templates.json")
    accounts_cfg = load_json(CONFIG_DIR / "vip-accounts.json")

    queries = build_queries(templates, target_date)
    semantic = templates.get("semantic_queries", [])
    vips = accounts_cfg.get("accounts", []) + accounts_cfg.get("chinese_focus", [])

    full_prompt = build_full_grok_prompt(target_date, queries, semantic, vips)

    out_file = DATA_DIR / f"daily-prompt-{target_date}.txt"
    out_file.write_text(full_prompt, encoding="utf-8")

    print(f"\n=== 已生成可直接复制的完整提示 ===\n保存位置: {out_file}\n")
    print("=== 下面是提示内容（可全选复制发给 Grok） ===\n")
    print(full_prompt)
    print("\n=== 提示结束 ===")
    print(f"\n提示：运行完成后，分析文章会出现在 reports/{target_date}-ai-heavyweight-analysis.md")

if __name__ == "__main__":
    main()
