"""输入、定时移动、碰撞结束及暂停控制器测试。"""  # 模块说明

import math  # 计算角度与距离
import os  # 无窗口测试环境
import unittest  # 标准库测试框架
from unittest.mock import patch  # 注入可重复的事件与时间

import pygame  # 图形库（只使用按键常量）

from greedy_snake import app, config  # 控制器与配置
from greedy_snake.layout import Layout  # 布局


class ControllerTestBase(unittest.TestCase):  # 控制器测试基类
    """创建带固定布局与控制器的测试环境。"""  # 类说明

    def setUp(self):  # 每个测试前创建控制器
        self.layout = Layout.default()  # 默认布局
        self.controller = app.Controller(self.layout, seed=1)  # 新控制器

    def press(self, key, now=0.0, character=""):  # 按下一个键
        """向控制器发送按键事件。"""  # 函数说明
        self.controller.handle_key(key, now, character)  # 交给控制器处理

    def click(self, position):  # 鼠标单击
        """向控制器发送鼠标单击事件。"""  # 函数说明
        self.controller.handle_click(position, 0.0)  # 交给控制器处理


class KeyFlowTests(ControllerTestBase):  # 键盘流程测试
    """验证开始、暂停、继续与退出。"""  # 类说明

    def test_any_key_starts_game(self):  # 开始界面按任意键进入游戏
        self.press(pygame.K_SPACE)  # 按空格
        self.assertEqual(self.controller.screen, "game")  # 进入游戏画面

    def test_double_p_pauses(self):  # 连按两次 P 暂停
        self.press(pygame.K_SPACE)  # 开始游戏
        self.press(pygame.K_p, now=0.0)  # 第一次按 P
        self.assertEqual(self.controller.screen, "game")  # 第一次不暂停
        self.press(pygame.K_p, now=0.2)  # 第二次按 P（窗口内）
        self.assertEqual(self.controller.screen, "pause")  # 触发暂停

    def test_single_p_does_not_pause(self):  # 单次 P 不会误触发暂停
        self.press(pygame.K_SPACE)  # 开始游戏
        self.press(pygame.K_p, now=0.0)  # 只按一次 P
        self.press(pygame.K_p, now=2.0)  # 超时后再次单按
        self.assertEqual(self.controller.screen, "game")  # 仍为游戏画面

    def test_p_pauses_and_single_p_resumes(self):  # 连按两次暂停、按一次继续
        self.press(pygame.K_SPACE)  # 开始游戏
        self.press(pygame.K_p, now=0.0)  # 第一次 P
        self.press(pygame.K_p, now=0.1)  # 第二次 P 暂停
        self.press(pygame.K_p, now=0.2)  # 按一次 P 继续
        self.assertEqual(self.controller.screen, "game")  # 回到游戏画面

    def test_pause_r_restarts(self):  # 暂停界面按 R 重试
        self.press(pygame.K_SPACE)  # 开始游戏
        self.press(pygame.K_p, now=0.0)  # 第一次 P
        self.press(pygame.K_p, now=0.1)  # 暂停
        old_state = self.controller.state  # 记录旧状态
        self.press(pygame.K_r)  # 按 R 重试
        self.assertEqual(self.controller.screen, "game")  # 回到游戏画面
        self.assertIsNot(self.controller.state, old_state)  # 生成了新状态

    def test_escape_quits(self):  # Esc 退出
        self.press(pygame.K_ESCAPE)  # 按 Esc
        self.assertTrue(self.controller.quit)  # 标记退出

    def test_preview_keys(self):  # 数字键切换预览界面
        for key, screen in ((pygame.K_1, "game"), (pygame.K_2, "start"),  # 1/2 切换
                            (pygame.K_3, "pause"), (pygame.K_4, "over")):  # 3/4 切换
            self.press(key)  # 按数字键
            self.assertEqual(self.controller.screen, screen)  # 界面正确


