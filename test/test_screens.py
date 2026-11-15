"""四种界面布局单元测试（基于画布单元格断言）。"""  # 模块说明

import unittest  # 标准库测试框架

from greedy_snake import config, screens  # 配置与界面绘制
from greedy_snake.state import create_initial_state  # 初始游戏状态

STATE = create_initial_state(seed=2024)  # 固定种子，保证食物位置可复现


def find_cells(canvas, char):  # 查找字符所在的所有格子
    """返回画布中指定字符的 (x, y) 坐标列表。"""  # 函数说明
    return [  # 坐标列表
        (x, y)  # 匹配到的坐标
        for y in range(canvas.height)  # 遍历所有行
        for x in range(canvas.width)  # 遍历所有列
        if canvas.grid[y][x] is not None and canvas.grid[y][x][0] == char  # 字符匹配
    ]  # 返回坐标列表


class GameScreenTests(unittest.TestCase):  # 游戏画面测试
    """验证墙、蛇、食物、分数与操作指引。"""  # 类说明

    def setUp(self):  # 每个测试前生成游戏画面
        self.canvas = screens.render_game(STATE)  # 绘制游戏画面

    def test_wall_corners_gray(self):  # 四角是灰色实心方块
        for x, y in (  # 四个角的坐标
            (config.BOARD_LEFT, config.BOARD_TOP),  # 左上角
            (config.BOARD_LEFT + config.BOARD_WIDTH - 1, config.BOARD_TOP),  # 右上角
            (config.BOARD_LEFT, config.BOARD_TOP + config.BOARD_HEIGHT - 1),  # 左下角
            (config.BOARD_LEFT + config.BOARD_WIDTH - 1, config.BOARD_TOP + config.BOARD_HEIGHT - 1),  # 右下角
        ):
            self.assertEqual(self.canvas.grid[y][x], (config.WALL_CHAR, config.WALL_FG, config.WALL_BG))  # 颜色与字符检查

    def test_board_interior_black(self):  # 内部是可活动黑色空地
        x = config.INTERIOR_LEFT  # 内部第一列
        y = config.INTERIOR_TOP  # 内部第一行
        self.assertEqual(self.canvas.grid[y][x], (" ", "white", "black"))  # 黑底空格

    def test_snake_head_blue(self):  # 蛇头是蓝色实心方块
        head_x, head_y = STATE.cells[0]  # 蛇头坐标
        self.assertEqual(self.canvas.grid[head_y][head_x], (config.HEAD_CHAR, config.HEAD_FG, config.HEAD_BG))  # 蛇头颜色

    def test_snake_body_yellow(self):  # 蛇身是黄色实心方块
        body_x, body_y = STATE.cells[1]  # 蛇身坐标
        self.assertEqual(self.canvas.grid[body_y][body_x], (config.BODY_CHAR, config.BODY_FG, config.BODY_BG))  # 蛇身颜色

    def test_initial_length_is_two(self):  # 初始长度为头 + 一格身体
        self.assertEqual(len(STATE.cells), 2)  # 共两格

    def test_food_green_circle(self):  # 食物是绿色空心圆
        food_x, food_y = STATE.food  # 食物坐标
        self.assertEqual(self.canvas.grid[food_y][food_x], (config.FOOD_CHAR, config.FOOD_FG, "black"))  # 食物字符与颜色

    def test_food_not_on_snake(self):  # 食物不与蛇重叠
        self.assertNotIn(STATE.food, STATE.cells)  # 食物坐标不在蛇身上

    def test_score_white_top_right(self):  # 分数为白色且位于右上角
        score_text = f"得分：{STATE.score}"  # 期望的分数文本
        self.assertIn(score_text, self.canvas.row_text(0))  # 第一行包含分数文本
        last_col = config.BOARD_LEFT + config.BOARD_WIDTH - 1  # 棋盘右上角列
        self.assertEqual(self.canvas.grid[0][last_col][0], str(STATE.score))  # 末位数字贴住右上角
        self.assertEqual(self.canvas.grid[0][last_col][1], "white")  # 数字为白色

    def test_guide_text(self):  # 操作指引存在
        self.assertIn("操作指引", self.canvas.row_text(20))  # 第 20 行含操作指引
        self.assertIn("W/A/S/D", self.canvas.row_text(20))  # 含移动按键说明
        self.assertIn("暂停", self.canvas.row_text(20))  # 含暂停说明

    def test_preview_hint(self):  # 预览按键提示存在
        self.assertIn("预览", self.canvas.row_text(21))  # 第 21 行含预览提示


