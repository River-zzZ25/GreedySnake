"""画布工具单元测试。"""  # 模块说明

import unittest  # 标准库测试框架

from greedy_snake import config  # 颜色与样式常量
from greedy_snake.canvas import Canvas, char_width, text_width  # 被测试的画布工具


class TextWidthTests(unittest.TestCase):  # 文本宽度测试
    """验证 ASCII 与中文的显示宽度计算。"""  # 类说明

    def test_ascii(self):  # ASCII 字符占一列
        self.assertEqual(text_width("WSAD"), 4)  # 四个字母共四列

    def test_cjk(self):  # 中文占两列
        self.assertEqual(text_width("贪吃蛇"), 6)  # 三个汉字共六列

    def test_mixed(self):  # 混合文本按宽度累加
        self.assertEqual(text_width("A贪"), 3)  # 一列 ASCII 加两列中文

    def test_char_width(self):  # 单字符宽度判断
        self.assertEqual(char_width("A"), 1)  # ASCII 为窄字符
        self.assertEqual(char_width("墙"), 2)  # 汉字为宽字符


class CanvasTests(unittest.TestCase):  # 画布功能测试
    """验证写入、覆盖、边框与渲染输出。"""  # 类说明

    def test_put_text_advances(self):  # 写入文本后返回结束列
        canvas = Canvas(10, 3)  # 小尺寸画布
        end = canvas.put_text(2, 1, "AB")  # 从第 2 列写入两个字符
        self.assertEqual(end, 4)  # 结束列应为 4

    def test_put_text_cells(self):  # 文本写入到正确的单元格
        canvas = Canvas(10, 3)  # 小尺寸画布
        canvas.put_text(1, 1, "XY", fg="green")  # 写入绿色文本
        self.assertEqual(canvas.grid[1][1], ("X", "green", "black"))  # 第一格内容与颜色
        self.assertEqual(canvas.grid[1][2], ("Y", "green", "black"))  # 第二格内容与颜色

    def test_wide_char(self):  # 中文占两个单元格
        canvas = Canvas(10, 3)  # 小尺寸画布
        end = canvas.put_text(1, 1, "中")  # 写入一个汉字
        self.assertEqual(canvas.grid[1][1][0], "中")  # 主格保存汉字
        self.assertIsNone(canvas.grid[1][2])  # 第二格标记为占位
        self.assertEqual(end, 3)  # 结束列前进两格

    def test_fill_rect(self):  # 矩形填充范围准确
        canvas = Canvas(5, 3)  # 小尺寸画布
        canvas.fill_rect(1, 1, 2, 1, "#", "white", "gray")  # 填充一行两格
        self.assertEqual(canvas.grid[1][1], ("#", "white", "gray"))  # 范围内第一格
        self.assertEqual(canvas.grid[1][2], ("#", "white", "gray"))  # 范围内第二格
        self.assertNotEqual(canvas.grid[1][3], ("#", "white", "gray"))  # 范围外未被填充

    def test_draw_border(self):  # 边框四个直角正确
        canvas = Canvas(10, 5)  # 小尺寸画布
        canvas.draw_border(1, 1, 8, 3)  # 绘制边框
        self.assertEqual(canvas.grid[1][1][0], "┌")  # 左上角
        self.assertEqual(canvas.grid[1][8][0], "┐")  # 右上角
        self.assertEqual(canvas.grid[3][1][0], "└")  # 左下角
        self.assertEqual(canvas.grid[3][8][0], "┘")  # 右下角

    def test_plain_text(self):  # 纯文本行内容正确
        canvas = Canvas(4, 2)  # 小尺寸画布
        canvas.put_text(0, 0, "AB")  # 第一行写入两个字符
        self.assertEqual(canvas.to_plain_text(), "AB  \n    ")  # 其余位置保留空格

    def test_render_contains_ansi(self):  # 渲染结果包含 ANSI 控制序列
        canvas = Canvas(4, 2)  # 小尺寸画布
        frame = canvas.render()  # 生成帧字符串
        self.assertIn("\x1b[", frame)  # 含光标与颜色转义
        self.assertIn(config.FG_COLORS["white"], frame)  # 含白色前景转义
        self.assertIn(config.BG_COLORS["black"], frame)  # 含黑色背景转义
