"""预览循环逻辑测试（打桩终端，不依赖真实控制台）。"""  # 模块说明

import unittest  # 标准库测试框架
from unittest import mock  # 用于打桩替换终端函数

from greedy_snake import app, terminal  # 被测试模块


class FakeFullscreen:  # 模拟 fullscreen 上下文管理器
    """不触碰真实终端的空上下文。"""  # 类说明

    def __enter__(self):  # 进入上下文
        return self  # 返回自身

    def __exit__(self, *exc_info):  # 退出上下文
        return False  # 不吞掉异常


class PreviewFlowTests(unittest.TestCase):  # 预览按键流程测试
    """验证数字键切换界面、P/R 键与退出逻辑。"""  # 类说明

    def test_key_flow(self):  # 按键序列：1 -> P -> 2 -> R -> Esc
        keys = iter(["1", "p", "2", "r", "\x1b"])  # 预先安排的按键序列
        frames = []  # 收集每次绘制的帧
        with (  # 同时打桩三个终端函数
            mock.patch.object(terminal, "fullscreen", FakeFullscreen),  # 伪全屏上下文
            mock.patch.object(terminal, "read_key", lambda: next(keys)),  # 按序返回按键
            mock.patch.object(terminal, "draw", frames.append),  # 收集帧内容
        ):  # 进入打桩环境
            app.run_preview(seed=1)  # 运行预览循环
        self.assertEqual(len(frames), 5)  # 每轮绘制一帧，共五帧
        self.assertIn("\x1b[H", frames[0])  # 帧内容包含光标定位序列

    def test_quit_by_q(self):  # 首键为 Q 时立即退出
        frames = []  # 收集帧
        with (  # 同时打桩三个终端函数
            mock.patch.object(terminal, "fullscreen", FakeFullscreen),  # 伪全屏上下文
            mock.patch.object(terminal, "read_key", lambda: "q"),  # 固定返回 Q
            mock.patch.object(terminal, "draw", frames.append),  # 收集帧内容
        ):  # 进入打桩环境
            app.run_preview(seed=1)  # 运行预览循环
        self.assertEqual(len(frames), 1)  # 只绘制一帧就退出
