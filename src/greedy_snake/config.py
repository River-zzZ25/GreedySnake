"""全局配置：屏幕与棋盘尺寸、颜色名称、方块与食物样式。"""  # 模块说明

# ---------------- 屏幕与棋盘尺寸（单位：终端字符格） ----------------  # 分组说明

SCREEN_WIDTH = 72  # 画布总宽度（列）
SCREEN_HEIGHT = 22  # 画布总高度（行）

BOARD_LEFT = 15  # 棋盘左墙所在列
BOARD_TOP = 4  # 棋盘上墙所在行（上方留给标题与左上角暂停面板）
BOARD_WIDTH = 42  # 棋盘总宽度（含左右两面墙）
BOARD_HEIGHT = 15  # 棋盘总高度（含上下两面墙）

INTERIOR_LEFT = BOARD_LEFT + 1  # 可活动区域左边界列
INTERIOR_TOP = BOARD_TOP + 1  # 可活动区域上边界行
INTERIOR_WIDTH = BOARD_WIDTH - 2  # 可活动区域宽度
INTERIOR_HEIGHT = BOARD_HEIGHT - 2  # 可活动区域高度

# ---------------- 图形样式 ----------------  # 分组说明

WALL_CHAR = "█"  # 墙：灰色实心方块字符
WALL_FG = "gray"  # 墙：灰色前景
WALL_BG = "gray"  # 墙：灰色实心背景
HEAD_CHAR = "█"  # 蛇头：实心方块字符
HEAD_FG = "blue"  # 蛇头：蓝色前景
HEAD_BG = "blue"  # 蛇头：蓝色实心背景
BODY_CHAR = "█"  # 蛇身：实心方块字符
BODY_FG = "yellow"  # 蛇身：黄色前景
BODY_BG = "yellow"  # 蛇身：黄色实心背景
FOOD_CHAR = "○"  # 食物：绿色空心圆形
FOOD_FG = "green"  # 食物的前景色为绿色
PANEL_FG = "white"  # 面板文字与边框：白色
TITLE_FG = "cyan"  # 游戏标题：青色
DANGER_FG = "red"  # 失败提示：红色
HINT_FG = "gray"  # 预览提示：灰色

# ---------------- 颜色名称到 ANSI 转义序列的映射 ----------------  # 分组说明

FG_COLORS = {  # 前景色（文字与线条）
    "black": "\x1b[30m",  # 黑色文字
    "white": "\x1b[97m",  # 亮白色文字
    "gray": "\x1b[90m",  # 灰色文字
    "blue": "\x1b[94m",  # 亮蓝色文字
    "yellow": "\x1b[93m",  # 亮黄色文字
    "green": "\x1b[92m",  # 亮绿色文字
    "cyan": "\x1b[96m",  # 亮青色文字
    "red": "\x1b[91m",  # 亮红色文字
}

BG_COLORS = {  # 背景色（实心方块）
    "black": "\x1b[40m",  # 黑色背景
    "gray": "\x1b[100m",  # 灰色背景（亮黑）
    "blue": "\x1b[104m",  # 蓝色背景（亮蓝）
    "yellow": "\x1b[103m",  # 黄色背景（亮黄）
}  # 背景色映射结束

RESET = "\x1b[0m"  # 重置全部颜色
