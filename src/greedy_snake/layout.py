"""窗口布局：根据窗口尺寸计算棋盘、可活动区域与各类面板位置。"""  # 模块说明

from dataclasses import dataclass  # 数据类工具

from . import config  # 尺寸与比例常量


@dataclass(frozen=True)  # 不可变数据类
class Rect:  # 像素矩形区域
    """以像素为单位的矩形（left/top 与宽高）。"""  # 类说明

    left: int  # 左边界
    top: int  # 上边界
    width: int  # 宽度
    height: int  # 高度

    @property  # 只读属性
    def right(self) -> int:  # 右边界（含）
        """返回最右侧像素列。"""  # 函数说明
        return self.left + self.width - 1  # 左侧加宽度减一

    @property  # 只读属性
    def bottom(self) -> int:  # 下边界（含）
        """返回最下方像素行。"""  # 函数说明
        return self.top + self.height - 1  # 上侧加高度减一

    @property  # 只读属性
    def center(self) -> tuple[int, int]:  # 中心点
        """返回矩形中心坐标。"""  # 函数说明
        return self.left + self.width // 2, self.top + self.height // 2  # 中心横纵坐标

    def inset(self, amount: int) -> "Rect":  # 向内收缩
        """返回四边各向内收缩 amount 像素后的矩形。"""  # 函数说明
        return Rect(self.left + amount, self.top + amount,  # 收缩后的左上角
                    self.width - 2 * amount, self.height - 2 * amount)  # 收缩后的宽高

    def contains(self, point: tuple[int, int]) -> bool:  # 判断点是否在矩形内
        """判断一个屏幕坐标是否落在矩形范围内。"""  # 函数说明
        x, y = point  # 拆出坐标
        return self.left <= x <= self.right and self.top <= y <= self.bottom  # 边界包含判断


@dataclass(frozen=True)  # 不可变数据类
class Layout:  # 界面布局
    """保存窗口、棋盘、可活动区域与页眉页脚矩形。"""  # 类说明

    window: tuple[int, int]  # 窗口宽高
    board: Rect  # 含灰色墙体的棋盘矩形
    interior: Rect  # 蛇与食物可活动的内部矩形
    header: Rect  # 顶部标题/分数区域
    footer: Rect  # 底部操作指引区域

    @classmethod  # 类方法：默认布局
    def default(cls) -> "Layout":  # 默认布局
        """按配置中的窗口尺寸创建布局。"""  # 函数说明
        window = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)  # 窗口尺寸
        board = Rect(  # 棋盘外框
            config.MARGIN,  # 左边界
            config.HEADER_HEIGHT,  # 上边界
            config.WINDOW_WIDTH - 2 * config.MARGIN,  # 宽度
            config.WINDOW_HEIGHT - config.HEADER_HEIGHT - config.FOOTER_HEIGHT,  # 高度
        )  # 棋盘矩形结束
        interior = board.inset(config.WALL_THICKNESS)  # 内部可活动区域
        header = Rect(0, 0, config.WINDOW_WIDTH, config.HEADER_HEIGHT)  # 顶部区域
        footer = Rect(0, config.WINDOW_HEIGHT - config.FOOTER_HEIGHT,  # 底部区域矩形
                      config.WINDOW_WIDTH, config.FOOTER_HEIGHT)  # 底部区域
        return cls(window=window, board=board, interior=interior, header=header, footer=footer)  # 返回布局

    def centered_rect(self, width: int, height: int) -> Rect:  # 在棋盘内部居中的矩形
        """返回以可活动区域中心为中心、指定宽高的矩形。"""  # 函数说明
        cx, cy = self.interior.center  # 可活动区域中心
        return Rect(cx - width // 2, cy - height // 2, width, height)  # 居中矩形

    def pause_panel_rect(self) -> Rect:  # 暂停面板矩形
        """返回暂停面板矩形（边长约为旧版的一半）。"""  # 函数说明
        return self.centered_rect(config.PAUSE_PANEL_WIDTH, config.PAUSE_PANEL_HEIGHT)  # 居中面板

    def pause_icon_centers(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:  # 三个图标中心
        """返回（退出、继续、重试）三个图标中心坐标。"""  # 函数说明
        cx, cy = self.pause_panel_rect().center  # 面板中心
        return ((cx - config.PAUSE_ICON_SPACING, cy),  # 左侧退出图标
                (cx, cy),  # 中间继续图标
                (cx + config.PAUSE_ICON_SPACING, cy))  # 右侧重试图标

    def pause_icon_rects(self) -> tuple[Rect, Rect, Rect]:  # 三个图标点击区域
        """返回三个图标的鼠标判定矩形。"""  # 函数说明
        half = config.PAUSE_ICON_HIT // 2  # 判定区域半边长
        return tuple(  # 三个判定矩形
            Rect(cx - half, cy - half, config.PAUSE_ICON_HIT, config.PAUSE_ICON_HIT)  # 图标周围的正方形
            for cx, cy in self.pause_icon_centers()  # 遍历三个中心
        )  # 判定矩形列表结束

    def start_panel_rect(self) -> Rect:  # 开始面板矩形
        """返回开始面板矩形。"""  # 函数说明
        return self.centered_rect(config.START_PANEL_WIDTH, config.START_PANEL_HEIGHT)  # 居中面板

    def menu_button_rects(self) -> tuple[Rect, Rect, Rect]:  # 主页面三个按钮
        """返回开始游戏、帮助和退出按钮。"""
        panel = self.start_panel_rect()
        return tuple(
            Rect(panel.left + 120, panel.top + 140 + index * 58 - 22,
                 panel.width - 240, 44)
            for index in range(3)
        )

    def settings_icon_rect(self) -> Rect:  # 主页面右上角设置图标
        """返回设置图标的点击区域。"""
        return Rect(self.window[0] - 72, 8, 48, 48)

    def settings_panel_rect(self) -> Rect:  # 设置弹层
        """返回控制模式设置弹层。"""
        return Rect(self.window[0] - 304, 66, 264, 154)

    def settings_mode_rects(self) -> tuple[Rect, Rect]:
        """返回 WASD 与鼠标摇杆两个设置选项。"""
        panel = self.settings_panel_rect()
        return (Rect(panel.left + 18, panel.top + 48, panel.width - 36, 42),
                Rect(panel.left + 18, panel.top + 98, panel.width - 36, 42))

    def help_panel_rect(self) -> Rect:
        """返回帮助页固定面板。"""
        return self.centered_rect(820, 470)

    def over_panel_rect(self) -> Rect:  # 结束面板矩形
        """返回结束面板矩形。"""  # 函数说明
        return self.centered_rect(config.OVER_PANEL_WIDTH, config.OVER_PANEL_HEIGHT)  # 居中面板
