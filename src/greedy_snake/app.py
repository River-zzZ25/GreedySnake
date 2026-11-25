"""应用逻辑：连续物理更新、虚拟摇杆、暂停触发与鼠标交互。"""  # 模块说明

import math  # 合成多个按键的摇杆向量
import time  # 使用单调时钟控制连续运动与暂停触发

import pygame  # 图形库

from . import config, screens  # 配置与界面渲染
from .layout import Layout  # 布局
from .state import advance_state, create_initial_state  # 连续更新与初始状态

PREVIEW_KEYS = {  # 数字键预览界面（临时，便于验收）
    pygame.K_1: "game",  # 1：游戏画面
    pygame.K_2: "menu",  # 2：主页面
    pygame.K_3: "pause",  # 3：暂停界面
    pygame.K_4: "over",  # 4：结束界面
}  # 预览快捷键映射结束
DIRECTION_BY_NAME = {  # WASD 名称到摇杆方向的映射
    "w": (0.0, -1.0),  # W 向上施力
    "a": (-1.0, 0.0),  # A 向左施力
    "s": (0.0, 1.0),  # S 向下施力
    "d": (1.0, 0.0),  # D 向右施力
}  # 方向映射结束


def _key_name(key: int, character: str = "") -> str:  # 规范化按键名称
    """优先使用事件字符并忽略大小写，兼容大小写键盘输入。"""  # 函数说明
    physical = pygame.key.name(key).casefold()  # 字母键的物理键名不受 Shift/Caps Lock 影响
    if physical in DIRECTION_BY_NAME:  # 按下和释放均采用稳定的键名
        return physical  # 避免松开 Shift 后无法释放旧的方向输入
    if len(character) == 1 and character.isalpha():  # 事件包含单个字母字符
        return character.casefold()  # 统一转为小写
    return pygame.key.name(key).casefold()  # 使用 pygame 按键名并统一大小写


