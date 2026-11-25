"""四类界面颜色与布局单元测试（离屏渲染，无需窗口）。"""  # 模块说明

import math  # 食物实色边框像素
import unittest  # 标准库测试框架

import pygame  # 图形库

from greedy_snake import config, graphics, screens  # 配置、图形与界面渲染
from greedy_snake.layout import Layout  # 布局
from greedy_snake.state import create_initial_state  # 初始状态

LAYOUT = Layout.default()  # 测试用默认布局
STATE = create_initial_state(LAYOUT, seed=7)  # 固定种子的初始状态


def pixel(surface, position):  # 取像素 RGB
    """返回像素的 RGB 三元组。"""  # 函数说明
    return tuple(surface.get_at(position)[:3])  # 只取 RGB


def count_color(surface, color, rect=None, threshold=2):  # 统计某颜色的像素数
    """统计画面或子区域中与颜色接近的像素数量。"""  # 函数说明
    target = surface if rect is None else surface.subsurface(rect)  # 选择统计区域
    mask = pygame.mask.from_threshold(target, (*color, 255), (threshold, threshold, threshold, 255))  # 颜色掩码
    return mask.count()  # 返回匹配像素数


class GameScreenTests(unittest.TestCase):  # 游戏画面测试
    """验证墙体、蛇、食物、分数与暂停图标。"""  # 类说明

    def setUp(self):  # 每个测试前渲染游戏画面
        self.surface = screens.render_game(STATE, LAYOUT)  # 游戏画面

    def test_window_size(self):  # 画面尺寸与窗口一致
        self.assertEqual(self.surface.get_size(), (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))  # 尺寸正确

    def test_wall_gray(self):  # 墙体为灰色实心区域
        self.assertEqual(pixel(self.surface, (LAYOUT.board.left + 4, LAYOUT.board.top + 4)),  # 左上角墙体颜色
                         config.COLOR_WALL)  # 左上角墙体

    def test_board_background(self):  # 内部为深色背景
        point = (LAYOUT.interior.left + 8, LAYOUT.interior.top + 8)  # 内部左上角附近
        self.assertEqual(pixel(self.surface, point), config.COLOR_BOARD)  # 深色背景

    def test_head_blue(self):  # 蛇头为蓝色实心圆
        self.assertEqual(pixel(self.surface, (int(STATE.snake[0][0]), int(STATE.snake[0][1]))),  # 蛇头圆心像素
                         config.COLOR_HEAD)  # 蛇头圆心颜色

    def test_body_yellow(self):  # 蛇身为黄色实心圆
        self.assertEqual(pixel(self.surface, (int(STATE.snake[1][0]), int(STATE.snake[1][1]))),  # 蛇身圆心像素
                         config.COLOR_BODY)  # 蛇身圆心颜色

    def test_overlap_darkened(self):  # 重叠区域颜色加深
        head, body = STATE.snake[0], STATE.snake[1]  # 蛇头与蛇身
        midpoint = (int((head[0] + body[0]) / 2), int(head[1]))  # 两圆心之间
        expected = graphics.darken(config.COLOR_HEAD, config.DARKEN_FACTOR)  # 计算期望加深色
        self.assertEqual(pixel(self.surface, midpoint), expected)  # 重叠处颜色加深

    def test_food_hollow_square(self):  # 食物为绿色空心正方形
        x, y = STATE.food  # 食物中心
        edge = (math.ceil(x - config.FOOD_SIDE / 2), round(y))  # 边框内部的实色像素
        self.assertEqual(pixel(self.surface, edge), config.COLOR_FOOD)  # 边框为绿色
        center = (round(x), round(y))  # 食物中心像素
        self.assertEqual(pixel(self.surface, center), config.COLOR_BOARD)  # 中心是空的

    def test_score_white_top_right(self):  # 分数为白色并位于右上角
        region = pygame.Rect(config.WINDOW_WIDTH - 180, 4, 170, 48)  # 右上角区域
        self.assertGreater(count_color(self.surface, config.COLOR_TEXT, region), 10)  # 存在白色文字像素

    def test_no_pause_icon_top_left(self):  # 左上角不再显示暂停图标
        region = pygame.Rect(0, 0, 300, config.HEADER_HEIGHT)  # 左上角区域
        self.assertEqual(count_color(self.surface, config.COLOR_BG, region), region.width * region.height)  # 全部是背景

    def test_guide_text_bottom(self):  # 底部有操作指引文字
        region = pygame.Rect(0, LAYOUT.footer.top, config.WINDOW_WIDTH, LAYOUT.footer.height)  # 底部区域
        self.assertGreater(count_color(self.surface, config.COLOR_TEXT, region), 20)  # 存在白色文字


    def test_energy_meter_is_visible(self):
        region = pygame.Rect(*config.ENERGY_BAR_RECT).inflate(30, 50)
        self.assertGreater(count_color(self.surface, config.COLOR_ENERGY, region), 100)

    def test_virtual_joystick_is_visible_only_in_joystick_mode(self):
        center = config.JOYSTICK_CENTER
        region = pygame.Rect(center[0] - 90, center[1] - 90, 180, 180)
        keyboard = screens.render_game(STATE, LAYOUT, input_mode="wasd")
        joystick = screens.render_game(STATE, LAYOUT, input_mode="joystick")
        self.assertNotEqual(pygame.image.tobytes(joystick.subsurface(region), "RGBA"),
                            pygame.image.tobytes(keyboard.subsurface(region), "RGBA"))


