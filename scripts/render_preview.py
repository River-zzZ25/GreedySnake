"""把四个界面渲染成 PNG 预览图（仅开发/验收使用，不参与游戏运行）。"""  # 模块说明

import pathlib  # 处理文件路径
import sys  # 修改模块搜索路径

ROOT = pathlib.Path(__file__).resolve().parents[1]  # 项目根目录
sys.path.insert(0, str(ROOT / "src"))  # 让脚本可以导入 greedy_snake 包

from PIL import Image, ImageDraw, ImageFont  # 图像绘制库（仅在生成预览图时需要）

from greedy_snake import config, screens  # 配置与界面绘制
from greedy_snake.canvas import char_width  # 字符显示宽度
from greedy_snake.state import create_initial_state  # 初始游戏状态

CELL_W = 16  # 每个终端字符格的像素宽度
CELL_H = 32  # 每个终端字符格的像素高度
BOX_CHARS = ("─", "│", "┌", "┐", "└", "┘")  # 需要手工绘制的框线字符

BG_RGB = {  # 背景色名称到 RGB 的映射
    "black": (12, 12, 12),  # 黑色背景
    "gray": (82, 82, 82),  # 灰色墙
    "blue": (37, 99, 204),  # 蓝色蛇头
    "yellow": (222, 184, 28),  # 黄色蛇身
}  # 背景色映射结束
FG_RGB = {  # 前景色名称到 RGB 的映射
    "white": (238, 238, 238),  # 白色文字
    "gray": (150, 150, 150),  # 灰色提示
    "blue": (90, 150, 255),  # 蓝色文字
    "yellow": (245, 210, 60),  # 黄色文字
    "green": (60, 200, 90),  # 绿色食物
    "cyan": (70, 210, 200),  # 青色标题与边框
    "red": (230, 90, 90),  # 红色失败提示
    "black": (10, 10, 10),  # 黑色文字
}  # 前景色映射结束

FONT_ASCII = pathlib.Path("C:/Windows/Fonts/consola.ttf")  # 等宽 ASCII 字体
FONT_CJK = pathlib.Path("C:/Windows/Fonts/msyh.ttc")  # 中文字体
SCREEN_NAMES = ("game", "start", "pause", "over")  # 需要生成预览图的界面


def load_fonts():  # 加载字体
    """返回 ASCII 与中文两套字体对象。"""  # 函数说明
    return {  # 字体字典
        "ascii": ImageFont.truetype(str(FONT_ASCII), 20),  # ASCII 等宽字体
        "cjk": ImageFont.truetype(str(FONT_CJK), 28),  # 中文字体
    }  # 字体字典结束


def draw_box_char(draw, left: int, top: int, ch: str, color) -> None:  # 手工绘制框线字符
    """用直线绘制边框字符，避免字体导致的虚线效果。"""  # 函数说明
    right = left + CELL_W - 1  # 单元格右边界
    bottom = top + CELL_H - 1  # 单元格下边界
    cx = left + CELL_W // 2  # 单元格中心列
    cy = top + CELL_H // 2  # 单元格中心行
    width = 2  # 线宽
    if ch == "─":  # 横线
        draw.line([left, cy, right, cy], fill=color, width=width)  # 画满整格宽度的横线
    elif ch == "│":  # 竖线
        draw.line([cx, top, cx, bottom], fill=color, width=width)  # 画满整格高度的竖线
    elif ch == "┌":  # 左上角
        draw.line([cx, cy, right, cy], fill=color, width=width)  # 向右的半条横线
        draw.line([cx, cy, cx, bottom], fill=color, width=width)  # 向下的半条竖线
    elif ch == "┐":  # 右上角
        draw.line([left, cy, cx, cy], fill=color, width=width)  # 向左的半条横线
        draw.line([cx, cy, cx, bottom], fill=color, width=width)  # 向下的半条竖线
    elif ch == "└":  # 左下角
        draw.line([cx, cy, right, cy], fill=color, width=width)  # 向右的半条横线
        draw.line([cx, top, cx, cy], fill=color, width=width)  # 向上的半条竖线
    elif ch == "┘":  # 右下角
        draw.line([left, cy, cx, cy], fill=color, width=width)  # 向左的半条横线
        draw.line([cx, top, cx, cy], fill=color, width=width)  # 向上的半条竖线