class Controller:  # 游戏界面与输入控制器
    """管理连续蛇状态、按住的 WASD、界面状态与暂停流程。"""  # 类说明

    def __init__(self, layout: Layout, seed: int | None = None):  # 构造控制器
        self.layout = layout  # 布局
        self.state = create_initial_state(layout, seed)  # 初始游戏状态
        self.screen = "menu"  # 默认显示主页面
        self.help_page = 0
        self.last_press_time: float | None = None  # 上一次空格按下时间
        self.last_update_time: float | None = None  # 上一次物理更新的时间
        self.held_keys: set[str] = set()  # 当前仍按住的 WASD
        self.mouse_joystick = (0.0, 0.0)
        self.input_mode = "wasd"  # 默认键盘控制，可在主页面设置中切换
        self.settings_open = False
        self.boost_requested = False
        self.quit = False  # 是否退出程序

    def reset(self) -> None:  # 重新开始
        """重置游戏状态并进入游戏画面。"""  # 函数说明
        self.state = create_initial_state(self.layout)  # 新的一局不沿用旧随机状态
        self.screen = "game"  # 切换到游戏画面
        self.last_press_time = None  # 重置暂停计时
        self.last_update_time = None  # 从当前时刻重新计时
        self.held_keys.clear()  # 清除上一局残留按键
        self.mouse_joystick = (0.0, 0.0)
        self.settings_open = False
        self.boost_requested = False

    def handle_key(self, key: int, now: float, character: str = "") -> None:  # 处理按键按下
        """按当前界面处理按键，并记录按住的 WASD 施力。"""  # 函数说明
        name = _key_name(key, character)  # 统一按键名称与大小写
        direction = DIRECTION_BY_NAME.get(name)  # 判断是否为方向键
        if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.boost_requested = self.screen == "game"
            return
        if key == pygame.K_ESCAPE or name == "q":
            if self.settings_open:
                self.settings_open = False
                return
            if self.screen in {"game", "pause", "over", "help"}:
                self.screen = "menu"
                self.last_update_time = None
                self.held_keys.clear()
                self.boost_requested = False
            else:
                self.quit = True
            return  # 结束处理
        if key in PREVIEW_KEYS:  # 数字键切换预览界面
            self.screen = PREVIEW_KEYS[key]  # 更新界面
            self.last_press_time = None  # 重置暂停计时
            self.last_update_time = None  # 重置物理计时
            self.held_keys.clear()  # 预览切换不保留摇杆输入
            return  # 结束处理
        if self.screen == "menu":
            if key == pygame.K_h:
                self.screen, self.help_page = "help", 0
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.screen = "game"
                self.last_update_time = None
            return
        if self.screen == "help":
            if key in (pygame.K_LEFT, pygame.K_a):
                self.help_page = max(0, self.help_page - 1)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.help_page = min(config.HELP_PAGE_COUNT - 1, self.help_page + 1)
            elif key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.screen = "menu"
            return
        if self.screen == "start":  # 开始界面按任意键开始
            if direction is not None:  # 若开始键本身是 WASD
                self.held_keys.add(name)  # 从开始这一帧起显示摇杆偏移
            self.screen = "game"  # 进入游戏画面
            self.last_press_time = None  # 重置暂停计时
            self.last_update_time = None  # 从进入游戏时开始计时
        elif self.screen == "game":  # 游戏画面处理方向与暂停
            if direction is not None:  # 按下 W/A/S/D
                self.held_keys.add(name)  # 持续施力直到收到 KEYUP
            elif key == pygame.K_SPACE:
                if (self.last_press_time is not None  # 已经按过一次空格
                        and now - self.last_press_time <= config.PAUSE_DOUBLE_WINDOW):  # 距上次足够近
                    self.screen = "pause"  # 连按两次才暂停
                    self.last_press_time = None  # 重置暂停计时
                    self.last_update_time = None  # 暂停期间不积累时间
                else:  # 第一次按空格
                    self.last_press_time = now  # 记录本次时间
        elif self.screen == "pause":  # 暂停界面按键
            if direction is not None:  # 记录暂停期间新按住的方向键
                self.held_keys.add(name)  # 恢复时仍按住才施力，KEYUP 会正常清除
            elif key == pygame.K_SPACE:
                if self.last_press_time is not None and now - self.last_press_time <= config.PAUSE_DOUBLE_WINDOW:
                    self.screen = "game"
                    self.last_press_time = None
                    self.last_update_time = None
                else:
                    self.last_press_time = now
            elif name == "r":  # 按 R 重试
                self.reset()  # 重开一局
        elif self.screen == "over":  # 结束界面按键
            if name == "r":  # 按 R 重试
                self.reset()  # 重开一局

    def handle_key_up(self, key: int, character: str = "") -> None:  # 处理按键释放
        """释放 WASD 后停止对应施力，使虚拟摇杆回到中心。"""  # 函数说明
        if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.boost_requested = False
            return
        name = _key_name(key, character)  # 统一按键名称
        if name in DIRECTION_BY_NAME:  # 仅处理方向键释放
            self.held_keys.discard(name)  # 清除持续施力

    def joystick_input(self) -> tuple[float, float]:  # 获取当前摇杆向量
        """合成当前按住的 WASD，返回归一化后的摇杆偏移方向。"""  # 函数说明
        if self.screen != "game":  # 暂停或结束时摇杆居中
            return (0.0, 0.0)  # 非游戏界面不施力
        if self.input_mode == "joystick":
            return self.mouse_joystick
        x = sum(DIRECTION_BY_NAME[name][0] for name in self.held_keys)  # 合成横向输入
        y = sum(DIRECTION_BY_NAME[name][1] for name in self.held_keys)  # 合成纵向输入
        length = math.hypot(x, y)  # 计算合成向量长度
        if length <= 1e-9:  # 没有按住方向键
            return (0.0, 0.0)  # 摇杆保持中心
        return (x / length, y / length)  # 对角线输入保持统一施力强度

    def lose_focus(self) -> None:  # 窗口失去焦点
        """清除可能在其他窗口释放的按键，防止回来后持续转弯。"""  # 函数说明
        self.held_keys.clear()  # 清除方向输入
        self.mouse_joystick = (0.0, 0.0)
        self.boost_requested = False
        self.last_update_time = None  # 恢复时不积累离开期间的时间
        self.last_press_time = None  # 丢弃旧暂停按键时间

    def update(self, now: float) -> None:  # 根据时间推进连续物理
        """按真实时间平滑移动蛇，并在几何碰撞时进入结束界面。"""  # 函数说明
        if self.screen != "game":  # 非游戏状态不推进蛇
            self.last_update_time = None  # 清除计时，防止暂停后补走
            return  # 保持当前状态
        if self.last_update_time is None:  # 刚进入游戏或从暂停恢复
            self.last_update_time = now  # 从当前时刻开始计时
            return  # 尚未发生时间流逝
        dt = max(0.0, min(now - self.last_update_time, config.MAX_FRAME_DT))  # 限制单帧步长
        self.last_update_time = now  # 记录本次物理更新时间
        hit = advance_state(self.state, self.layout, dt, self.joystick_input(),
                            boost=self.boost_requested)  # 连续推进并处理墙体与能量
        if hit:  # 本帧撞墙
            self.screen = "over"  # 显示结束界面
            self.last_update_time = None  # 结束后停止物理计时

    def handle_click(self, position: tuple[int, int], now: float) -> None:  # 处理鼠标单击
        """根据当前界面与点击位置执行暂停、继续、重试或退出。"""  # 函数说明
        del now  # 单击逻辑不需要时间参数
        self.last_press_time = None  # 鼠标操作后重新计算双击窗口
        self.last_update_time = None  # 切换界面后重新计时
        if self.screen == "start":
            self.reset()
        elif self.screen == "menu":
            icon_rect = self.layout.settings_icon_rect()
            icon = pygame.Rect(icon_rect.left, icon_rect.top,
                               icon_rect.width, icon_rect.height)
            if icon.collidepoint(position):
                self.settings_open = not self.settings_open
                return
            if self.settings_open:
                wasd_rect, joystick_rect = (
                    pygame.Rect(item.left, item.top, item.width, item.height)
                    for item in self.layout.settings_mode_rects()
                )
                if wasd_rect.collidepoint(position):
                    self.input_mode = "wasd"
                    self.held_keys.clear()
                    self.mouse_joystick = (0.0, 0.0)
                elif joystick_rect.collidepoint(position):
                    self.input_mode = "joystick"
                    self.held_keys.clear()
                    self.mouse_joystick = (0.0, 0.0)
                else:
                    self.settings_open = False
                return
            for index, rect in enumerate(self.layout.menu_button_rects()):
                hit_rect = pygame.Rect(rect.left, rect.top, rect.width, rect.height)
                if hit_rect.collidepoint(position):
                    if index == 0:
                        self.reset()
                    elif index == 1:
                        self.screen, self.help_page = "help", 0
                    else:
                        self.quit = True
                    return
        elif self.screen == "help":
            panel = self.layout.help_panel_rect()
            if position[1] >= panel.bottom - 115:
                self.screen = "menu"
            elif position[0] < panel.left + 90 and self.help_page > 0:
                self.help_page -= 1
            elif position[0] > panel.right - 90 and self.help_page < config.HELP_PAGE_COUNT - 1:
                self.help_page += 1
        elif self.screen == "game":  # 游戏画面单击暂停
            self.screen = "pause"  # 进入暂停界面
        elif self.screen == "pause":  # 暂停界面按图标区域判断
            exit_rect, _play_rect, restart_rect = self.layout.pause_icon_rects()  # 三个图标判定区域
            if exit_rect.contains(position):  # 点中左侧退出图标
                self.screen = "menu"
            elif restart_rect.contains(position):  # 点中右侧重试图标
                self.reset()  # 重开一局
            else:  # 点中其他位置（含中间继续图标）
                self.screen = "game"  # 继续游戏
        elif self.screen == "over":  # 结束界面单击重试
            self.reset()  # 重开一局

    def handle_mouse_motion(self, position: tuple[int, int]) -> None:
        if self.screen != "game" or self.input_mode != "joystick":
            return
        cx, cy = config.JOYSTICK_CENTER
        dx, dy = position[0] - cx, position[1] - cy
        radius = config.JOYSTICK_BASE_RADIUS
        length = math.hypot(dx, dy)
        if length > radius:
            dx, dy = dx * radius / length, dy * radius / length
        self.mouse_joystick = (dx / radius, dy / radius)


