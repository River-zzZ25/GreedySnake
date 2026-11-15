"""游戏状态单元测试。"""  # 模块说明

import math  # 计算圆心距离

import unittest  # 标准库测试框架

from greedy_snake import config  # 尺寸比例
from greedy_snake.layout import Layout  # 布局
from greedy_snake.state import create_initial_state  # 初始状态


class InitialStateTests(unittest.TestCase):  # 初始状态测试
    """验证初始蛇长、圆形间距、食物位置与分数。"""  # 类说明

    def setUp(self):  # 每个测试前创建初始状态
        self.layout = Layout.default()  # 默认布局
        self.state = create_initial_state(self.layout, seed=7)  # 固定种子的初始状态

    def test_snake_length(self):  # 初始长度为蛇头加一格身体
        self.assertEqual(len(self.state.snake), 2)  # 共两个圆

    def test_center_distance(self):  # 蛇头与蛇身圆心距离
        (hx, hy), (bx, by) = self.state.snake[0], self.state.snake[1]  # 头与身体圆心
        self.assertAlmostEqual(math.hypot(hx - bx, hy - by), config.SNAKE_SPACING)  # 圆心距对应四分之一半径重叠

    def test_food_inside_interior(self):  # 食物完整落在可活动区域内
        x, y = self.state.food  # 食物左上角
        interior = self.layout.interior  # 可活动区域
        self.assertGreaterEqual(x, interior.left)  # 左边界
        self.assertGreaterEqual(y, interior.top)  # 上边界
        self.assertLessEqual(x + config.FOOD_SIDE, interior.right)  # 右边界
        self.assertLessEqual(y + config.FOOD_SIDE, interior.bottom)  # 下边界

    def test_food_not_on_snake(self):  # 食物不与蛇重叠
        x, y = self.state.food  # 食物左上角
        for cx, cy in self.state.snake:  # 遍历蛇的圆心
            nearest_x = min(max(cx, x), x + config.FOOD_SIDE - 1)  # 最近横坐标
            nearest_y = min(max(cy, y), y + config.FOOD_SIDE - 1)  # 最近纵坐标
            self.assertGreater(math.hypot(cx - nearest_x, cy - nearest_y), config.SNAKE_RADIUS)  # 距离大于半径

    def test_score_zero(self):  # 初始分数为 0
        self.assertEqual(self.state.score, 0)  # 分数为 0

    def test_seed_reproducible(self):  # 相同随机种子得到相同食物
        first = create_initial_state(self.layout, seed=42)  # 第一次
        second = create_initial_state(self.layout, seed=42)  # 第二次
        self.assertEqual(first.food, second.food)  # 食物位置一致
