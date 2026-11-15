"""应用逻辑：实现步骤 1 的界面预览切换循环。"""  # 模块说明

from . import screens, terminal  # 界面绘制与终端工具
from .state import create_initial_state  # 初始游戏状态

SCREEN_KEYS = {  # 数字键到界面名的映射
    "1": "game",  # 1：游戏画面
    "2": "start",  # 2：开始界面
    "3": "pause",  # 3：暂停界面
    "4": "over",  # 4：失败界面
}


def run_preview(seed: int | None = None) -> None:  # 运行界面预览循环
    """在备用屏幕中循环绘制界面，按键切换，Esc/Q 退出。"""  # 函数说明
    state = create_initial_state(seed)  # 生成用于展示的初始状态
    current = "start"  # 默认先展示开始界面
    with terminal.fullscreen():  # 进入全屏备用屏幕
        while True:  # 持续绘制与等待按键
            canvas = screens.render(current, state)  # 绘制当前界面
            terminal.draw(canvas.render())  # 输出到终端
            key = terminal.read_key()  # 阻塞等待一个按键
            if key == "\x1b" or key.lower() == "q":  # Esc 或 Q 退出预览
                break  # 结束循环
            if key in SCREEN_KEYS:  # 数字键直接跳转界面
                current = SCREEN_KEYS[key]  # 更新当前界面名
                continue  # 进入下一轮绘制
            if current == "start":  # 开始界面按任意键进入游戏画面
                current = "game"  # 切换到游戏画面
            elif current == "pause":  # 暂停界面按任意键回到游戏画面
                current = "game"  # 恢复为游戏画面
            elif current == "game" and key.lower() == "p":  # 游戏画面按 P 预览暂停界面
                current = "pause"  # 切换到暂停界面
            elif current == "over" and key.lower() == "r":  # 失败界面按 R 预览重试
                current = "game"  # 切换到游戏画面