def draw_cell_char(draw, x: int, y: int, ch: str, fg: str, fonts) -> None:  # 绘制单格前景
    """根据字符类型选择字体或手绘图形。"""  # 函数说明
    left, top = x * CELL_W, y * CELL_H  # 单元格左上角像素坐标
    color = FG_RGB[fg]  # 当前前景颜色
    if ch in BOX_CHARS:  # 框线字符手工绘制
        draw_box_char(draw, left, top, ch, color)  # 画边框线段
        return  # 绘制完成
    if ch == config.FOOD_CHAR:  # 食物画成空心圆
        cx = left + CELL_W // 2  # 圆心横坐标
        cy = top + CELL_H // 2  # 圆心纵坐标
        radius = 6  # 圆的半径（像素）
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=2)  # 空心圆
        return  # 绘制完成
    font = fonts["cjk"] if char_width(ch) == 2 or ord(ch) > 127 else fonts["ascii"]  # 选择字体
    width = char_width(ch) * CELL_W  # 字符占用的像素宽度
    draw.text((left + width // 2, top + CELL_H // 2), ch, font=font, fill=color, anchor="mm")  # 居中绘制文字


def render_png(screen: str, state, out_path: pathlib.Path, fonts) -> None:  # 渲染单个界面
    """把一个画布渲染为 PNG 文件。"""  # 函数说明
    canvas = screens.render(screen, state)  # 取得界面画布
    image = Image.new("RGB", (canvas.width * CELL_W, canvas.height * CELL_H), (12, 12, 12))  # 创建黑底图像
    draw = ImageDraw.Draw(image)  # 创建绘图对象
    for y in range(canvas.height):  # 遍历每一行
        for x in range(canvas.width):  # 遍历每一列
            cell = canvas.grid[y][x]  # 取出单元格
            if cell is None:  # 跳过宽字符占位格
                continue  # 继续下一格
            ch, fg, bg = cell  # 拆出字符与颜色
            left, top = x * CELL_W, y * CELL_H  # 计算像素位置
            draw.rectangle([left, top, left + CELL_W - 1, top + CELL_H - 1], fill=BG_RGB[bg])  # 填充背景色
            if ch in (" ", config.WALL_CHAR, config.HEAD_CHAR, config.BODY_CHAR):  # 空格与实心方块由背景色呈现
                continue  # 无需绘制字形
            draw_cell_char(draw, x, y, ch, fg, fonts)  # 绘制前景内容
    image.save(out_path)  # 保存 PNG 文件


def main() -> int:  # 脚本主函数
    """生成四个界面的 PNG 预览图。"""  # 函数说明
    out_dir = ROOT / "docs" / "screenshots"  # 预览图输出目录
    out_dir.mkdir(parents=True, exist_ok=True)  # 目录不存在时自动创建
    fonts = load_fonts()  # 加载字体
    state = create_initial_state(seed=7)  # 固定种子的演示状态
    for screen in SCREEN_NAMES:  # 逐个界面生成图片
        state.score = 12 if screen in ("pause", "over") else 0  # 暂停/失败界面演示较高分数
        out_path = out_dir / f"{screen}.png"  # 输出文件路径
        render_png(screen, state, out_path, fonts)  # 渲染并保存
        print(f"generated: {out_path}", flush=True)  # 打印生成进度（英文避免控制台编码问题）
    return 0  # 成功退出


if __name__ == "__main__":  # 允许直接运行脚本
    sys.exit(main())  # 以主函数返回值作为退出码
