"""平滑图形绘制：抗锯齿圆形、重叠区域、空心方块、图标与中文文字。"""  # 模块说明

import math  # 计算圆环与透镜形状
import os  # 判断字体文件是否存在

import pygame  # 图形库
import pygame.font  # 字体子模块

from . import config  # 颜色与尺寸配置

_FONT_CANDIDATES = (  # 中文字体候选路径（Windows / Ubuntu）
    "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Ubuntu Noto CJK
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",  # Ubuntu Noto CJK 另一种路径
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Ubuntu 文泉驿微米黑
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Ubuntu 文泉驿正黑
    "/usr/share/fonts/truetype/arphic/uming.ttc",  # Ubuntu 文鼎明体
)  # 字体路径候选结束
_FONT_NAMES = ("microsoftyahei", "msyh", "notosanscjk", "notosanscjksc",  # SysFont 名称候选
               "wenquanyimicrohei", "wenquanyizenhei", "simhei")  # SysFont 名称候选
_font_cache: dict[int, pygame.font.Font] = {}  # 字号到字体的缓存


def get_font(size: int) -> pygame.font.Font:  # 获取中文字体
    """按字号加载中文字体，找不到中文字体时退回默认字体。"""  # 函数说明
    if not pygame.font.get_init():  # 重新渲染前可能已经退出过 pygame
        _font_cache.clear()  # 旧 Font 对象在字体模块退出后失效
        pygame.font.init()  # 重建字体环境
    if size in _font_cache:  # 命中缓存
        return _font_cache[size]  # 直接返回
    pygame.font.init()  # 确保字体模块已初始化
    font = None  # 字体对象
    for path in _FONT_CANDIDATES:  # 依次尝试字体文件
        if os.path.exists(path):  # 字体文件存在
            try:  # 加载字体
                font = pygame.font.Font(path, size)  # 创建字体对象
                break  # 加载成功即停止
            except Exception:  # 字体损坏或格式不支持
                font = None  # 继续尝试下一个
    if font is None:  # 文件方式失败时尝试系统字体名
        for name in _FONT_NAMES:  # 依次尝试字体名
            path = pygame.font.match_font(name)  # 查找字体文件
            if path:  # 找到字体
                try:  # 加载字体
                    font = pygame.font.Font(path, size)  # 创建字体对象
                    break  # 加载成功即停止
                except Exception:  # 加载失败
                    font = None  # 继续尝试
    if font is None:  # 仍然没有中文字体
        font = pygame.font.Font(None, size)  # 使用默认字体（中文可能显示为方框）
    _font_cache[size] = font  # 写入缓存
    return font  # 返回字体


def darken(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:  # 颜色加深
    """把颜色每个通道乘以系数并限制在 0~255。"""  # 函数说明
    return tuple(max(0, min(255, int(channel * factor))) for channel in color)  # 逐通道缩放


def draw_circle(surface: pygame.Surface, center: tuple[float, float],  # 中心点与半径
                radius: float, color: tuple[int, int, int]) -> None:  # 绘制抗锯齿实心圆
    """局部四倍采样保留小数圆心，缓慢移动时也不会整像素跳动。"""  # 函数说明
    left, top = math.floor(center[0] - radius) - 1, math.floor(center[1] - radius) - 1  # 局部画布原点
    size, scale = math.ceil(radius * 2) + 4, 4  # 只放大当前小圆的范围
    layer = pygame.Surface((size * scale, size * scale), pygame.SRCALPHA)  # 四倍透明画布
    local = (round((center[0] - left) * scale), round((center[1] - top) * scale))  # 保留亚像素圆心
    pygame.draw.circle(layer, color, local, round(radius * scale))  # 画真实尺寸的实心圆
    surface.blit(pygame.transform.smoothscale(layer, (size, size)), (left, top), special_flags=pygame.BLEND_PREMULTIPLIED)  # 平滑降采样后合成


def draw_polygon(surface: pygame.Surface, points, color: tuple[int, int, int]) -> None:  # 绘制抗锯齿多边形
    """局部四倍采样保留重叠轮廓的小数位置。"""  # 函数说明
    if len(points) < 3:  # 少于三个点无法构成多边形
        return  # 直接返回
    left, top = math.floor(min(x for x, _ in points)) - 1, math.floor(min(y for _, y in points)) - 1  # 局部原点
    width, height = math.ceil(max(x for x, _ in points)) - left + 2, math.ceil(max(y for _, y in points)) - top + 2  # 局部尺寸
    scale = 4  # 与圆形使用相同亚像素精度
    layer = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)  # 局部透明画布
    local = [(round((x - left) * scale), round((y - top) * scale)) for x, y in points]  # 放大的局部顶点
    pygame.draw.polygon(layer, color, local)  # 填充轮廓
    surface.blit(pygame.transform.smoothscale(layer, (width, height)), (left, top), special_flags=pygame.BLEND_PREMULTIPLIED)  # 合成到原始尺寸画面


