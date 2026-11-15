#!/usr/bin/env bash
# 启动贪吃蛇（图形窗口版本，需要 pygame-ce）
set -euo pipefail  # 出错立即退出
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"  # 取得项目根目录
export PYTHONPATH="$root/src"  # 把 src 加入模块搜索路径
exec python3 -m greedy_snake "$@"  # 运行游戏入口并透传参数
