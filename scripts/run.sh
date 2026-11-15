#!/usr/bin/env bash
# 启动贪吃蛇，并在项目虚拟环境中准备依赖。
set -euo pipefail  # 遇到错误、未定义变量或管道失败时退出。
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"  # 取得项目根目录。
venv="$root/.venv"  # 使用项目级虚拟环境隔离依赖。
python="$venv/bin/python"  # 指定虚拟环境中的 Python。

if [[ ! -x "$python" ]]; then  # 首次运行时创建虚拟环境。
    python3 -m venv "$venv"
fi

if ! "$python" -c 'import pygame' >/dev/null 2>&1; then  # 缺少图形库时安装项目依赖。
    "$python" -m pip install -r "$root/requirements.txt"
fi

export PYTHONPATH="$root/src"  # 把 src 加入模块搜索路径。
exec "$python" -m greedy_snake "$@"  # 运行游戏入口并透传参数。
