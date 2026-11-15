# 启动贪吃蛇（当前为“实现步骤 1：静态界面”预览版）
$ErrorActionPreference = "Stop"  # 出错时立即停止
$root = Split-Path -Parent $PSScriptRoot  # 取得项目根目录
$env:PYTHONPATH = Join-Path $root "src"  # 把 src 加入模块搜索路径
python -m greedy_snake @args  # 运行游戏入口并透传参数
