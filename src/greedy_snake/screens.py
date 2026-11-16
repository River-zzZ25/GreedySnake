"""四类界面渲染：连续蛇运动、虚拟摇杆、开始、暂停和结束。"""  # 模块说明

import math  # 计算重试图标的箭头方向

import pygame  # 图形库

from . import config, graphics  # 配置与图形绘制
from .layout import Layout, Rect  # 布局矩形
from .state import GameState  # 游戏状态

PANEL_RADIUS = 20  # 弹窗圆角半径


def _to_pygame_rect(rect: Rect) -> pygame.Rect:  # 转换为 pygame 矩形
    """把自定义 Rect 转成 pygame.Rect。"""  # 函数说明
    return pygame.Rect(rect.left, rect.top, rect.width, rect.height)  # 构造 pygame 矩形


def _draw_board(surface: pygame.Surface, layout: Layout) -> None:  # 绘制棋盘
    """绘制灰色实心墙体与内部深色可活动区域。"""  # 函数说明
    pygame.draw.rect(surface, config.COLOR_WALL, _to_pygame_rect(layout.board))  # 整块灰色墙体
    pygame.draw.rect(surface, config.COLOR_BOARD, _to_pygame_rect(layout.interior))  # 内部深色区域


def _draw_snake(surface: pygame.Surface, state: GameState) -> None:  # 绘制蛇
    """绘制蓝色蛇头、黄色蛇身的实心圆，并把相邻圆形的重叠区域颜色加深。"""  # 函数说明
    centers = state.snake  # 蛇的圆心列表
    colors = [config.COLOR_HEAD] + [config.COLOR_BODY] * (len(centers) - 1)  # 蛇头蓝色、其余黄色
    for (cx, cy), color in zip(centers, colors):  # 逐节绘制圆形
        graphics.draw_circle(surface, (cx, cy), config.SNAKE_RADIUS, color)  # 抗锯齿实心圆
    for first in range(len(centers)):  # 遍历所有圆形对
        for second in range(first + 1, len(centers)):  # 只与后面的圆形比较
            lens = graphics.lens_polygon(centers[first], centers[second], config.SNAKE_RADIUS)  # 计算重叠透镜
            if lens:  # 两个圆确实重叠
                overlap_color = graphics.darken(colors[first], config.DARKEN_FACTOR)  # 重叠处用前一个圆的加深色
                graphics.draw_polygon(surface, lens, overlap_color)  # 绘制加深的重叠区域


def _draw_food(surface: pygame.Surface, state: GameState) -> None:  # 绘制食物
    """以连续中心坐标绘制绿色空心正方形食物。"""  # 函数说明
    if state.food is None:  # 没有可放食物的空间
        return  # 不绘制占据身体的兜底食物
    cx, cy = state.food  # 食物中心
    rect = (cx - config.FOOD_SIDE / 2, cy - config.FOOD_SIDE / 2,  # 对齐实际中心而不取整
            config.FOOD_SIDE, config.FOOD_SIDE)  # 与碰撞检测相同的外边界
    graphics.draw_hollow_square(surface, rect, config.COLOR_FOOD, config.FOOD_OUTLINE)  # 只画边框，形成空心


