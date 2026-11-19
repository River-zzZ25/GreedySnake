"""连续运动验收回归：真实边界、路径跟随、自由角度和帧率一致性。"""  # 模块说明

import math  # 独立计算距离与角度
from dataclasses import replace  # 缩小测试棋盘
import unittest  # 标准测试框架

from greedy_snake import config  # 游戏尺寸与速度
from greedy_snake.layout import Layout, Rect  # 测试棋盘
from greedy_snake.state import (GameState, advance_state, create_initial_state,  # 状态与物理更新
                                _circle_hits_square, _food_contact, _body_contact, _random_food)  # 几何边界检查


class ContinuousStateTests(unittest.TestCase):  # 连续玩法测试
    """在相同时间与几何场景下核对玩家可观察的行为。"""  # 类说明

    def setUp(self):  # 创建独立一局
        self.layout = Layout.default()  # 默认棋盘
        self.state = create_initial_state(self.layout, seed=7)  # 可重复的随机流
        self.state.food = (1100.0, 600.0)  # 放到测试路线之外

    def step(self, seconds, steering=(0.0, 0.0), fps=120):  # 推进一段时间
        """以指定帧率推进，并在碰撞时停止。"""  # 函数说明
        for _ in range(round(seconds * fps)):  # 模拟独立帧
            if advance_state(self.state, self.layout, 1 / fps, steering):  # 执行物理
                return True  # 提前返回碰撞
        return False  # 安全完成这段运动

    def test_initial_size_and_length(self):  # 用户确认按面积缩小到四分之一
        self.assertAlmostEqual(config.SNAKE_DIAMETER, 36 * math.sqrt(2 / 3))
        self.assertAlmostEqual(config.FOOD_SIDE, 18 * math.sqrt(2 / 3))
        self.assertEqual(len(self.state.snake), 2)  # 保留头加一节身体
        self.assertAlmostEqual(math.dist(*self.state.snake), config.SNAKE_SPACING)
        self.assertEqual(self.state.score, 0)  # 初始零分

    def test_continuous_forward_motion_without_input(self):  # 每帧都有位移
        head = self.state.snake[0]  # 初始位置
        advance_state(self.state, self.layout, 1 / 120)  # 一帧
        self.assertAlmostEqual(self.state.snake[0][0] - head[0], config.SNAKE_SPEED / 120)  # 不等待半秒
        self.assertLess(math.dist(head, self.state.snake[0]), 2)  # 不会跳一整节
        self.step(1)  # 无按键也会继续走
        self.assertAlmostEqual(self.state.snake[0][0] - head[0], config.SNAKE_SPEED * (1 + 1 / 120))  # 恒定速度

    def test_short_press_leaves_arbitrary_heading(self):  # 释放后保留中间角度
        self.assertFalse(self.step(0.1, (0, -1)))  # 短暂向上施力
        direction = self.state.direction  # 松开时的航向
        self.assertGreater(direction[0], 0)  # 仍有横向分量
        self.assertLess(direction[1], 0)  # 同时有向上分量
        self.assertNotAlmostEqual(abs(direction[0]), abs(direction[1]))  # 不限制为 45 度
        before = self.state.snake[0]  # 释放时位置
        self.assertFalse(self.step(0.5))  # 松开后继续前进
        self.assertAlmostEqual(self.state.direction[0], direction[0])  # 航向保持
        self.assertAlmostEqual(self.state.direction[1], direction[1])  # 纵向分量保持
        self.assertAlmostEqual(math.dist(before, self.state.snake[0]), config.SNAKE_SPEED * 0.5)  # 不因松键停车

    def test_turning_is_continuous_and_speed_stays_constant(self):  # 无直角瞬移
        previous_angle = 0.0  # 初始向右
        for _ in range(90):  # 持续按住 W
            head = self.state.snake[0]  # 上一帧位置
            self.assertFalse(advance_state(self.state, self.layout, 1 / 120, (0, -1)))  # 平滑转向
            angle = math.atan2(self.state.direction[1], self.state.direction[0])  # 新角度
            self.assertLessEqual(abs(angle - previous_angle), config.TURN_RATE / 120 + 1e-9)  # 角度逐渐改变
            self.assertAlmostEqual(math.dist(head, self.state.snake[0]), config.SNAKE_SPEED / 120, delta=0.0001)  # 曲线不减速
            previous_angle = angle  # 为下一帧保存角度

    def test_opposite_input_makes_curved_uturn(self):  # 反向键不能失效或瞬间掉头
        self.assertFalse(self.step(0.1, (-1, 0)))  # 先按反向键一小段时间
        self.assertGreater(self.state.direction[0], 0)  # 仍在转弯途中
        self.assertFalse(self.step(1.4, (-1, 0)))  # 持续按住完成掉头
        self.assertLess(self.state.direction[0], -0.99)  # 最终朝左
        self.assertGreater(abs(self.state.snake[0][1] - 364), 50)  # 经过有宽度的弧线

    def test_body_follows_recorded_curve(self):  # 身体必须经过蛇头实际走过的位置
        self.state = GameState(snake=[(600 - index * config.SNAKE_SPACING, 364) for index in range(7)],  # 足够长的蛇
                               food=(1100, 600))  # 食物远离路径
        history = [self.state.snake[0]]  # 记录实际头部位置
        dt = 1 / 240  # 每个记录对应半像素左右位移
        for _ in range(180):  # 持续转弯四分之三秒
            self.assertFalse(advance_state(self.state, self.layout, dt, (0, -1)))  # 按真实物理推进
            history.append(self.state.snake[0])  # 保存头部经过的位置
        delay = round(config.SNAKE_SPACING / (config.SNAKE_SPEED * dt))  # 一节对应的历史点数
        for index in range(1, 4):  # 前三节都应在已记录的历史路径上
            self.assertLess(math.dist(self.state.snake[index], history[-1 - index * delay]), 1.0)

    def test_history_is_bounded(self):  # 不保留整局无限增长的路径
        self.step(3)  # 连续前进三秒
        self.assertLess(len(self.state.trail), 300)  # 两节蛇只需有限轨迹

    def test_same_motion_at_30_60_120_fps(self):  # 帧率改变不改变路线和速度
        results = []  # 各帧率最终状态
        for fps in (30, 60, 120):  # 不同显示刷新率
            self.setUp()  # 重置相同初始条件
            self.assertFalse(self.step(0.5, (0, -1), fps))  # 相同施力时长
            self.assertFalse(self.step(0.5, (0, 0), fps))  # 相同松开时长
            results.append(self.state.snake)  # 保存结果
        for other in results[1:]:  # 与 30 FPS 比较
            for first, second in zip(results[0], other):  # 每个身体圆
                self.assertLess(math.dist(first, second), 1e-7)  # 路线一致

    def test_all_walls_stop_at_visible_edge(self):  # 回归用户截图中的提前失败
        interior, radius = self.layout.interior, config.SNAKE_RADIUS  # 实际边界
        cases = (((interior.left + radius + 3.7, 400), (-1, 0), (interior.left + radius, 400)),  # 左墙
                 ((interior.right + 1 - radius - 3.7, 400), (1, 0), (interior.right + 1 - radius, 400)),  # 右墙
                 ((600, interior.top + radius + 3.7), (0, -1), (600, interior.top + radius)),  # 上墙
                 ((600, interior.bottom + 1 - radius - 3.7), (0, 1), (600, interior.bottom + 1 - radius)))  # 下墙
        for head, direction, contact in cases:  # 分别接触四面墙
            with self.subTest(direction=direction):  # 独立报告方向
                body = (head[0] - direction[0] * config.SNAKE_SPACING, head[1] - direction[1] * config.SNAKE_SPACING)  # 颈部
                state = GameState(snake=[head, body], food=(800, 500), direction=direction, score=2)  # 构造贴墙前状态
                self.assertFalse(advance_state(state, self.layout, 0.01))  # 尚未接触不能失败
                self.assertTrue(advance_state(state, self.layout, 0.1))  # 本帧中途发生接触
                self.assertLess(math.dist(state.snake[0], contact), 1e-8)  # 恰好贴墙，不能停在上一帧
                self.assertEqual(state.score, 2)  # 保留得分
                self.assertEqual(state.food, (800, 500))  # 保留食物

    def test_diagonal_wall_contact(self):  # 斜向运动也正确贴墙
        direction = (0.6, -0.8)  # 任意斜向航向
        head = (600.3, self.layout.interior.top + config.SNAKE_RADIUS + 8)  # 距上墙 8 像素
        body = (head[0] - direction[0] * 31.5, head[1] - direction[1] * 31.5)  # 身体在后方
        state = GameState(snake=[head, body], direction=direction)  # 无食物测试
        self.assertTrue(advance_state(state, self.layout, 0.2))  # 斜向撞墙
        self.assertAlmostEqual(state.snake[0][0], 606.3)  # 按真实斜线到达接触点
        self.assertAlmostEqual(state.snake[0][1], self.layout.interior.top + config.SNAKE_RADIUS)  # 头部外围贴墙

    def test_eats_off_axis_food_and_adds_one_segment(self):  # 食物不必与蛇中心对齐
        self.state.food = (640.37, 375.29)  # 非整数且偏离水平轨迹
        self.assertFalse(self.step(0.3))  # 沿水平方向经过食物
        self.assertEqual(self.state.score, 1)  # 实际相交即可吃到
        self.assertEqual(len(self.state.snake), 3)  # 新增长一节
        self.assertAlmostEqual(self.state.snake[0][0], 656.7)
        self.assertNotEqual(self.state.food, (640.37, 375.29))  # 生成新食物
        self.assertTrue(all(self.layout.interior.contains(point) for point in self.state.snake))  # 增长后的身体仍在棋盘内

    def test_new_food_is_inside_board_and_avoids_all_circles(self):  # 后续食物随机位置合法
        for seed in range(20):  # 覆盖多个随机种子
            state = create_initial_state(self.layout, seed)  # 独立随机流
            state.food = (635, 364)  # 下一段运动内的食物
            self.assertFalse(advance_state(state, self.layout, 0.2))  # 吃掉并重新生成
            self.assertIsNotNone(state.food)  # 空间充足应有新食物
            half = config.FOOD_SIDE / 2  # 半边长
            for sign in (-1, 1):  # 正方形两端
                self.assertTrue(self.layout.interior.contains((state.food[0] + sign * half, state.food[1] + sign * half)))  # 端点在内部
            for center in state.snake:  # 检查每节身体
                self.assertFalse(_circle_hits_square(center, config.SNAKE_RADIUS, state.food, config.FOOD_SIDE))  # 不重叠

    def test_empty_board_space_does_not_spawn_on_body(self):  # 没有空位也不能把食物塞进身体
        centers = [(x, y) for x in range(0, 61, 12) for y in range(0, 61, 12)]  # 用圆覆盖整个棋盘
        self.assertIsNone(_random_food(self.state.rng, replace(self.layout, interior=Rect(0, 0, 60, 60)), centers))  # 无合法食物位置

    def test_seed_reproduces_initial_and_next_food(self):  # 固定种子可重放
        first = create_initial_state(self.layout, 42)  # 第一局
        second = create_initial_state(self.layout, 42)  # 第二局
        self.assertEqual(first.food, second.food)  # 初始食物相同
        for state in (first, second):  # 两局使用相同运动
            state.food = (635, 364)  # 保证吃到
            advance_state(state, self.layout, 0.2)  # 更新状态
        self.assertEqual(first.food, second.food)  # 后续随机结果相同

    def test_self_collision_on_curve_stops_at_circle_contact(self):  # 沿圆弧绕回身体会碰撞
        centers = [(700 - index * config.SNAKE_SPACING, 400) for index in range(14)]
        state = GameState(snake=centers, food=(1100, 600))
        contact = _body_contact(centers, [(700, 400), (700 - config.SNAKE_SPACING, 400),
                                         (700 - config.SNAKE_DIAMETER + 0.5, 400), *centers[3:]])
        self.assertIsNotNone(contact)


