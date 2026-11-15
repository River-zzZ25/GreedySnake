"""应用逻辑：pygame 窗口循环、暂停触发与鼠标交互。"""  # 模块说明

import time  # 判断连按两次 P 的时间窗口

import pygame  # 图形库

from . import config, screens  # 配置与界面渲染
from .layout import Layout  # 布局
from .state import create_initial_state  # 初始状态

PREVIEW_KEYS = {  # 数字键预览界面（临时，便于验收）
    pygame.K_1: "game",  # 1：游戏画面
    pygame.K_2: "start",  # 2：开始界面
    pygame.K_3: "pause",  # 3：暂停界面
    pygame.K_4: "over",  # 4：结束界面
}  # 预览快捷键映射结束


class Controller:  # 游戏界面与输入控制器
    """管理当前界面、游戏状态与暂停触发规则（不依赖窗口，便于测试）。"""  # 类说明

    def __init__(self, layout: Layout, seed: int | None = None):  # 构造控制器
        self.layout = layout  # 布局
        self.state = create_initial_state(layout, seed)  # 初始游戏状态
        self.screen = "start"  # 默认显示开始界面
        self.last_press_time: float | None = None  # 上一次按 P 的时间（None 表示还没按过）
        self.quit = False  # 是否退出程序

    def reset(self) -> None:  # 重新开始
        """重置游戏状态并进入游戏画面。"""  # 函数说明
        self.state = create_initial_state(self.layout)  # 新的初始状态
        self.screen = "game"  # 切换到游戏画面
        self.last_press_time = None  # 重置按键计时

    def handle_key(self, key: int, now: float) -> None:  # 处理按键
        """根据当前界面与按键更新时间，规则包含 P 连按两次暂停。"""  # 函数说明
        if key in (pygame.K_ESCAPE, pygame.K_q):  # Esc / Q 退出
            self.quit = True  # 标记退出
            return  # 结束处理
        if key in PREVIEW_KEYS:  # 数字键切换预览界面
            self.screen = PREVIEW_KEYS[key]  # 更新界面
            self.last_press_time = None  # 重置计时
            return  # 结束处理
        if self.screen == "start":  # 开始界面按任意键开始
            self.screen = "game"  # 进入游戏画面
            self.last_press_time = None  # 重置计时
        elif self.screen == "game":  # 游戏画面处理 P 键
            if key == pygame.K_p:  # 按下 P
                if (self.last_press_time is not None  # 已经按过一次 P
                        and now - self.last_press_time <= config.PAUSE_DOUBLE_WINDOW):  # 距上次足够近
                    self.screen = "pause"  # 连按两次才暂停
                    self.last_press_time = None  # 重置计时
                else:  # 第一次按 P
                    self.last_press_time = now  # 记录本次时间
        elif self.screen == "pause":  # 暂停界面按键
            if key == pygame.K_p:  # 按一次 P 继续
                self.screen = "game"  # 回到游戏画面
                self.last_press_time = None  # 重置计时
            elif key == pygame.K_r:  # 按 R 重试
                self.reset()  # 重开一局
        elif self.screen == "over":  # 结束界面按键
            if key == pygame.K_r:  # 按 R 重试
                self.reset()  # 重开一局

    def handle_click(self, position: tuple[int, int], now: float) -> None:  # 处理鼠标单击
        """根据当前界面与点击位置执行暂停、继续、重试或退出。"""  # 函数说明
        del now  # 单击逻辑不需要时间参数
        if self.screen == "start":  # 开始界面单击开始
            self.screen = "game"  # 进入游戏画面
            self.last_press_time = None  # 重置按键计时
        elif self.screen == "game":  # 游戏画面单击暂停
            self.screen = "pause"  # 进入暂停界面
        elif self.screen == "pause":  # 暂停界面按图标区域判断
            exit_rect, play_rect, restart_rect = self.layout.pause_icon_rects()  # 三个图标判定区域
            if exit_rect.contains(position):  # 点中左侧退出图标
                self.quit = True  # 退出程序
            elif restart_rect.contains(position):  # 点中右侧重试图标
                self.reset()  # 重开一局
            else:  # 点中其他位置（含中间继续图标）
                self.screen = "game"  # 继续游戏
                self.last_press_time = None  # 重置计时
        elif self.screen == "over":  # 结束界面单击重试
            self.reset()  # 重开一局


def run(seed: int | None = None) -> None:  # 运行图形窗口
    """创建 pygame 窗口并进入事件循环。"""  # 函数说明
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
                    controller.handle_key(event.key, time.monotonic())  # 交给控制器
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 鼠标左键
                    controller.handle_click(event.pos, time.monotonic())  # 交给控制器
            if controller.quit:  # 需要退出
                break  # 跳出循环
            frame = screens.render(controller.screen, controller.state, layout)  # 渲染当前界面
            window.blit(frame, (0, 0))  # 绘制到窗口
            pygame.display.flip()  # 刷新显示
            clock.tick(config.FPS)  # 控制帧率
    finally:  # 无论是否异常都清理
        pygame.quit()  # 关闭 pygame