def _draw_header(surface: pygame.Surface, layout: Layout, state: GameState) -> None:  # 绘制顶部信息
    """绘制顶部青色标题与右上角白色分数（不再显示左上角暂停图标）。"""  # 函数说明
    graphics.draw_text(surface, config.TITLE_TEXT, config.TITLE_FONT_SIZE, config.COLOR_TITLE,  # 标题居中
                       center=(layout.window[0] // 2, layout.header.height // 2))  # 标题居中
    graphics.draw_text(surface, f"得分：{state.score}", config.SCORE_FONT_SIZE, config.COLOR_TEXT,  # 分数右上角
                       topright=(layout.window[0] - config.MARGIN, 16))  # 右上角白色分数


def _draw_footer(surface: pygame.Surface, layout: Layout, text: str) -> None:  # 绘制底部指引
    """在底部居中绘制操作指引。"""  # 函数说明
    graphics.draw_text(surface, text, config.GUIDE_FONT_SIZE, config.COLOR_TEXT,  # 底部居中
                       center=(layout.window[0] // 2, layout.footer.top + layout.footer.height // 2))  # 居中指引


def _draw_veil(surface: pygame.Surface, layout: Layout, alpha: int) -> None:  # 绘制半透明遮罩
    """在棋盘区域盖上一层指定透明度的深色遮罩。"""  # 函数说明
    veil = pygame.Surface((layout.board.width, layout.board.height), pygame.SRCALPHA)  # 透明遮罩层
    veil.fill((*config.COLOR_VEIL, alpha))  # 填充带透明度的深色
    surface.blit(veil, (layout.board.left, layout.board.top))  # 盖上遮罩


def _draw_panel(surface: pygame.Surface, rect: Rect, alpha: int,  # 面板参数
                border_color: tuple[int, int, int]) -> None:  # 绘制半透明圆角面板
    """绘制带阴影、半透明底与彩色边框的圆角面板。"""  # 函数说明
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)  # 阴影层
    pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=PANEL_RADIUS)  # 圆角黑色阴影
    surface.blit(shadow, (rect.left + 8, rect.top + 10))  # 阴影向右下偏移
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)  # 面板层
    pygame.draw.rect(panel, (*config.COLOR_PANEL, alpha), panel.get_rect(),  # 半透明圆角底色
                     border_radius=PANEL_RADIUS)  # 半透明圆角底色
    pygame.draw.rect(panel, (*border_color, 220), panel.get_rect(), width=2,  # 彩色边框
                     border_radius=PANEL_RADIUS)  # 彩色边框
    surface.blit(panel, (rect.left, rect.top))  # 绘制到主画面


def _draw_exit_icon(surface: pygame.Surface, center: tuple[int, int],  # 图标中心与颜色
                    color: tuple[int, int, int]) -> None:  # 绘制退出图标
    """绘制“去掉右边竖线的口 + 指向门内的箭头”。"""  # 函数说明
    cx, cy = center  # 图标中心
    left, top = cx - 18, cy - 26  # 门框左上角
    box_width, box_height, thickness = 30, 52, 4  # 门框宽高与线宽
    pygame.draw.rect(surface, color, (left, top, box_width, thickness))  # 上门框
    pygame.draw.rect(surface, color, (left, top + box_height - thickness, box_width, thickness))  # 下门框
    pygame.draw.rect(surface, color, (left, top, thickness, box_height))  # 左门框（右边留空形成开口）
    shaft_y = cy  # 箭头纵坐标
    pygame.draw.rect(surface, color, (left + 8, shaft_y - 2, box_width + 22, 4))  # 从右侧伸入的箭杆
    graphics.draw_arrow_head(surface, (left + 8, shaft_y), (-1, 0), 12, color)  # 指向左侧门内的箭头


def _draw_play_icon(surface: pygame.Surface, center: tuple[int, int],  # 图标中心与颜色
                    color: tuple[int, int, int]) -> None:  # 绘制继续图标
    """绘制尖端向右的实心正三角形。"""  # 函数说明
    graphics.draw_triangle(surface, (center[0] + 24, center[1]), 30, 46, color)  # 实心向右三角形


def _draw_restart_icon(surface: pygame.Surface, center: tuple[int, int],  # 图标中心与颜色
                       color: tuple[int, int, int]) -> None:  # 绘制重试图标
    """绘制开口向左的圆形未闭合箭头。"""  # 函数说明
    radius, thickness = 26, 6  # 圆环半径与线宽
    graphics.draw_ring_arc(surface, center, radius, thickness, color, 210, 510, steps=100)  # 缺口在左侧的圆环
    end_angle = math.radians(150)  # 圆环下端（左下）角度
    end_point = (center[0] + radius * math.cos(end_angle),  # 箭头起点横坐标
                 center[1] + radius * math.sin(end_angle))  # 箭头起点纵坐标
    direction = (-math.sin(end_angle), math.cos(end_angle))  # 沿缺口方向的切线
    tip = (end_point[0] + direction[0] * 10, end_point[1] + direction[1] * 10)  # 箭头尖端
    graphics.draw_arrow_head(surface, tip, direction, 16, color)  # 指向左侧缺口的箭头


def _base_scene(layout: Layout, state: GameState, show_food: bool,  # 组装公共场景
                joystick: tuple[float, float] = (0.0, 0.0)) -> pygame.Surface:  # 可选摇杆输入
    """绘制背景、棋盘、蛇、可选食物、标题与分数。"""  # 函数说明
    surface = pygame.Surface(layout.window, pygame.SRCALPHA)  # 整窗画面
    surface.fill((*config.COLOR_BG, 255))  # 填充窗口背景
    _draw_board(surface, layout)  # 绘制墙体与内部背景
    _draw_snake(surface, state)  # 绘制蛇
    if show_food:  # 开始界面不显示食物位置
        _draw_food(surface, state)  # 绘制食物
    _draw_header(surface, layout, state)  # 绘制标题与分数
    if show_food:  # 游戏相关画面显示虚拟摇杆
        graphics.draw_joystick(surface, config.JOYSTICK_CENTER, config.JOYSTICK_BASE_RADIUS,  # 摇杆底座
                                config.JOYSTICK_KNOB_RADIUS, joystick, config.JOYSTICK_MAX_OFFSET,  # 摇杆偏移
                                config.COLOR_ACCENT, config.JOYSTICK_ALPHA)  # 摇杆颜色与透明度
    return surface  # 返回基础画面


def render_game(state: GameState, layout: Layout,  # 游戏画面
                joystick: tuple[float, float] = (0.0, 0.0)) -> pygame.Surface:  # 当前摇杆输入
    """返回运行中的游戏画面。"""  # 函数说明
    surface = _base_scene(layout, state, show_food=True, joystick=joystick)  # 基础场景
    _draw_footer(surface, layout, config.GUIDE_TEXT)  # 游戏操作指引
    return surface  # 返回画面


def render_start(state: GameState, layout: Layout) -> pygame.Surface:  # 开始界面
    """返回带开始面板、且不显示食物位置的开始界面。"""  # 函数说明
    surface = _base_scene(layout, state, show_food=False)  # 基础场景（隐藏食物）
    _draw_footer(surface, layout, "开始：按任意键开始游戏    Esc 退出")  # 开始界面指引
    panel = layout.start_panel_rect()  # 开始面板矩形
    _draw_panel(surface, panel, config.START_PANEL_ALPHA, config.COLOR_TITLE)  # 不透明青色边框面板
    graphics.draw_text(surface, config.TITLE_TEXT, config.PANEL_TITLE_FONT_SIZE + 8,  # 面板大标题
                       config.COLOR_TITLE, center=(panel.center[0], panel.top + 64))  # 大标题
    line_y = panel.top + 140  # 第一行正文纵坐标
    for line in config.START_LINES:  # 逐行绘制规则说明
        graphics.draw_text(surface, line, config.PANEL_TEXT_FONT_SIZE, config.COLOR_TEXT,  # 居中正文
                           center=(panel.center[0], line_y))  # 居中正文
        line_y += 40  # 行距
    graphics.draw_text(surface, config.START_HINT, config.PANEL_HINT_FONT_SIZE,  # 开始提示
                       config.COLOR_ACCENT, center=(panel.center[0], panel.bottom - 48))  # 开始提示
    return surface  # 返回画面


def render_pause(state: GameState, layout: Layout) -> pygame.Surface:  # 暂停界面
    """返回半透明遮罩 + 缩小一半的暂停面板与三个图标。"""  # 函数说明
    surface = _base_scene(layout, state, show_food=True, joystick=(0.0, 0.0))  # 保留游戏画面但固定摇杆中心
    _draw_veil(surface, layout, config.PAUSE_VEIL_ALPHA)  # 棋盘整体压暗
    panel = layout.pause_panel_rect()  # 暂停面板矩形（约为旧版一半）
    _draw_panel(surface, panel, config.PANEL_ALPHA, config.COLOR_TITLE)  # 半透明面板
    centers = layout.pause_icon_centers()  # 三个图标中心
    _draw_exit_icon(surface, centers[0], config.COLOR_TEXT)  # 左侧退出图标
    _draw_play_icon(surface, centers[1], config.COLOR_ACCENT)  # 中间实心向右三角形
    _draw_restart_icon(surface, centers[2], config.COLOR_TEXT)  # 右侧开口向左的圆形箭头
    for center, label in zip(centers, config.PAUSE_LABELS):  # 逐个绘制图标标签
        graphics.draw_text(surface, label, config.LABEL_FONT_SIZE, config.COLOR_DIM_TEXT,  # 图标标签
                           center=(center[0], center[1] + 50), shadow=True)  # 图标下方灰色小字
    _draw_footer(surface, layout, config.PAUSE_HINT)  # 暂停操作指引
    return surface  # 返回画面


def render_over(state: GameState, layout: Layout) -> pygame.Surface:  # 结束界面
    """返回保留蛇与食物最后位置的半透明结束界面。"""  # 函数说明
    surface = _base_scene(layout, state, show_food=True, joystick=(0.0, 0.0))  # 保留最后一帧的蛇和食物位置
    _draw_veil(surface, layout, config.OVER_VEIL_ALPHA)  # 轻微压暗，最后位置清晰可见
    panel = layout.over_panel_rect()  # 结束面板矩形
    _draw_panel(surface, panel, config.PANEL_ALPHA, config.COLOR_DANGER)  # 半透明红色边框面板
    graphics.draw_text(surface, "游戏结束", config.PANEL_TITLE_FONT_SIZE, config.COLOR_DANGER,  # 失败标题
                       center=(panel.center[0], panel.top + 64), shadow=True)  # 失败标题
    graphics.draw_text(surface, f"得分：{state.score}", 32, config.COLOR_BODY,  # 最终得分
                       center=(panel.center[0], panel.top + 128), shadow=True)  # 最终得分
    graphics.draw_text(surface, config.OVER_HINT, config.PANEL_HINT_FONT_SIZE, config.COLOR_TEXT,  # 重试提示
                       center=(panel.center[0], panel.bottom - 52), shadow=True)  # 重试与退出提示
    _draw_footer(surface, layout, "结束：R 重试    Esc 退出")  # 底部操作指引
    return surface  # 返回画面


BUILDERS = {  # 界面名到绘制函数的映射
    "game": render_game,  # 游戏画面
    "start": render_start,  # 开始界面
    "pause": render_pause,  # 暂停界面
    "over": render_over,  # 结束界面
}  # 界面映射结束


def render(screen: str, state: GameState, layout: Layout, joystick: tuple[float, float] = (0.0, 0.0)) -> pygame.Surface:  # 按名称渲染界面
    """根据界面名调用对应绘制函数。"""  # 函数说明
    if screen not in BUILDERS:  # 校验界面名
        raise ValueError(f"未知界面：{screen}")  # 抛出错误
    if screen == "game":  # 只有运行中的界面显示方向偏移
        return render_game(state, layout, joystick)  # 绘制当前按住的摇杆方向
    return BUILDERS[screen](state, layout)  # 其他界面使用居中的摇杆