class MouseFlowTests(ControllerTestBase):  # 鼠标流程测试
    """验证单击暂停、继续、重试与退出。"""  # 类说明

    def test_click_starts_game(self):  # 开始界面单击开始
        self.click((600, 360))  # 单击任意位置
        self.assertEqual(self.controller.screen, "game")  # 进入游戏画面

    def test_click_toggles_pause(self):  # 游戏画面单击暂停，暂停界面单击继续
        self.click((600, 360))  # 开始游戏
        self.click((600, 360))  # 单击暂停
        self.assertEqual(self.controller.screen, "pause")  # 暂停
        self.click((600, 360))  # 再次单击继续
        self.assertEqual(self.controller.screen, "game")  # 继续游戏

    def test_pause_play_icon_resumes(self):  # 点击中间继续图标
        self.click((600, 360))  # 开始游戏
        self.click((600, 360))  # 暂停
        centers = self.layout.pause_icon_centers()  # 三个图标中心
        self.click(centers[1])  # 点击中间图标
        self.assertEqual(self.controller.screen, "game")  # 继续游戏

    def test_pause_exit_icon_quits(self):  # 点击左侧退出图标
        self.click((600, 360))  # 开始游戏
        self.click((600, 360))  # 暂停
        centers = self.layout.pause_icon_centers()  # 三个图标中心
        self.click(centers[0])  # 点击左侧图标
        self.assertTrue(self.controller.quit)  # 标记退出

    def test_pause_restart_icon_restarts(self):  # 点击右侧重试图标
        self.click((600, 360))  # 开始游戏
        self.click((600, 360))  # 暂停
        centers = self.layout.pause_icon_centers()  # 三个图标中心
        old_state = self.controller.state  # 记录旧状态
        self.click(centers[2])  # 点击右侧图标
        self.assertEqual(self.controller.screen, "game")  # 回到游戏画面
        self.assertIsNot(self.controller.state, old_state)  # 生成了新状态

    def test_over_click_retries(self):  # 结束界面单击重试
        self.press(pygame.K_4)  # 预览结束界面
        self.click((600, 360))  # 单击重试
        self.assertEqual(self.controller.screen, "game")  # 回到游戏画面