class StartScreenTests(unittest.TestCase):  # 开始界面测试
    """验证开始界面隐藏食物且显示规则面板。"""  # 类说明

    def setUp(self):  # 每个测试前渲染开始界面
        self.surface = screens.render_start(STATE, LAYOUT)  # 开始界面

    def test_no_food_before_start(self):  # 开始前不显示食物位置
        self.assertEqual(count_color(self.surface, config.COLOR_FOOD), 0)  # 画面中没有任何食物颜色像素

    def test_panel_present(self):  # 开始面板存在
        panel = LAYOUT.start_panel_rect()  # 开始面板矩形
        self.assertNotEqual(pixel(self.surface, (panel.center[0], panel.top + 4)),  # 面板填充像素
                            config.COLOR_BG)  # 面板填充色与背景不同

    def test_start_hint_text(self):  # 面板内有开始提示文字
        panel = LAYOUT.start_panel_rect()  # 开始面板矩形
        region = pygame.Rect(panel.left, panel.bottom - 80, panel.width, 60)  # 提示文字区域
        self.assertGreater(count_color(self.surface, config.COLOR_ACCENT, region, 80), 10)  # 青色提示文字


class MenuScreenTests(unittest.TestCase):
    """主页面设置入口与控制模式弹层。"""

    def test_settings_icon_is_in_top_right(self):
        surface = screens.render_menu(STATE, LAYOUT)
        rect = LAYOUT.settings_icon_rect()
        region = pygame.Rect(rect.left, rect.top, rect.width, rect.height)
        self.assertGreater(count_color(surface, config.COLOR_TITLE, region), 30)

    def test_settings_panel_shows_both_modes(self):
        surface = screens.render_menu(STATE, LAYOUT, input_mode="joystick",
                                      settings_open=True)
        for rect in LAYOUT.settings_mode_rects():
            region = pygame.Rect(rect.left, rect.top, rect.width, rect.height)
            self.assertGreater(count_color(surface, config.COLOR_TEXT, region), 10)


class HelpScreenTests(unittest.TestCase):
    """教程页包含单食物计分与新增能量说明。"""

    def test_scoring_page_uses_one_food_example(self):
        surface = screens.render_help(STATE, LAYOUT, page=2)
        self.assertLess(count_color(surface, config.COLOR_FOOD), 100)

    def test_last_help_page_explains_safe_body_contact(self):
        surface = screens.render_help(STATE, LAYOUT, page=3)
        self.assertGreater(count_color(surface, config.COLOR_ACCENT), 10)