def _sample_arc(center: tuple[float, float], radius: float, start: float, end: float,  # 圆弧参数
                steps: int) -> list[tuple[float, float]]:  # 采样圆弧上的点
    """返回从 start 角度到 end 角度（弧度）均匀采样的点。"""  # 函数说明
    points = []  # 结果列表
    for index in range(steps + 1):  # 逐点采样
        angle = start + (end - start) * index / steps  # 当前角度
        points.append((center[0] + radius * math.cos(angle),  # 当前横坐标
                       center[1] + radius * math.sin(angle)))  # 当前纵坐标
    return points  # 返回采样点


def _sweep(start: float, end: float, through: float) -> float:  # 计算经过某角度的圆弧扫角
    """返回从 start 到 end、且经过 through 的带符号扫角。"""  # 函数说明
    two_pi = 2 * math.pi  # 圆周弧度
    ccw = (end - start) % two_pi  # 逆时针方向扫角
    through_rel = (through - start) % two_pi  # 经过角度相对起点
    if through_rel <= ccw:  # 逆时针路径经过目标角度
        return ccw  # 使用逆时针扫角
    return -((start - end) % two_pi)  # 否则使用顺时针扫角


def lens_polygon(center_a: tuple[float, float], center_b: tuple[float, float],  # 两圆心与半径
                 radius: float, steps: int = 16) -> list[tuple[float, float]]:  # 计算两圆重叠区域
    """返回两个半径相同、相交圆的重叠透镜多边形；不相交时返回空列表。"""  # 函数说明
    dx, dy = center_b[0] - center_a[0], center_b[1] - center_a[1]  # 两圆心位移
    distance = math.hypot(dx, dy)  # 圆心距
    if distance <= 0 or distance >= 2 * radius:  # 相离或重合时不绘制
        return []  # 返回空列表
    ux, uy = dx / distance, dy / distance  # 单位方向向量
    mx, my = (center_a[0] + center_b[0]) / 2, (center_a[1] + center_b[1]) / 2  # 两圆心中点
    half_chord = math.sqrt(radius * radius - (distance / 2) ** 2)  # 交点弦半长
    px, py = -uy, ux  # 垂直方向向量
    point_one = (mx + half_chord * px, my + half_chord * py)  # 第一个交点
    point_two = (mx - half_chord * px, my - half_chord * py)  # 第二个交点
    angle_a_one = math.atan2(point_one[1] - center_a[1], point_one[0] - center_a[0])  # 交点相对 A 的角度
    angle_a_two = math.atan2(point_two[1] - center_a[1], point_two[0] - center_a[0])  # 交点相对 A 的角度
    sweep_a = _sweep(angle_a_one, angle_a_two, math.atan2(uy, ux))  # A 圆上经过 B 方向的圆弧
    points = _sample_arc(center_a, radius, angle_a_one, angle_a_one + sweep_a, steps)  # A 圆上的弧
    angle_b_one = math.atan2(point_two[1] - center_b[1], point_two[0] - center_b[0])  # 交点相对 B 的角度
    angle_b_two = math.atan2(point_one[1] - center_b[1], point_one[0] - center_b[0])  # 交点相对 B 的角度
    sweep_b = _sweep(angle_b_one, angle_b_two, math.atan2(-uy, -ux))  # B 圆上经过 A 方向的圆弧
    points += _sample_arc(center_b, radius, angle_b_one, angle_b_one + sweep_b, steps)  # B 圆上的弧
    return points  # 返回透镜多边形


def draw_hollow_square(surface: pygame.Surface, rect, color: tuple[int, int, int],  # 矩形与线宽
                       width: int) -> None:  # 绘制空心正方形
    """使用浮点矩形的真实外围绘制空心边框，与食物碰撞轮廓一致。"""  # 函数说明
    x, y, span_x, span_y = rect  # 可以传入带小数坐标的矩形
    left, top = math.floor(x) - 1, math.floor(y) - 1  # 局部画布原点
    size = (math.ceil(span_x) + 4, math.ceil(span_y) + 4)  # 保留抗锯齿边缘
    scale = 4  # 与蛇圆保持相同的亚像素精度
    layer = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)  # 四倍画布
    local = (round((x - left) * scale), round((y - top) * scale), round(span_x * scale), round(span_y * scale))  # 真实轮廓
    pygame.draw.rect(layer, color, local, width=width * scale)  # 绘制向内的空心方块边框
    surface.blit(pygame.transform.smoothscale(layer, size), (left, top), special_flags=pygame.BLEND_PREMULTIPLIED)  # 降采样并合成


def draw_ring_arc(surface: pygame.Surface, center: tuple[float, float], radius: float,  # 圆心与半径
                  thickness: float, color: tuple[int, int, int],  # 线宽与角度
                  start_deg: float, end_deg: float, steps: int = 90) -> None:  # 绘制粗圆弧
    """沿圆弧采样小圆，绘制平滑且可留缺口的圆环。"""  # 函数说明
    start = math.radians(start_deg)  # 起始弧度
    end = math.radians(end_deg)  # 结束弧度
    for index in range(steps + 1):  # 沿弧线逐个采样
        angle = start + (end - start) * index / steps  # 当前弧度
        point = (center[0] + radius * math.cos(angle),  # 采样点横坐标
                 center[1] + radius * math.sin(angle))  # 采样点纵坐标
        draw_circle(surface, point, thickness / 2, color)  # 用实心圆填充圆环


