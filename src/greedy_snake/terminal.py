"""Windows 终端控制：启用 ANSI、切换备用屏幕、读取按键。"""  # 模块说明

import ctypes  # 调用 Windows 控制台 API
import sys  # 访问标准输入输出
from contextlib import contextmanager  # 提供 with 上下文管理

STD_OUTPUT_HANDLE = -11  # 标准输出句柄编号
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004  # 允许解释 ANSI 转义序列的控制台标志


def _enable_ansi() -> bool:  # 开启 Windows 控制台的 ANSI 支持
    """尝试为当前控制台启用 VT 解析，成功返回 True。"""  # 函数说明
    try:  # 非 Windows 或没有控制台时安静失败
        kernel32 = ctypes.windll.kernel32  # 取得 kernel32 动态库
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)  # 获取标准输出句柄
        mode = ctypes.c_ulong()  # 用来接收当前控制台模式
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):  # 读取当前模式
            return False  # 读取失败说明不是真实控制台
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING  # 追加 ANSI 开关位
        return bool(kernel32.SetConsoleMode(handle, new_mode))  # 写回模式并返回是否成功
    except Exception:  # 捕获所有平台异常
        return False  # 视为不支持 ANSI


def _force_utf8() -> None:  # 强制标准流使用 UTF-8
    """把标准输出与标准错误切换为 UTF-8，避免中文乱码。"""  # 函数说明
    for stream in (sys.stdout, sys.stderr):  # 同时处理两个输出流
        try:  # 部分流可能不支持重新配置
            encoding = (stream.encoding or "").lower().replace("-", "")  # 归一化当前编码名
            if encoding != "utf8":  # 当前不是 UTF-8 时才切换
                stream.reconfigure(encoding="utf-8")  # 重新配置编码
        except Exception:  # 忽略无法配置的流
            pass  # 继续处理下一个流


def setup() -> None:  # 终端初始化
    """初始化终端编码与 ANSI 支持，绘制前调用一次即可。"""  # 函数说明
    _force_utf8()  # 先保证中文正常输出
    _enable_ansi()  # 再尝试开启 ANSI 颜色


@contextmanager  # 上下文管理器装饰器
def fullscreen():  # 进入全屏备用屏幕
    """进入备用屏幕并隐藏光标，退出时恢复原终端。"""  # 函数说明
    setup()  # 确保终端已初始化
    out = sys.stdout  # 缓存标准输出
    out.write("\x1b[?1049h\x1b[?25l\x1b[2J")  # 进入备用屏、隐藏光标、清屏
    out.flush()  # 立即刷新
    try:  # 保证异常退出也能恢复终端
        yield  # 把控制权交给绘制循环
    finally:  # 无论是否异常都执行恢复
        out.write("\x1b[?25h\x1b[?1049l")  # 显示光标并退出备用屏幕
        out.flush()  # 立即刷新


def draw(frame: str) -> None:  # 输出一帧
    """把画布生成的一帧内容写到终端。"""  # 函数说明
    sys.stdout.write(frame)  # 写入整帧
    sys.stdout.flush()  # 立即刷新到屏幕


def read_key() -> str:  # 读取一个按键
    """阻塞读取一个按键；方向键等扩展键返回空字符串。"""  # 函数说明
    if not sys.stdin.isatty():  # 没有交互式终端时无法读键
        raise RuntimeError("当前不是交互式终端，请使用 --snapshot 预览单帧")  # 抛出友好错误
    import msvcrt  # 延迟导入 Windows 专用模块
    ch = msvcrt.getwch()  # 读取一个宽字符按键
    if ch in ("\x00", "\xe0"):  # 扩展键（方向键、功能键）的引导字节
        msvcrt.getwch()  # 丢弃扩展键的第二个字节
        return ""  # 扩展键暂不处理
    return ch  # 返回普通按键字符
