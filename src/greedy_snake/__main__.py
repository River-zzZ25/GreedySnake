"""命令行入口：python -m greedy_snake。"""  # 模块说明

import argparse  # 解析命令行参数
import pathlib  # 处理截图输出目录
import sys  # 标准错误与退出码

import pygame  # 图形库

from . import screens  # 界面渲染
from .app import run  # 图形窗口主循环
from .layout import Layout  # 布局
from .state import create_initial_state  # 初始状态

SCREENSHOT_SCREENS = ("game", "start", "pause", "over")  # 需要生成截图的界面


def build_parser() -> argparse.ArgumentParser:  # 构造参数解析器
    """创建并返回命令行参数解析器。"""  # 函数说明
    parser = argparse.ArgumentParser(prog="greedy-snake", description="贪吃蛇（实现步骤 1：界面）")  # 程序名与说明
    parser.add_argument("--screenshots", type=pathlib.Path, default=None,  # 截图模式参数
                        help="渲染四张界面截图到指定目录后退出（无需打开窗口）")  # 截图模式参数
    parser.add_argument("--seed", type=int, default=None, help="食物随机种子，便于复现画面")  # 随机种子
    return parser  # 返回解析器


def render_screenshots(out_dir: pathlib.Path, seed: int | None) -> int:  # 渲染界面截图
    """把四个界面渲染成 PNG 文件，返回退出码。"""  # 函数说明
    layout = Layout.default()  # 默认布局
    state = create_initial_state(layout, seed)  # 初始状态
    out_dir.mkdir(parents=True, exist_ok=True)  # 创建输出目录
    for name in SCREENSHOT_SCREENS:  # 逐个界面渲染
        state.score = 12 if name in ("pause", "over") else 0  # 暂停/结束界面演示较高分数
        frame = screens.render(name, state, layout)  # 渲染界面
        path = out_dir / f"{name}.png"  # 输出文件路径
        pygame.image.save(frame, str(path))  # 保存 PNG
        print(f"generated: {path}", flush=True)  # 打印生成进度
    return 0  # 成功退出


def main(argv: list[str] | None = None) -> int:  # 命令行主函数
    """解析参数并运行截图模式或图形窗口。"""  # 函数说明
    args = build_parser().parse_args(argv)  # 解析参数
    if args.screenshots:  # 截图模式
        try:  # 捕获图形初始化错误
            return render_screenshots(args.screenshots, args.seed)  # 生成截图后退出
        except pygame.error as exc:  # 图形库错误
            print(f"错误：{exc}", file=sys.stderr)  # 输出错误
            return 1  # 返回失败退出码
    try:  # 运行图形窗口
        run(args.seed)  # 启动窗口主循环
    except KeyboardInterrupt:  # 用户按下 Ctrl+C
        return 0  # 视为正常退出
    except pygame.error as exc:  # 无法创建窗口等图形错误
        print(f"错误：无法创建图形窗口（{exc}）。Ubuntu 下请确认已安装图形环境。", file=sys.stderr)  # 输出友好错误
        return 1  # 返回失败退出码
    return 0  # 正常退出


if __name__ == "__main__":  # 允许直接运行本文件
    sys.exit(main())  # 以主函数返回值作为退出码
