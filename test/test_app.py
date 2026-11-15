"""界面与暂停触发控制器逻辑测试（不打开窗口）。"""  # 模块说明

import unittest  # 标准库测试框架

import pygame  # 图形库（只使用按键常量）

from greedy_snake import app, config  # 控制器与配置
from greedy_snake.layout import Layout  # 布局
from greedy_snake.state import create_initial_state  # 初始状态


class ControllerTestBase(unittest.TestCase):  # 控制器测试基类
    """创建带固定布局与控制器的测试环境。"""  # 类说明

    def setUp(self):  # 每个测试前创建控制器
        self.layout = Layout.default()  # 默认布局
        self.controller = app.Controller(self.layout, seed=1)  # 新控制器

    def press(self, key, now=0.0):  # 按下一个键
        """向控制器发送按键事件。"""  # 函数说明
        self.controller.handle_key(key, now)  # 交给控制器处理

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
