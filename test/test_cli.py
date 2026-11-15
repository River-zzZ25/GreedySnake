"""命令行界面截图测试：真实启动子进程验证入口可运行。"""  # 模块说明

import os  # 环境变量
import pathlib  # 路径处理
import struct  # 解析 PNG 尺寸
import subprocess  # 启动子进程
import sys  # 当前解释器
import tempfile  # 临时目录
import unittest  # 标准库测试框架

ROOT = pathlib.Path(__file__).resolve().parents[1]  # 项目根目录
SRC = ROOT / "src"  # 源码目录
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"  # PNG 文件头


def png_size(path: pathlib.Path) -> tuple[int, int]:  # 读取 PNG 尺寸
    """从 PNG 文件的 IHDR 块解析宽高。"""  # 函数说明
    data = path.read_bytes()  # 读取文件内容
    width, height = struct.unpack(">II", data[16:24])  # IHDR 中的宽高
    return width, height  # 返回宽高


def run_screenshots(out_dir: pathlib.Path) -> subprocess.CompletedProcess:  # 运行截图命令
    """以子进程方式执行 --screenshots 并返回结果。"""  # 函数说明
    env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONIOENCODING="utf-8")  # 补充导入路径
    return subprocess.run(  # 启动子进程
        [sys.executable, "-m", "greedy_snake", "--screenshots", str(out_dir), "--seed", "7"],  # 入口与参数
        capture_output=True,  # 捕获输出
        text=True,  # 文本模式
        encoding="utf-8",  # 统一 UTF-8
        env=env,  # 环境变量
        cwd=ROOT,  # 项目根目录
    )  # 子进程调用结束


class ScreenshotTests(unittest.TestCase):  # 截图命令测试
    """验证四个界面截图能够生成且尺寸正确。"""  # 类说明

    def test_generate_four_screenshots(self):  # 生成四张截图
        with tempfile.TemporaryDirectory() as temp_dir:  # 临时输出目录
            out_dir = pathlib.Path(temp_dir)  # 转成路径
            result = run_screenshots(out_dir)  # 执行截图命令
            self.assertEqual(result.returncode, 0, result.stderr)  # 退出码为 0
            for name in ("game", "start", "pause", "over"):  # 四个界面
                path = out_dir / f"{name}.png"  # 截图文件
                self.assertTrue(path.exists())  # 文件存在
                self.assertEqual(path.read_bytes()[:8], PNG_SIGNATURE)  # PNG 文件头正确
                self.assertGreater(path.stat().st_size, 5000)  # 文件有一定大小
                self.assertEqual(png_size(path), (1200, 720))  # 尺寸为窗口大小

    def test_output_message(self):  # 输出生成提示
        with tempfile.TemporaryDirectory() as temp_dir:  # 临时输出目录
            result = run_screenshots(pathlib.Path(temp_dir))  # 执行截图命令
            self.assertIn("generated:", result.stdout)  # 打印了生成提示
