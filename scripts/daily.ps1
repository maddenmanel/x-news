# x-news 每日一键准备脚本 (Windows PowerShell)
# 用途：生成当天的搜索提示，直接准备好粘贴给 Grok 使用
# 用法：
#   右键以 PowerShell 运行，或在项目根目录执行：
#   pwsh scripts/daily.ps1
#   pwsh scripts/daily.ps1 -Date 2026-06-08

param(
    [string]$Date
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=== x-news AI 重量级每日监控 ===" -ForegroundColor Cyan
Write-Host "项目目录: $root" -ForegroundColor Gray

$py = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }

$args = @("scripts/prepare_daily.py")
if ($Date) {
    $args += "--date"
    $args += $Date
}

Write-Host "`n正在生成今日查询与完整 Grok 提示..." -ForegroundColor Yellow
& $py @args

Write-Host "`n完成！" -ForegroundColor Green
Write-Host "下一步：" -ForegroundColor White
Write-Host "1. 全选上面输出的提示内容（或打开 data/daily-prompt-*.txt）" -ForegroundColor Gray
Write-Host "2. 粘贴到当前 Grok 对话中（或任何支持工具调用的 Grok 界面）" -ForegroundColor Gray
Write-Host "3. Grok 会自动使用 x_keyword_search / x_semantic_search 抓取最新内容" -ForegroundColor Gray
Write-Host "4. 分析文章会生成到 reports/ 目录下" -ForegroundColor Gray
Write-Host ""
Write-Host "提示文件位置示例: data/daily-prompt-$(Get-Date -Format 'yyyy-MM-dd').txt" -ForegroundColor DarkGray
Write-Host "报告示例位置: reports/YYYY-MM-DD-ai-heavyweight-analysis.md" -ForegroundColor DarkGray
