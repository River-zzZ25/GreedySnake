"""全局配置：窗口、颜色、比例尺寸、透明度与界面文案。"""  # 模块说明

import math

# ---------------- 窗口与布局（单位：像素） ----------------  # 分组说明

WINDOW_WIDTH = 1200  # 窗口宽度（兼顾 1366×768 屏幕）
WINDOW_HEIGHT = 720  # 窗口高度
FPS = 120  # 目标刷新率，保证连续转向平滑
MAX_FRAME_DT = 0.05  # 单帧最大物理步长，避免窗口卡顿后瞬移
SNAKE_SPEED = 189.0  # 在上一阶段基础上提升 1.5 倍
TURN_RATE = 3.141592653589793  # 最大转速为每秒 180 度，形成有半径的曲线
TURN_RESPONSE = 5.0  # 朝目标方向转动的响应强度，接近目标时逐渐放缓
PHYSICS_DT = 1 / 240  # 小步物理积分，曲线与碰撞不依赖显示刷新率
MARGIN = 24  # 窗口左右边距
HEADER_HEIGHT = 64  # 顶部标题与分数区域高度
FOOTER_HEIGHT = 56  # 底部操作指引区域高度
WALL_THICKNESS = 12  # 灰色墙体厚度

# ---------------- 图形比例（题目要求 头 3 : 身 3 : 食物 1.5） ----------------  # 分组说明

UNIT = 12
AREA_SCALE = math.sqrt(2 / 3)  # 面积缩为当前的 2/3
SNAKE_DIAMETER = 36 * AREA_SCALE  # 直径约 29.4 像素
SNAKE_RADIUS = SNAKE_DIAMETER / 2  # 蛇圆半径约 14.7 像素
SNAKE_OVERLAP = SNAKE_RADIUS / 4  # 相邻圆形重叠长度为半径的 1/4
SNAKE_SPACING = 2 * SNAKE_RADIUS - SNAKE_OVERLAP  # 沿轨迹的相邻圆心距约 25.7 像素
FOOD_SIDE = 18 * AREA_SCALE  # 边长约 14.7 像素，面积约缩为 2/3
FOOD_OUTLINE = 2  # 空心正方形边框粗细
FOOD_MARGIN = 12  # 食物距离墙的最小像素距离
DARKEN_FACTOR = 0.55  # 圆形重叠区域颜色加深系数

# ---------------- 虚拟摇杆 ----------------  # 分组说明