class SweptGeometryTests(unittest.TestCase):  # 几何边界回归
    """覆盖方块角部、圆周相切和跨过物体的运动。"""  # 类说明

    def test_square_corner_is_not_bounding_box(self):  # 圆角不按方形包围框碰撞
        self.assertFalse(_circle_hits_square((0, 0), 18, (24, 24), 18))  # 两个轴都近但角点仍在圆外
        self.assertTrue(_circle_hits_square((0, 0), 18, (21, 21), 18))  # 更近角点实际接触

    def test_fast_motion_cannot_skip_food(self):  # 两帧均在食物外也要检测途中接触
        contact = _food_contact((0, 0), (200, 0), (100, 0))  # 跨过食物的整段位移
        self.assertAlmostEqual(contact, (100 - config.FOOD_SIDE / 2 - config.SNAKE_RADIUS) / 200)

    def test_grazing_food_corner(self):  # 擦过方块圆角边缘
        half, radius = config.FOOD_SIDE / 2, config.SNAKE_RADIUS  # 实际轮廓尺寸
        self.assertIsNotNone(_food_contact((-100, half + radius), (100, half + radius), (0, 0)))  # 相切吃到
        self.assertIsNone(_food_contact((-100, half + radius + 0.01), (100, half + radius + 0.01), (0, 0)))  # 离开 0.01 像素不吃

    def test_moving_circle_contact_is_not_a_square(self):  # 身体圆角附近也不能误判
        self.assertIsNone(_body_contact([(0, 0), (-31.5, 0), (30, 30)], [(1, 0), (-30.5, 0), (30, 30)]))  # 圆周未接触
        contact = _body_contact([(0, 0), (-31.5, 0), (100, 0)], [(200, 0), (168.5, 0), (100, 0)])  # 一帧跨越身体
        self.assertAlmostEqual(contact, (100 - config.SNAKE_DIAMETER) / 200)  # 扫掠能捕捉第一次圆周接触