def run(seed: int | None = None) -> None:  # 运行图形窗口
    """创建 pygame 窗口并进入高刷新率事件循环。"""  # 函数说明
    pygame.init()  # 初始化 pygame
    try:  # 保证退出时清理 pygame
        window = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))  # 创建窗口
        pygame.display.set_caption("贪吃蛇")  # 设置窗口标题
        clock = pygame.time.Clock()  # 帧率控制
        layout = Layout.default()  # 默认布局
        controller = Controller(layout, seed)  # 创建控制器
        while not controller.quit:  # 主循环
            for event in pygame.event.get():  # 处理所有事件
                if event.type == pygame.QUIT:  # 关闭窗口
                    controller.quit = True  # 标记退出
                elif event.type == pygame.KEYDOWN:  # 键盘按下
                    controller.handle_key(event.key, time.monotonic(), getattr(event, "unicode", ""))  # 传入字符兼容大小写
                elif event.type == pygame.KEYUP:  # 键盘释放
                    controller.handle_key_up(event.key, getattr(event, "unicode", ""))  # 解除 WASD 施力
                elif event.type == pygame.WINDOWFOCUSLOST:  # 切换到其他窗口
                    controller.lose_focus()  # 清除可能无法收到释放事件的方向键
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 鼠标左键
                    controller.handle_click(event.pos, time.monotonic())
                elif event.type == pygame.MOUSEMOTION:
                    controller.handle_mouse_motion(event.pos)
            if controller.quit:  # 需要退出
                break  # 跳出循环
            now = time.monotonic()  # 为一帧使用同一个时间戳
            controller.update(now)  # 按真实时间连续移动蛇
            joystick = controller.joystick_input()
            if controller.screen == "help":
                frame = screens.render(controller.screen, controller.state, layout, joystick,
                                       help_page=controller.help_page)
            else:
                frame = screens.render(controller.screen, controller.state, layout, joystick,
                                       input_mode=controller.input_mode,
                                       settings_open=controller.settings_open,
                                       boosting=controller.boost_requested)
            window.blit(frame, (0, 0))  # 绘制到窗口
            pygame.display.flip()  # 刷新显示
            clock.tick(config.FPS)  # 控制高刷新率
    finally:  # 无论是否异常都清理
        pygame.quit()  # 关闭 pygame
