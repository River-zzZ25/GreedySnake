"""命令行入口：python -m greedy_snake。"""  # 模块说明

import argparse  # 解析命令行参数
import sys  # 标准错误输出与退出码

from . import screens, terminal  # 界面绘制与终端工具
from .app import run_preview  # 交互式预览主循环
from .state import create_initial_state  # 初始游戏状态

SCREEN_CHOICES = ("game", "start", "pause", "over")  # 支持快照的界面名列表


def build_parser() -> argparse.ArgumentParser:  # 构造参数解析器
    """创建并返回命令行参数解析器。"""  # 函数说明
    parser = argparse.ArgumentParser(prog="greedy-snake", description="贪吃蛇（实现步骤 1：静态界面）")  # 程序名与说明
    parser.add_argument("--snapshot", choices=SCREEN_CHOICES, help="渲染指定界面后直接退出，便于验收")  # 单帧快照参数
    parser.add_argument("--seed", type=int, default=None, help="食物随机种子，便于复现画面")  # 随机种子参数
    parser.add_argument("--color", action="store_true", help="快照模式保留 ANSI 颜色")  # 颜色开关参数
    return parser  # 返回解析器


def run_snapshot(screen: str, seed: int | None, color: bool) -> int:  # 渲染单帧快照
    """渲染指定界面一次并退出，返回进程退出码。"""  # 函数说明
    canvas = screens.render(screen, create_initial_state(seed))  # 生成指定界面的画布
    if color:  # 需要颜色时输出 ANSI 帧
        terminal.setup()  # 初始化终端以支持 ANSI
        terminal.draw(canvas.render())  # 输出带颜色的画面
    else:  # 默认输出纯文本便于查看
        print(canvas.to_plain_text())  # 输出无颜色整屏文本
    return 0  # 成功退出


def main(argv: list[str] | None = None) -> int:  # 命令行主函数
    """解析参数并运行快照或交互式预览。"""  # 函数说明
    args = build_parser().parse_args(argv)  # 解析命令行参数
    terminal.setup()  # 初始化终端编码与 ANSI
    if args.snapshot:  # 快照模式
        return run_snapshot(args.snapshot, args.seed, args.color)  # 输出一帧后退出
    try:  # 捕获用户中断以正常恢复终端
        run_preview(args.seed)  # 启动交互式预览
    except KeyboardInterrupt:  # 用户按下 Ctrl+C
        return 0  # 视为正常退出
    except RuntimeError as exc:  # 没有交互式终端等错误
        print(f"错误：{exc}", file=sys.stderr)  # 输出友好错误信息
        return 1  # 返回失败退出码
    return 0  # 正常退出


if __name__ == "__main__":  # 允许直接执行本文件
    sys.exit(main())  # 以主函数返回值作为退出码
