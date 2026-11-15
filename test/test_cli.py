"""命令行快照测试：真实启动子进程验证入口可运行。"""  # 模块说明

import os  # 读取环境变量
import pathlib  # 拼接路径
import subprocess  # 启动子进程
import sys  # 当前 Python 解释器
import unittest  # 标准库测试框架

ROOT = pathlib.Path(__file__).resolve().parents[1]  # 项目根目录
SRC = ROOT / "src"  # 源码目录


def run_snapshot(*args):  # 运行一次快照命令
    """在当前 Python 中以模块方式执行快照，返回子进程结果。"""  # 函数说明
    env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONIOENCODING="utf-8")  # 补充导入路径与编码
    return subprocess.run(  # 启动子进程
        [sys.executable, "-m", "greedy_snake", *args],  # 模块入口与参数
        capture_output=True,  # 捕获标准输出与错误
        text=True,  # 以文本方式读取
        encoding="utf-8",  # 统一按 UTF-8 解码
        env=env,  # 使用补充后的环境变量
        cwd=ROOT,  # 在项目根目录运行
    )  # 子进程调用结束


class SnapshotTests(unittest.TestCase):  # 快照输出测试
    """验证四种界面快照都能正常输出关键内容。"""  # 类说明

    def test_game_snapshot(self):  # 游戏画面快照
        result = run_snapshot("--snapshot", "game", "--seed", "7")  # 执行快照
        self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
        self.assertIn("得分", result.stdout)  # 含分数文本
        self.assertIn("█", result.stdout)  # 含灰色墙与蛇的实心方块
        self.assertIn("○", result.stdout)  # 含食物圆圈
        self.assertIn("操作指引", result.stdout)  # 含操作指引

    def test_start_snapshot(self):  # 开始界面快照
        result = run_snapshot("--snapshot", "start", "--seed", "7")  # 执行快照
        self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
        self.assertIn("按任意键开始", result.stdout)  # 含开始提示

    def test_pause_snapshot(self):  # 暂停界面快照
        result = run_snapshot("--snapshot", "pause", "--seed", "7")  # 执行快照
        self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
        self.assertIn("已暂停", result.stdout)  # 含暂停文字

    def test_over_snapshot(self):  # 失败界面快照
        result = run_snapshot("--snapshot", "over", "--seed", "7")  # 执行快照
        self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
        self.assertIn("游戏结束", result.stdout)  # 含失败标题
        self.assertIn("重试", result.stdout)  # 含重试入口

    def test_color_snapshot_has_ansi(self):  # 彩色快照包含 ANSI 颜色
        result = run_snapshot("--snapshot", "game", "--color", "--seed", "7")  # 执行彩色快照
        self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
        self.assertIn("\x1b[", result.stdout)  # 含 ANSI 转义序列
        self.assertIn("\x1b[100m", result.stdout)  # 墙使用灰色背景
        self.assertIn("\x1b[104m", result.stdout)  # 蛇头使用蓝色背景
        self.assertIn("\x1b[103m", result.stdout)  # 蛇身使用黄色背景
        self.assertIn("\x1b[92m", result.stdout)  # 食物使用绿色前景
