"""绘制开始、游戏、暂停、结束四种静态界面（实现步骤 1）。"""  # 模块说明

from . import config  # 尺寸与颜色配置
from .canvas import Canvas, text_width  # 字符画布与文本宽度工具
from .state import GameState  # 游戏状态

TITLE_TEXT = "贪 吃 蛇"  # 顶部游戏标题
GUIDE_TEXT = "操作指引：W/A/S/D 移动    P / 鼠标点击 暂停    +1 分/食物"  # 棋盘下方操作指引
PREVIEW_HINT = "预览：1 游戏  2 开始  3 暂停  4 结束   P 暂停  R 重试  Esc 退出"  # 底部预览按键提示

PAUSE_PANEL_X = 1  # 暂停面板左上角列（要求显示在左上角）
PAUSE_PANEL_Y = 0  # 暂停面板左上角行
PAUSE_PANEL_WIDTH = 26  # 暂停面板宽度
PAUSE_PANEL_HEIGHT = 4  # 暂停面板高度
PAUSE_LINES = (  # 暂停面板文字内容
    ("已暂停", "yellow"),  # 第一行：暂停状态
    ("P / 鼠标点击 继续", "white"),  # 第二行：继续方式
)  # 暂停面板文字结束

START_PANEL_WIDTH = 38  # 开始面板宽度
START_PANEL_HEIGHT = 10  # 开始面板高度
START_LINES = (  # 开始面板文字内容（8 行 + 上下边框）
    ("贪 吃 蛇", "yellow"),  # 游戏标题
    ("", "white"),  # 空行
    ("W / A / S / D   移动小蛇", "white"),  # 移动操作说明
    ("吃到食物 +1 分，小蛇变长一格", "white"),  # 得分与成长规则
    ("撞墙或撞到自己，游戏结束", "white"),  # 失败规则
    ("P 键 / 鼠标点击   暂停", "white"),  # 暂停操作说明
    ("", "white"),  # 空行
    ("== 按任意键开始 ==", "cyan"),  # 开始提示
)  # 开始面板文字结束

OVER_PANEL_WIDTH = 34  # 失败面板宽度
OVER_PANEL_HEIGHT = 7  # 失败面板高度


def _new_canvas() -> Canvas:  # 创建空白画布
    """创建一块全黑背景的空白画布。"""  # 函数说明
    return Canvas()  # 使用配置中的默认尺寸


def _draw_title(canvas: Canvas) -> None:  # 绘制游戏标题
    """在棋盘上方居中绘制青色标题。"""  # 函数说明
    canvas.put_centered(config.BOARD_LEFT, config.BOARD_WIDTH, 0, TITLE_TEXT, fg=config.TITLE_FG)  # 居中写入标题


def _draw_score(canvas: Canvas, state: GameState) -> None:  # 绘制右上角分数
    """把白色分数文本右对齐到棋盘右上角。"""  # 函数说明
    text = f"得分：{state.score}"  # 组织分数文本
    x = config.BOARD_LEFT + config.BOARD_WIDTH - text_width(text)  # 计算右对齐起点列
    canvas.put_text(x, 0, text, fg="white")  # 用白色写入


def _draw_board(canvas: Canvas) -> None:  # 绘制墙体
    """用灰色实心方块画出矩形围墙，并把内部清成黑色。"""  # 函数说明
    canvas.fill_rect(config.BOARD_LEFT, config.BOARD_TOP, config.BOARD_WIDTH, config.BOARD_HEIGHT,  # 铺满整个棋盘外框
                     config.WALL_CHAR, config.WALL_FG, config.WALL_BG)  # 先铺满灰色实心方块
    canvas.fill_rect(config.INTERIOR_LEFT, config.INTERIOR_TOP, config.INTERIOR_WIDTH,  # 内部空地起点与宽度
                     config.INTERIOR_HEIGHT, " ", "white", "black")  # 再把内部挖成黑色空地


def _draw_snake(canvas: Canvas, state: GameState) -> None:  # 绘制蛇
    """蛇头用蓝色实心方块，蛇身用黄色实心方块。"""  # 函数说明
    for index, (x, y) in enumerate(state.cells):  # 遍历蛇头与每一节身体
        is_head = index == 0  # 第 0 格为蛇头
        char = config.HEAD_CHAR if is_head else config.BODY_CHAR  # 蛇头与身体使用实心方块字符
        fg = config.HEAD_FG if is_head else config.BODY_FG  # 蛇头蓝色、身体黄色
        bg = config.HEAD_BG if is_head else config.BODY_BG  # 背景与前景同色以填满整格
        canvas.fill_rect(x, y, 1, 1, char, fg, bg)  # 用实心方块填出一格


def _draw_food(canvas: Canvas, state: GameState) -> None:  # 绘制食物
    """食物用绿色空心圆形表示。"""  # 函数说明
    x, y = state.food  # 取出食物所在坐标
    canvas.put_text(x, y, config.FOOD_CHAR, fg=config.FOOD_FG)  # 写入绿色空心圆


def _draw_guide(canvas: Canvas) -> None:  # 绘制操作指引
    """在棋盘下方居中绘制白色操作指引。"""  # 函数说明
    canvas.put_centered(0, config.SCREEN_WIDTH, 20, GUIDE_TEXT, fg="white")  # 第 20 行居中显示


