"""平滑图形绘制单元测试。"""  # 模块说明

import unittest  # 标准库测试框架

import pygame  # 图形库

from greedy_snake import config, graphics  # 配置与图形绘制


def make_surface(width=200, height=200):  # 创建测试画布
    """创建填充背景色的透明画布。"""  # 函数说明
    surface = pygame.Surface((width, height), pygame.SRCALPHA)  # 透明画布
    surface.fill((*config.COLOR_BG, 255))  # 填充背景
    return surface  # 返回画布


def pixel(surface, x, y):  # 取像素 RGB
    """返回像素的 RGB 三元组。"""  # 函数说明
    return tuple(surface.get_at((x, y))[:3])  # 只取 RGB


class DarkenTests(unittest.TestCase):  # 颜色加深测试
    """验证颜色加深函数。"""  # 类说明

    def test_darken(self):  # 按比例变暗
        self.assertEqual(graphics.darken((200, 100, 50), 0.5), (100, 50, 25))  # 各通道减半

    def test_clamp(self):  # 不会小于 0
        self.assertEqual(graphics.darken((10, 20, 30), 0.01), (0, 0, 0))  # 取整后归零


class ShapeTests(unittest.TestCase):  # 图形绘制测试
    """验证圆形、重叠、空心方块与圆环。"""  # 类说明

    def test_circle(self):  # 实心圆
        surface = make_surface()  # 测试画布
        graphics.draw_circle(surface, (100, 100), config.SNAKE_RADIUS, config.COLOR_HEAD)  # 画圆
        self.assertEqual(pixel(surface, 100, 100), config.COLOR_HEAD)  # 圆心是蛇头色
        self.assertEqual(pixel(surface, 100 + config.SNAKE_RADIUS + 5, 100), config.COLOR_BG)  # 圆外是背景

    def test_lens_polygon(self):  # 重叠透镜
        first = (100.0, 100.0)  # 第一个圆心
        second = (100.0 + config.SNAKE_SPACING, 100.0)  # 第二个圆心
        points = graphics.lens_polygon(first, second, config.SNAKE_RADIUS)  # 计算透镜多边形
        self.assertGreater(len(points), 0)  # 有重叠区域
        far_points = graphics.lens_polygon((0.0, 0.0), (1000.0, 0.0), config.SNAKE_RADIUS)  # 远处两个圆
        self.assertEqual(far_points, [])  # 不相交时为空

    def test_overlap_darkened(self):  # 重叠区域颜色加深
        surface = make_surface()  # 测试画布
        first = (100.0, 100.0)  # 第一个圆心
        second = (100.0 + config.SNAKE_SPACING, 100.0)  # 第二个圆心
        graphics.draw_circle(surface, first, config.SNAKE_RADIUS, config.COLOR_BODY)  # 画身体圆
        graphics.draw_circle(surface, second, config.SNAKE_RADIUS, config.COLOR_HEAD)  # 画蛇头圆
        lens = graphics.lens_polygon(first, second, config.SNAKE_RADIUS)  # 计算重叠区域
        graphics.draw_polygon(surface, lens, graphics.darken(config.COLOR_HEAD, config.DARKEN_FACTOR))  # 绘制加深重叠
        midpoint = (int((first[0] + second[0]) / 2), int(first[1]))  # 两圆心之间的像素
        self.assertEqual(pixel(surface, *midpoint), graphics.darken(config.COLOR_HEAD, config.DARKEN_FACTOR))  # 重叠处变暗

    def test_hollow_square(self):  # 空心正方形
        surface = make_surface()  # 测试画布
        rect = pygame.Rect(20, 20, config.FOOD_SIDE, config.FOOD_SIDE)  # 食物矩形
        graphics.draw_hollow_square(surface, rect, config.COLOR_FOOD, config.FOOD_OUTLINE)  # 画空心方块
        self.assertEqual(pixel(surface, 20, 20), config.COLOR_FOOD)  # 左上角是绿色边框
        self.assertEqual(pixel(surface, 20 + config.FOOD_SIDE // 2, 20 + config.FOOD_SIDE // 2), config.COLOR_BG)  # 中心是空的

    def test_ring_arc_opening_left(self):  # 圆环缺口朝左
        surface = make_surface()  # 测试画布
        graphics.draw_ring_arc(surface, (100, 100), 50, 8, config.COLOR_TEXT, 210, 510, steps=120)  # 缺口在左侧的圆环
        self.assertEqual(pixel(surface, 50, 100), config.COLOR_BG)  # 正左方是缺口
        self.assertEqual(pixel(surface, 150, 100), config.COLOR_TEXT)  # 正右方是圆环

    def test_triangle(self):  # 实心三角形
        surface = make_surface()  # 测试画布
        graphics.draw_triangle(surface, (150, 100), 30, 50, config.COLOR_ACCENT)  # 尖端向右的三角形
        self.assertEqual(pixel(surface, 149, 100), config.COLOR_ACCENT)  # 尖端附近被填充
        self.assertEqual(pixel(surface, 149, 40), config.COLOR_BG)  # 三角形外是背景