def draw_triangle(surface: pygame.Surface, tip: tuple[float, float],  # 尖端与尺寸
                  half_height: float, length: float, color: tuple[int, int, int]) -> None:  # 绘制向右实心三角形
    """绘制尖端向右的实心正三角形。"""  # 函数说明
    back_x = tip[0] - length  # 底边横坐标
    points = [(back_x, tip[1] - half_height),  # 底边上端
              (back_x, tip[1] + half_height),  # 底边下端
              (tip[0], tip[1])]  # 尖端
    draw_polygon(surface, points, color)  # 填充三角形


def draw_arrow_head(surface: pygame.Surface, tip: tuple[float, float],  # 尖端与方向
                    direction: tuple[float, float], size: float,  # 箭头尺寸
                    color: tuple[int, int, int]) -> None:  # 绘制箭头三角
    """在 tip 处绘制朝向 direction 的实心箭头。"""  # 函数说明
    length = math.hypot(direction[0], direction[1]) or 1  # 方向向量长度
    ux, uy = direction[0] / length, direction[1] / length  # 单位方向
    px, py = -uy, ux  # 垂直方向
    base = (tip[0] - ux * size, tip[1] - uy * size)  # 箭头底边中点
    points = [(tip[0], tip[1]),  # 箭尖
              (base[0] + px * size * 0.55, base[1] + py * size * 0.55),  # 一侧底角
              (base[0] - px * size * 0.55, base[1] - py * size * 0.55)]  # 另一侧底角
    draw_polygon(surface, points, color)  # 填充箭头三角形


def draw_joystick(surface: pygame.Surface, center: tuple[int, int], base_radius: int,  # 摇杆底座
                  knob_radius: int, offset: tuple[float, float], max_offset: int,  # 摇杆中心偏移
                  color: tuple[int, int, int], alpha: int) -> None:  # 绘制半透明虚拟摇杆
    """绘制底座与摇杆中心；没有按住 WASD 时中心停在底座中央。"""  # 函数说明
    margin = base_radius + max_offset + 4  # 临时图层边距
    size = margin * 2  # 临时图层边长
    layer = pygame.Surface((size, size), pygame.SRCALPHA)  # 独立透明图层
    local_center = (margin, margin)  # 底座在图层中的中心
    pygame.draw.circle(layer, (*config.COLOR_PANEL, 255), local_center, base_radius)  # 底座填充
    pygame.draw.circle(layer, (*color, 255), local_center, base_radius, width=2)  # 底座边框
    length = math.hypot(*offset)  # 计算输入向量长度
    if length > 1:  # 防止超过最大偏移
        scale = 1 / length  # 计算单位向量缩放比例
        offset = (offset[0] * scale, offset[1] * scale)  # 限制摇杆中心偏移
    knob_center = (int(round(local_center[0] + offset[0] * max_offset)),  # 摇杆中心横坐标
                   int(round(local_center[1] + offset[1] * max_offset)))  # 摇杆中心纵坐标
    pygame.draw.circle(layer, (*color, 255), knob_center, knob_radius)  # 绘制摇杆中心
    pygame.draw.circle(layer, (*config.COLOR_TEXT, 255), knob_center, knob_radius, width=2)  # 绘制摇杆高光边
    layer.set_alpha(alpha)  # 整个控件统一应用 40% 透明度，重叠处不增加不透明度
    surface.blit(layer, (center[0] - margin, center[1] - margin))  # 合成到游戏画面


def draw_text(surface: pygame.Surface, text: str, size: int, color: tuple[int, int, int],  # 文本与对齐参数
              center: tuple[int, int] | None = None, topright: tuple[int, int] | None = None,  # 对齐方式参数
              topleft: tuple[int, int] | None = None, shadow: bool = False) -> pygame.Rect:  # 绘制文字
    """绘制抗锯齿文字，支持居中对齐与可选黑色阴影。"""  # 函数说明
    font = get_font(size)  # 获取字体
    image = font.render(text, True, color)  # 渲染文字
    rect = image.get_rect()  # 文字矩形
    if center is not None:  # 居中对齐
        rect.center = center  # 设置中心
    elif topright is not None:  # 右上角对齐
        rect.topright = topright  # 设置右上角
    elif topleft is not None:  # 左上角对齐
        rect.topleft = topleft  # 设置左上角
    if shadow:  # 需要阴影时
        shadow_image = font.render(text, True, (0, 0, 0))  # 渲染黑色文字
        surface.blit(shadow_image, (rect.x + 2, rect.y + 2))  # 绘制向右下偏移的阴影
    surface.blit(image, rect)  # 绘制文字
    return rect  # 返回文字矩形