JOYSTICK_BOX = (WINDOW_WIDTH - 268, 400, 220, 220)  # 右侧鼠标摇杆框，位于棋盘内
JOYSTICK_CENTER = (JOYSTICK_BOX[0] + JOYSTICK_BOX[2] // 2,
                   JOYSTICK_BOX[1] + JOYSTICK_BOX[3] // 2)  # 摇杆中心
JOYSTICK_BASE_RADIUS = 72  # 框内底座半径
JOYSTICK_KNOB_RADIUS = 20  # 摇杆中心圆半径
JOYSTICK_MAX_OFFSET = 28  # 摇杆中心最大偏移
JOYSTICK_TRANSPARENCY = 0.40  # 摇杆透明度为 40%
JOYSTICK_ALPHA = int(255 * (1 - JOYSTICK_TRANSPARENCY))  # 40% 透明对应 60% 不透明
MAX_FOOD_COUNT = 10  # 同时存在的食物上限
INITIAL_FOOD_COUNT = 3  # 开局同时出现多个食物

# ---------------- 颜色（RGB 三元组） ----------------  # 分组说明

COLOR_BG = (14, 14, 20)  # 窗口背景
COLOR_BOARD = (18, 18, 26)  # 棋盘内部背景
COLOR_WALL = (105, 105, 112)  # 灰色实心墙体
COLOR_HEAD = (60, 130, 255)  # 蓝色实心圆形蛇头
COLOR_BODY = (244, 202, 44)  # 黄色实心圆形蛇身
COLOR_FOOD = (58, 208, 92)  # 绿色空心正方形食物
COLOR_TEXT = (238, 238, 238)  # 白色文字
COLOR_TITLE = (82, 214, 206)  # 青色标题
COLOR_DANGER = (238, 92, 92)  # 红色失败提示
COLOR_ACCENT = (96, 226, 164)  # 绿色继续按钮
COLOR_DIM_TEXT = (150, 150, 160)  # 灰色提示文字
COLOR_PANEL = (18, 18, 26)  # 弹窗面板底色
COLOR_PANEL_BORDER = (95, 95, 110)  # 弹窗面板边框
COLOR_VEIL = (5, 5, 10)  # 半透明遮罩颜色

# ---------------- 透明度 ----------------  # 分组说明

TRANSPARENCY_70 = 0.70  # 题目要求的 70% 透明度
PANEL_ALPHA = int(255 * (1 - TRANSPARENCY_70))  # 70% 透明即不透明度 30%，alpha ≈ 76
PAUSE_VEIL_ALPHA = 170  # 暂停时棋盘压暗，避免半透明面板下方过于花哨
OVER_VEIL_ALPHA = 76  # 结束界面只轻微压暗，保证蛇与食物最后位置清晰可见
START_PANEL_ALPHA = 255  # 开始面板完全不透明，保证文字清晰

# ---------------- 弹窗尺寸（暂停面板为旧版的一半） ----------------  # 分组说明

PAUSE_PANEL_WIDTH = 400  # 暂停面板宽度（旧版约 800 像素的一半）
PAUSE_PANEL_HEIGHT = 168  # 暂停面板高度（旧版约 336 像素的一半）
PAUSE_ICON_SPACING = 110  # 暂停界面三个图标的中心间距
PAUSE_ICON_HIT = 70  # 暂停图标鼠标点击判定区域边长
PAUSE_DOUBLE_WINDOW = 0.6  # 连续按两次空格的判定窗口（秒）
START_PANEL_WIDTH = 560  # 开始面板宽度
START_PANEL_HEIGHT = 340  # 开始面板高度
OVER_PANEL_WIDTH = 460  # 结束面板宽度
OVER_PANEL_HEIGHT = 240  # 结束面板高度

# ---------------- 字体字号 ----------------  # 分组说明

TITLE_FONT_SIZE = 38  # 顶部标题字号
SCORE_FONT_SIZE = 30  # 右上角分数字号
GUIDE_FONT_SIZE = 22  # 底部操作指引字号
PANEL_TITLE_FONT_SIZE = 44  # 面板标题字号
PANEL_TEXT_FONT_SIZE = 24  # 面板正文字号
PANEL_HINT_FONT_SIZE = 26  # 面板操作提示字号
LABEL_FONT_SIZE = 18  # 图标下方的小标签字号

# ---------------- 界面文案 ----------------  # 分组说明

TITLE_TEXT = "贪 吃 蛇"  # 顶部标题
GUIDE_TEXT = "按住 WASD 或拖动右侧摇杆转向    松开继续前进    单击 / 空格连按两次暂停"
PAUSE_HINT = "暂停中：单击 / 空格连按两次继续    右侧重试    左侧回主页面"
OVER_HINT = "R 重试    Esc 回主页面"
START_LINES = (  # 开始面板正文
    "按住 W / A / S / D   平滑转向",  # 移动说明
    "松开继续前进，吃食物 +1 分并增长",  # 得分与成长规则
    "撞墙或撞到自己，游戏结束",  # 失败规则
    "空格连按两次 / 鼠标单击   暂停",  # 暂停说明
)  # 开始面板正文结束
START_HINT = "== 按任意键开始 =="  # 开始提示
PAUSE_LABELS = ("退出", "继续", "重试")  # 暂停界面三个图标下方标签
MENU_BUTTONS = ("开始游戏", "帮助", "退出")