class MovementControlTests(ControllerTestBase):  # 连续运动控制测试
    """按键保持、松开、暂停和每帧运动的完整行为。"""  # 类说明

    def setUp(self):  # 设置独立状态
        super().setUp()  # 创建控制器
        self.controller.state.food = (1000, 600)  # 测试路径之外的食物

    def run_frames(self, first, count):  # 按真实帧间隔更新
        """从指定时刻连续执行 count 个 120 FPS 更新。"""  # 函数说明
        for index in range(count):  # 逐帧模拟
            self.controller.update(first + index / 120)  # 按真实时间推进

    def test_wasd_case_shift_and_release(self):  # 事件大小写不会留下卡住的方向
        for name, direction in (("w", (0, -1)), ("a", (-1, 0)), ("s", (0, 1)), ("d", (1, 0))):  # 四方向
            for character in (name, name.upper(), ""):  # 普通、Shift/Caps、无字符输入
                with self.subTest(name=name, character=character):  # 分别报告
                    self.controller = app.Controller(self.layout, seed=1)  # 新控制器
                    self.press(ord(name), character=character)  # 开始并保持方向键
                    self.assertEqual(self.controller.joystick_input(), direction)  # 按住才有偏移
                    self.assertEqual(self.controller.state.direction, (1, 0))  # 不在按下瞬间硬切航向
                    self.controller.handle_key_up(ord(name))  # 释放可能没有 Unicode 字符
                    self.assertEqual(self.controller.joystick_input(), (0, 0))  # 摇杆回中

    def test_diagonal_and_opposing_inputs(self):  # 多键像摇杆一样合成
        self.press(pygame.K_SPACE)  # 进入游戏
        self.press(pygame.K_w)  # 向上
        self.press(pygame.K_d)  # 同时向右
        self.assertAlmostEqual(self.controller.joystick_input()[0], math.sqrt(0.5))  # 归一化对角线横向
        self.assertAlmostEqual(self.controller.joystick_input()[1], -math.sqrt(0.5))  # 归一化对角线纵向
        self.press(pygame.K_a)  # 水平方向抵消
        self.assertEqual(self.controller.joystick_input(), (0, -1))  # 剩下向上
        self.press(pygame.K_s)  # 竖直方向也抵消
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 四键同时按不施力
        self.controller.handle_key_up(pygame.K_w)  # 释放上键
        self.assertEqual(self.controller.joystick_input(), (0, 1))  # 下键继续有效

    def test_repeated_keydown_does_not_accumulate_force(self):  # 系统键盘重复事件不叠加力度
        self.press(pygame.K_w)  # 按下 W
        for _ in range(10):  # 模拟重复事件
            self.press(pygame.K_w)  # 仍是同一个键
        self.assertEqual(self.controller.joystick_input(), (0, -1))  # 始终单位力度
        self.controller.handle_key_up(pygame.K_w)  # 一次释放
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 完全解除

    def test_smooth_motion_each_frame(self):  # 第一帧之后持续运动
        self.press(pygame.K_SPACE)  # 开始
        self.controller.update(0)  # 初始化时钟
        original = self.controller.state.snake[0]  # 初始位置
        self.controller.update(1 / 120)  # 一帧
        first = self.controller.state.snake[0]  # 第一次移动
        self.controller.update(2 / 120)  # 再一帧
        self.assertAlmostEqual(math.dist(original, first), config.SNAKE_SPEED / 120)  # 不再等待半秒
        self.assertAlmostEqual(math.dist(first, self.controller.state.snake[0]), config.SNAKE_SPEED / 120)  # 帧间连续

    def test_holding_turns_and_releasing_preserves_heading(self):  # 按住转弯，松开沿新方向走
        self.press(pygame.K_w, character="W")  # 以 W 开始
        self.run_frames(0, 16)  # 短暂转向
        direction = self.controller.state.direction  # 松开时的方向
        self.assertLess(direction[1], 0)  # 已向上弯曲
        self.assertGreater(direction[0], 0)  # 尚未达到正上方
        self.controller.handle_key_up(pygame.K_w)  # 松开
        self.run_frames(16 / 120, 20)  # 继续走
        self.assertAlmostEqual(self.controller.state.direction[0], direction[0])  # 保留水平分量
        self.assertAlmostEqual(self.controller.state.direction[1], direction[1])  # 保留垂直分量
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 显示的摇杆已经居中

    def test_long_frame_has_bounded_travel(self):  # 暂时卡顿不导致瞬移
        self.press(pygame.K_SPACE)  # 开始
        self.controller.update(0)  # 初始化时钟
        head = self.controller.state.snake[0]  # 初始位置
        self.controller.update(10)  # 模拟卡顿
        self.assertAlmostEqual(math.dist(head, self.controller.state.snake[0]), config.SNAKE_SPEED * config.MAX_FRAME_DT)  # 限制最大补算时间

    def test_non_game_states_freeze(self):  # 开始、暂停、结束保持静止
        for key in (pygame.K_2, pygame.K_3, pygame.K_4):  # 预览不同界面
            self.press(key)  # 切换
            before = self.controller.state.snake.copy()  # 保存位置
            self.controller.update(0)  # 首帧
            self.controller.update(100)  # 等待较长时间
            self.assertEqual(self.controller.state.snake, before)  # 不移动
            self.assertEqual(self.controller.joystick_input(), (0, 0))  # 摇杆不偏移

    def test_pause_key_release_and_resume_without_catchup(self):  # 暂停期间释放键不会卡住
        self.press(pygame.K_w)  # 开始并向上施力
        self.run_frames(0, 10)  # 先走一小段
        self.press(pygame.K_p, 0.1)  # 第一次 P
        self.press(pygame.K_p, 0.2)  # 第二次 P 暂停
        before = self.controller.state.snake.copy()  # 暂停位置
        self.controller.handle_key_up(pygame.K_w)  # 在暂停期间释放方向键
        self.controller.update(20)  # 等待很久
        self.assertEqual(self.controller.state.snake, before)  # 保持静止
        self.press(pygame.K_p, 20)  # 恢复
        self.controller.update(20)  # 恢复首帧不补走
        self.assertEqual(self.controller.state.snake, before)  # 没有瞬移
        self.controller.update(20 + 1 / 120)  # 下一帧
        self.assertGreater(math.dist(before[0], self.controller.state.snake[0]), 0)  # 立即恢复连续运动
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 松开的方向不残留

    def test_mouse_pause_resume_in_same_frame_resets_clock(self):  # 快速鼠标操作也不会补走
        self.click((600, 360))  # 开始
        self.controller.update(0)  # 初始化时钟
        before = self.controller.state.snake.copy()  # 保存位置
        self.click((600, 360))  # 暂停
        self.click((600, 360))  # 同一帧内又恢复
        self.controller.update(30)  # 下一帧
        self.assertEqual(self.controller.state.snake, before)  # 重新计时

    def test_key_held_during_pause_takes_effect_on_resume(self):  # 暂停期间仍正确记录按住的键
        self.press(pygame.K_SPACE)  # 开始
        self.click((600, 360))  # 暂停
        self.press(pygame.K_s)  # 暂停期间按住 S
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 暂停画面不施力
        self.press(pygame.K_p)  # 恢复
        self.assertEqual(self.controller.joystick_input(), (0, 1))  # 恢复时仍按住则向下施力
        self.controller.handle_key_up(pygame.K_s)  # 松开
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 摇杆回中

    def test_lost_focus_clears_held_keys(self):  # 切出窗口不能留下持续转向
        self.press(pygame.K_w)  # 按住方向键
        self.run_frames(0, 10)  # 开始转向
        before = self.controller.state.snake.copy()  # 保存位置
        self.controller.lose_focus()  # 切出窗口
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 摇杆回中
        self.controller.update(20)  # 恢复时重新计时
        self.assertEqual(self.controller.state.snake, before)  # 不补算失去焦点期间

    def test_wall_contact_ends_game_and_freezes_contact_frame(self):  # 停在墙边而非提前一格
        self.press(pygame.K_SPACE)  # 开始
        self.controller.update(0)  # 初始化时间
        self.run_frames(1 / 120, 600)  # 持续走向右墙
        self.assertEqual(self.controller.screen, "over")  # 自动失败
        self.assertAlmostEqual(self.controller.state.snake[0][0] + config.SNAKE_RADIUS, self.layout.interior.right + 1)  # 刚好接触
        before = self.controller.state.snake.copy()  # 终局位置
        self.controller.update(100)  # 结束后继续刷新
        self.assertEqual(self.controller.state.snake, before)  # 保持接触帧

    def test_retry_resets_score_size_input_and_clock(self):  # 重试恢复新的一局
        self.controller.state.food = (635, 364)  # 放置可吃食物
        self.press(pygame.K_SPACE)  # 开始
        self.run_frames(0, 30)  # 吃到食物
        self.assertEqual(self.controller.state.score, 1)  # 确实获得了分数
        self.press(pygame.K_w)  # 设置旧局输入
        self.press(pygame.K_4)  # 结束预览
        self.press(pygame.K_r, character="R")  # 重试
        self.assertEqual(self.controller.state.score, 0)  # 清零分数
        self.assertEqual(len(self.controller.state.snake), 2)  # 恢复初始长度
        self.assertEqual(self.controller.state.direction, (1, 0))  # 恢复航向
        self.assertEqual(self.controller.joystick_input(), (0, 0))  # 没有旧按键
        self.controller.update(100)  # 新一局第一帧
        self.assertEqual(self.controller.state.snake[0], (600, 364))  # 不立即跳跃