def _draw_preview_hint(canvas: Canvas) -> None:  # 绘制预览模式提示
    """在最底部绘制灰色预览按键说明。"""  # 函数说明
    canvas.put_centered(0, config.SCREEN_WIDTH, 21, PREVIEW_HINT, fg=config.HINT_FG)  # 第 21 行灰色居中


def _draw_panel(canvas: Canvas, x: int, y: int, width: int, height: int,  # 面板位置与尺寸
                border_fg: str = config.PANEL_FG) -> None:  # 绘制带边框的面板
    """清空面板区域并画出边框。"""  # 函数说明
    canvas.fill_rect(x, y, width, height, " ", "white", "black")  # 面板内部先铺黑底
    canvas.draw_border(x, y, width, height, fg=border_fg)  # 再画白色边框


def _put_panel_lines(canvas: Canvas, x: int, y: int, width: int,  # 面板位置与宽度
                     lines: tuple[tuple[str, str], ...]) -> None:  # 写面板文字
    """在面板内部逐行居中写入文字。"""  # 函数说明
    for offset, (text, fg) in enumerate(lines):  # 逐行遍历面板文字
        if not text:  # 空字符串只占一行，不写内容
            continue  # 跳过空行
        canvas.put_centered(x + 1, width - 2, y + 1 + offset, text, fg=fg)  # 在内容区居中写入


def _base_scene(state: GameState) -> Canvas:  # 组装公共场景
    """组装标题、分数、墙、蛇、食物、指引与预览提示。"""  # 函数说明
    canvas = _new_canvas()  # 新建画布
    _draw_title(canvas)  # 画标题
    _draw_score(canvas, state)  # 画右上角分数
    _draw_board(canvas)  # 画灰色墙
    _draw_snake(canvas, state)  # 画蛇
    _draw_food(canvas, state)  # 画食物
    _draw_guide(canvas)  # 画操作指引
    _draw_preview_hint(canvas)  # 画预览提示
    return canvas  # 返回组装完成的画布


def render_game(state: GameState) -> Canvas:  # 游戏进行中的界面
    """返回游戏画面（步骤 1 为静态展示）。"""  # 函数说明
    return _base_scene(state)  # 直接返回公共场景


def render_start(state: GameState) -> Canvas:  # 开始界面
    """返回带开始面板的界面。"""  # 函数说明
    canvas = _base_scene(state)  # 先画公共场景
    x = config.INTERIOR_LEFT + (config.INTERIOR_WIDTH - START_PANEL_WIDTH) // 2  # 水平居中
    y = config.INTERIOR_TOP + (config.INTERIOR_HEIGHT - START_PANEL_HEIGHT) // 2  # 垂直居中
    _draw_panel(canvas, x, y, START_PANEL_WIDTH, START_PANEL_HEIGHT, border_fg=config.TITLE_FG)  # 画青色边框面板
    _put_panel_lines(canvas, x, y, START_PANEL_WIDTH, START_LINES)  # 写入开始界面文字
    return canvas  # 返回画布


def render_pause(state: GameState) -> Canvas:  # 暂停界面
    """返回左上角显示暂停面板的界面。"""  # 函数说明
    canvas = _base_scene(state)  # 先画公共场景
    _draw_panel(canvas, PAUSE_PANEL_X, PAUSE_PANEL_Y, PAUSE_PANEL_WIDTH, PAUSE_PANEL_HEIGHT,  # 左上角暂停面板
                border_fg=config.TITLE_FG)  # 在左上角画暂停面板
    _put_panel_lines(canvas, PAUSE_PANEL_X, PAUSE_PANEL_Y, PAUSE_PANEL_WIDTH, PAUSE_LINES)  # 写入暂停文字
    return canvas  # 返回画布


def render_over(state: GameState) -> Canvas:  # 失败界面
    """返回居中显示失败面板与最终得分的界面。"""  # 函数说明
    canvas = _base_scene(state)  # 先画公共场景
    x = config.INTERIOR_LEFT + (config.INTERIOR_WIDTH - OVER_PANEL_WIDTH) // 2  # 水平居中
    y = config.INTERIOR_TOP + (config.INTERIOR_HEIGHT - OVER_PANEL_HEIGHT) // 2  # 垂直居中
    _draw_panel(canvas, x, y, OVER_PANEL_WIDTH, OVER_PANEL_HEIGHT, border_fg=config.DANGER_FG)  # 画红色边框面板
    lines = (  # 组装失败界面文字（含实时得分）
        ("游戏结束", config.DANGER_FG),  # 第一行：失败标题
        ("", "white"),  # 空行
        (f"得分：{state.score}", "yellow"),  # 最终得分
        ("", "white"),  # 空行
        ("R 重试    Esc 退出", "white"),  # 重试与退出操作说明
    )
    _put_panel_lines(canvas, x, y, OVER_PANEL_WIDTH, lines)  # 写入失败界面文字
    return canvas  # 返回画布


BUILDERS = {  # 界面名到绘制函数的映射
    "game": render_game,  # 游戏画面
    "start": render_start,  # 开始界面
    "pause": render_pause,  # 暂停界面
    "over": render_over,  # 失败界面
}  # 界面映射结束


def render(screen: str, state: GameState) -> Canvas:  # 按名称渲染界面
    """根据界面名调用对应绘制函数。"""  # 函数说明
    if screen not in BUILDERS:  # 校验界面名是否合法
        raise ValueError(f"未知界面：{screen}")  # 抛出明确错误
    return BUILDERS[screen](state)  # 调用对应绘制函数