class StartScreenTests(unittest.TestCase):  # 开始界面测试
    """验证开始面板内容。"""  # 类说明

    def setUp(self):  # 每个测试前生成开始界面
        self.canvas = screens.render_start(STATE)  # 绘制开始界面

    def test_panel_title(self):  # 面板含游戏标题
        self.assertEqual(len(find_cells(self.canvas, "┌")), 1)  # 恰好一个面板
        self.assertIn("贪 吃 蛇", self.canvas.to_plain_text())  # 标题存在

    def test_start_hint(self):  # 含开始提示
        self.assertIn("按任意键开始", self.canvas.to_plain_text())  # 开始提示存在

    def test_rules_and_controls(self):  # 含规则与操作说明
        plain = self.canvas.to_plain_text()  # 纯文本画面
        self.assertIn("W / A / S / D", plain)  # 移动说明
        self.assertIn("撞墙或撞到自己", plain)  # 失败规则
        self.assertIn("鼠标点击", plain)  # 暂停触发说明


class PauseScreenTests(unittest.TestCase):  # 暂停界面测试
    """验证左上角暂停面板。"""  # 类说明

    def setUp(self):  # 每个测试前生成暂停界面
        self.canvas = screens.render_pause(STATE)  # 绘制暂停界面

    def test_panel_top_left(self):  # 暂停面板位于左上角
        x, y = screens.PAUSE_PANEL_X, screens.PAUSE_PANEL_Y  # 面板左上角坐标
        self.assertLess(x, 10)  # 横向靠近左侧
        self.assertLess(y, 5)  # 纵向靠近顶部
        self.assertEqual(self.canvas.grid[y][x][0], "┌")  # 面板左上角存在
        self.assertEqual(self.canvas.grid[y][x][1], config.TITLE_FG)  # 面板边框为青色

    def test_pause_text(self):  # 含暂停与继续说明
        plain = self.canvas.to_plain_text()  # 纯文本画面
        self.assertIn("已暂停", plain)  # 暂停状态文字
        self.assertIn("继续", plain)  # 继续方式说明
        self.assertIn("P", plain)  # P 键说明


class OverScreenTests(unittest.TestCase):  # 失败界面测试
    """验证失败面板与重试入口。"""  # 类说明

    def setUp(self):  # 每个测试前生成失败界面
        self.canvas = screens.render_over(STATE)  # 绘制失败界面

    def test_over_panel(self):  # 面板含失败标题与得分
        plain = self.canvas.to_plain_text()  # 纯文本画面
        self.assertIn("游戏结束", plain)  # 失败标题
        self.assertIn(f"得分：{STATE.score}", plain)  # 最终得分
        self.assertIn("R 重试", plain)  # 重试入口
        self.assertIn("Esc 退出", plain)  # 退出入口

    def test_over_border_red(self):  # 失败面板边框为红色
        panel_x = config.INTERIOR_LEFT + (config.INTERIOR_WIDTH - screens.OVER_PANEL_WIDTH) // 2  # 面板左边界
        panel_y = config.INTERIOR_TOP + (config.INTERIOR_HEIGHT - screens.OVER_PANEL_HEIGHT) // 2  # 面板上边界
        corners = [  # 面板四角坐标
            (panel_x, panel_y),  # 左上角
            (panel_x + screens.OVER_PANEL_WIDTH - 1, panel_y),  # 右上角
            (panel_x, panel_y + screens.OVER_PANEL_HEIGHT - 1),  # 左下角
            (panel_x + screens.OVER_PANEL_WIDTH - 1, panel_y + screens.OVER_PANEL_HEIGHT - 1),  # 右下角
        ]
        for x, y in corners:  # 逐一检查四角
            self.assertEqual(self.canvas.grid[y][x][1], config.DANGER_FG)  # 红色边框


class RenderDispatchTests(unittest.TestCase):  # 界面分发测试
    """验证界面名到绘制函数的映射。"""  # 类说明

    def test_render_game(self):  # 名称分发到游戏画面
        self.assertEqual(screens.render("game", STATE).to_plain_text(), screens.render_game(STATE).to_plain_text())  # 内容一致

    def test_unknown_screen(self):  # 未知界面名报错
        with self.assertRaises(ValueError):  # 应当抛出 ValueError
            screens.render("unknown", STATE)  # 调用未知界面