class MainLoopTests(unittest.TestCase):  # 实际 pygame 事件循环集成
    """真实事件队列、物理、绘制及 KEYUP 都要接入主循环。"""  # 类说明

    def test_real_loop_movement_food_turn_release_and_pause(self):  # 完整交互链路
        controller = app.Controller(Layout.default(), seed=7)  # 使用真实控制器
        controller.state.food = (635, 364)  # 可确定的首个食物
        original_get, original_render = pygame.event.get, app.screens.render  # 保留真实事件和绘制
        frames = []  # 每帧实际状态
        clock_time = [0.0]  # 可重复的时间源
        frame_index = [-1]  # 模拟帧索引
        events = {0: (pygame.KEYDOWN, pygame.K_SPACE, " "),  # 开始
                  40: (pygame.KEYDOWN, pygame.K_w, "W"), 50: (pygame.KEYUP, pygame.K_w, ""),  # 短暂转向再释放
                  70: (pygame.KEYDOWN, pygame.K_p, "p"), 71: (pygame.KEYDOWN, pygame.K_p, "P"),  # 暂停
                  90: (pygame.KEYDOWN, pygame.K_p, "p")}  # 恢复

        def feed_events():  # 将合成输入送入真实 pygame 队列
            frame_index[0] += 1  # 新帧
            index = frame_index[0]  # 本帧索引
            clock_time[0] = index / 120  # 时间由帧索引决定
            if index in events:  # 这一帧有输入
                kind, key, character = events[index]  # 读取输入
                pygame.event.post(pygame.event.Event(kind, key=key, unicode=character))  # 投递实际事件
            if index == 100:  # 测试结束
                pygame.event.post(pygame.event.Event(pygame.QUIT))  # 正常退出窗口
            return original_get()  # 真实队列取出事件

        def capture(screen, state, layout, joystick):  # 记录真实渲染过程
            frames.append((screen, state.snake.copy(), state.direction, state.score, joystick))  # 保存观察结果
            return original_render(screen, state, layout, joystick)  # 使用实际绘图

        with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), patch.object(app, "Controller", return_value=controller), patch.object(pygame.event, "get", side_effect=feed_events), patch.object(app.time, "monotonic", side_effect=lambda: clock_time[0]), patch.object(pygame.time, "Clock"), patch.object(app.screens, "render", side_effect=capture):  # 仅替换外部输入和时钟
            app.run(seed=7)  # 实际创建窗口、处理事件、推进并渲染
        self.assertGreater(frames[1][1][0][0], frames[0][1][0][0])  # 每帧前进
        self.assertEqual(frames[39][3], 1)  # 吃食物与计分已接通
        self.assertEqual(len(frames[39][1]), 3)  # 增长已接通
        self.assertEqual(frames[40][4], (0, -1))  # 按住方向偏移
        self.assertEqual(frames[50][4], (0, 0))  # KEYUP 让摇杆回中
        self.assertEqual(frames[51][2], frames[69][2])  # 松开保持航向
        self.assertEqual(frames[71][0], "pause")  # 双 P 暂停
        self.assertEqual(frames[71], frames[89])  # 暂停期间完全冻结
        self.assertEqual(frames[90][1], frames[89][1])  # 恢复首帧不补走
        self.assertNotEqual(frames[91][1], frames[90][1])  # 下一帧立即继续
        self.assertFalse(pygame.get_init())  # 退出后清理图形库
