"""布局计算单元测试。"""  # 模块说明

import unittest  # 标准库测试框架

from greedy_snake import config  # 尺寸与比例
from greedy_snake.layout import Layout, Rect  # 被测试对象


class RectTests(unittest.TestCase):  # 矩形测试
    """验证矩形边界、中心与点击判断。"""  # 类说明

    def test_bounds(self):  # 右边界与下边界
        rect = Rect(10, 20, 100, 50)  # 构造矩形
        self.assertEqual(rect.right, 109)  # 右边为左加宽减一
        self.assertEqual(rect.bottom, 69)  # 下边为上加高减一

    def test_center(self):  # 中心点
        self.assertEqual(Rect(0, 0, 100, 50).center, (50, 25))  # 中心坐标

    def test_inset(self):  # 向内收缩
        rect = Rect(0, 0, 100, 50).inset(10)  # 四边各收缩 10
        self.assertEqual((rect.left, rect.top, rect.width, rect.height), (10, 10, 80, 30))  # 收缩结果

    def test_contains(self):  # 点是否在矩形内
        rect = Rect(10, 20, 100, 50)  # 构造矩形
        self.assertTrue(rect.contains((10, 20)))  # 左上角属于矩形
        self.assertTrue(rect.contains((109, 69)))  # 右下角属于矩形
        self.assertFalse(rect.contains((110, 69)))  # 右外侧不属于矩形


class LayoutTests(unittest.TestCase):  # 布局测试
    """验证窗口、棋盘与面板尺寸符合设计。"""  # 类说明

    def setUp(self):  # 每个测试前创建默认布局
        self.layout = Layout.default()  # 默认布局

    def test_window(self):  # 窗口尺寸来自配置
        self.assertEqual(self.layout.window, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))  # 窗口宽高

    def test_board_bounds(self):  # 棋盘边界
        self.assertEqual(self.layout.board.left, config.MARGIN)  # 左边界
        self.assertEqual(self.layout.board.top, config.HEADER_HEIGHT)  # 上边界
        self.assertEqual(self.layout.board.width, config.WINDOW_WIDTH - 2 * config.MARGIN)  # 宽度
        self.assertEqual(self.layout.board.height,  # 棋盘高度
                         config.WINDOW_HEIGHT - config.HEADER_HEIGHT - config.FOOTER_HEIGHT)  # 高度

    def test_interior(self):  # 可活动区域由棋盘向内收缩墙厚
        self.assertEqual(self.layout.interior.left, self.layout.board.left + config.WALL_THICKNESS)  # 左侧
        self.assertEqual(self.layout.interior.top, self.layout.board.top + config.WALL_THICKNESS)  # 上侧
        self.assertEqual(self.layout.interior.right,  # 右侧内边界
                         self.layout.board.right - config.WALL_THICKNESS)  # 右侧

    def test_snake_ratio(self):  # 蛇圆直径比例为 3 个单位
        self.assertEqual(config.SNAKE_DIAMETER, 3 * config.UNIT)  # 头与身体直径 3 单位

    def test_food_ratio(self):  # 食物边长比例为 1.5 个单位
        self.assertEqual(config.FOOD_SIDE, int(1.5 * config.UNIT))  # 食物正方形边长 1.5 单位
        self.assertEqual(config.FOOD_SIDE, config.SNAKE_DIAMETER // 2)  # 恰好为蛇直径的一半

    def test_overlap_ratio(self):  # 重叠为半径的四分之一
        self.assertAlmostEqual(config.SNAKE_SPACING, 2 * config.SNAKE_RADIUS - config.SNAKE_RADIUS / 4)  # 圆心距
        self.assertAlmostEqual(config.SNAKE_OVERLAP, config.SNAKE_RADIUS / 4)  # 重叠长度

    def test_pause_panel_half_size(self):  # 暂停面板边长为旧版一半
        rect = self.layout.pause_panel_rect()  # 暂停面板
        self.assertEqual((rect.width, rect.height), (400, 168))  # 旧版约 800×336 的一半

    def test_pause_icon_centers(self):  # 三个图标中心水平排列
        centers = self.layout.pause_icon_centers()  # 三个中心
        self.assertEqual(centers[1][0] - centers[0][0], config.PAUSE_ICON_SPACING)  # 左侧与中间间距
        self.assertEqual(centers[2][0] - centers[1][0], config.PAUSE_ICON_SPACING)  # 中间与右侧间距

    def test_pause_icon_rects(self):  # 图标点击区域包含中心
        for rect, center in zip(self.layout.pause_icon_rects(), self.layout.pause_icon_centers()):  # 遍历图标
            self.assertTrue(rect.contains(center))  # 中心点落在点击区域内