class PauseScreenTests(unittest.TestCase):  # 暂停界面测试
    """验证暂停面板尺寸、三个图标与遮罩。"""  # 类说明

    def setUp(self):  # 每个测试前渲染暂停界面
        self.surface = screens.render_pause(STATE, LAYOUT)  # 暂停界面
        self.panel = LAYOUT.pause_panel_rect()  # 暂停面板
        self.centers = LAYOUT.pause_icon_centers()  # 三个图标中心

    def test_panel_half_size(self):  # 暂停面板为旧版一半大小
        self.assertEqual((self.panel.width, self.panel.height),  # 面板尺寸
                         (config.PAUSE_PANEL_WIDTH, config.PAUSE_PANEL_HEIGHT))  # 尺寸由配置决定

    def test_play_triangle_center(self):  # 中间为绿色实心三角形
        self.assertEqual(pixel(self.surface, self.centers[1]), config.COLOR_ACCENT)  # 中心像素为绿色

    def test_exit_icon_left(self):  # 左侧存在退出图标
        self.assertGreater(count_color(self.surface, config.COLOR_TEXT,  # 左侧白色像素
                                       pygame.Rect(self.centers[0][0] - 30, self.centers[0][1] - 30, 60, 60)), 20)  # 白色像素

    def test_restart_icon_right(self):  # 右侧存在圆形未闭合箭头
        self.assertGreater(count_color(self.surface, config.COLOR_TEXT,  # 右侧白色像素
                                       pygame.Rect(self.centers[2][0] - 32, self.centers[2][1] - 32, 64, 64)), 20)  # 白色像素

    def test_restart_opening_left(self):  # 重试箭头开口朝左
        center = self.centers[2]  # 重试图标中心
        left_point = (center[0] - 26, center[1])  # 圆环正左方
        right_point = (center[0] + 26, center[1])  # 圆环正右方
        self.assertNotEqual(pixel(self.surface, left_point), config.COLOR_TEXT)  # 左侧是缺口
        self.assertEqual(pixel(self.surface, right_point), config.COLOR_TEXT)  # 右侧是圆环

    def test_board_dimmed(self):  # 暂停时棋盘被压暗
        point = (LAYOUT.board.left + 4, LAYOUT.board.top + 4)  # 墙体像素
        self.assertNotEqual(pixel(self.surface, point), config.COLOR_WALL)  # 墙色被遮罩压暗

    def test_no_pause_icon_top_left(self):  # 暂停界面左上角没有暂停图标
        region = pygame.Rect(0, 0, 300, config.HEADER_HEIGHT)  # 左上角区域
        self.assertEqual(count_color(self.surface, config.COLOR_BG, region), region.width * region.height)  # 全部背景


class OverScreenTests(unittest.TestCase):  # 结束界面测试
    """验证结束界面保留蛇与食物最后位置且半透明。"""  # 类说明

    def setUp(self):  # 每个测试前渲染结束界面
        self.surface = screens.render_over(STATE, LAYOUT)  # 结束界面
        self.panel = LAYOUT.over_panel_rect()  # 结束面板

    def test_final_snake_visible(self):  # 蛇头最后位置仍可见（被遮罩压暗但未消失）
        point = (int(STATE.snake[0][0]), int(STATE.snake[0][1]))  # 蛇头圆心
        color = pixel(self.surface, point)  # 当前像素
        self.assertNotEqual(color, config.COLOR_HEAD)  # 已被半透明遮罩处理
        self.assertNotEqual(color, config.COLOR_BG)  # 不是纯背景，仍能看到蛇头位置

    def test_final_food_visible(self):  # 食物最后位置仍可见
        x, y = STATE.food  # 食物中心
        color = pixel(self.surface, (math.ceil(x - config.FOOD_SIDE / 2), round(y)))  # 食物边框像素
        self.assertNotEqual(color, config.COLOR_FOOD)  # 已被半透明遮罩处理
        self.assertNotEqual(color, config.COLOR_BG)  # 不是纯背景

    def test_panel_present(self):  # 结束面板存在
        self.assertNotEqual(pixel(self.surface, (self.panel.center[0], self.panel.top + 4)),  # 结束面板填充像素
                            config.COLOR_BG)  # 面板填充色与背景不同

    def test_title_text(self):  # 存在红色“游戏结束”文字
        region = pygame.Rect(self.panel.left, self.panel.top + 30, self.panel.width, 70)  # 标题区域
        self.assertGreater(count_color(self.surface, config.COLOR_DANGER, region, 60), 10)  # 红色文字像素


class RenderDispatchTests(unittest.TestCase):  # 界面分发测试
    """验证界面名到绘制函数的映射。"""  # 类说明

    def test_render_game(self):  # 名称分发到游戏画面
        first = screens.render("game", STATE, LAYOUT)  # 按名称渲染
        second = screens.render_game(STATE, LAYOUT)  # 直接渲染
        self.assertEqual(first.get_size(), second.get_size())  # 尺寸一致

    def test_unknown_screen(self):  # 未知界面名报错
        with self.assertRaises(ValueError):  # 应当抛出 ValueError
            screens.render("unknown", STATE, LAYOUT)  # 调用未知界面
