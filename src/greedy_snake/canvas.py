"""字符画布：用二维单元格网格拼出终端画面。"""  # 模块说明

import unicodedata  # 用于判断字符的东亚显示宽度

from .config import BG_COLORS, FG_COLORS, RESET, SCREEN_HEIGHT, SCREEN_WIDTH  # 颜色与默认尺寸

DEFAULT_FG = "white"  # 默认前景色
DEFAULT_BG = "black"  # 默认背景色

Cell = tuple[str, str, str] | None  # (字符, 前景色名, 背景色名)；None 表示宽字符占用的第二格


def char_width(ch: str) -> int:  # 计算单个字符占用的列数
    """返回字符在终端中的显示宽度。"""  # 函数说明
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1  # 全角/宽字符占两列


def text_width(text: str) -> int:  # 计算整段文本的显示宽度
    """返回文本在终端中占用的总列数。"""  # 函数说明
    return sum(char_width(ch) for ch in text)  # 累加每个字符的宽度


class Canvas:  # 固定尺寸的字符画布
    """二维单元格网格，负责绘制与转成 ANSI 字符串。"""  # 类说明

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):  # 构造画布
        self.width = width  # 记录画布宽度
        self.height = height  # 记录画布高度
        self.grid: list[list[Cell]] = [  # 二维网格：行 -> 列
            [(" ", DEFAULT_FG, DEFAULT_BG) for _ in range(width)]  # 每行铺满黑底空格
            for _ in range(height)  # 共 height 行
        ]  # 二维网格初始化结束

    def _write(self, x: int, y: int, cell: Cell) -> None:  # 安全写入单个单元格
        """写入单元格，并清理被覆盖的宽字符及其占位格。"""  # 函数说明
        if not (0 <= x < self.width and 0 <= y < self.height):  # 越界直接忽略
            return  # 结束本次写入
        old = self.grid[y][x]  # 取出被覆盖的旧单元格
        if old is None and x > 0:  # 旧格是宽字符的第二格
            self.grid[y][x - 1] = (" ", DEFAULT_FG, DEFAULT_BG)  # 清掉第一格避免残留
        elif old is not None and char_width(old[0]) == 2 and x + 1 < self.width:  # 旧格是宽字符的第一格
            self.grid[y][x + 1] = (" ", DEFAULT_FG, DEFAULT_BG)  # 清掉第二格占位
        self.grid[y][x] = cell  # 写入新单元格

    def fill_rect(self, x: int, y: int, width: int, height: int,  # 填充矩形（左上角与宽高）
                  char: str = " ", fg: str = DEFAULT_FG, bg: str = DEFAULT_BG) -> None:  # 填充矩形区域
        """把矩形区域统一填充为指定字符与颜色。"""  # 函数说明
        for row in range(max(0, y), min(y + height, self.height)):  # 限定有效行范围
            for col in range(max(0, x), min(x + width, self.width)):  # 限定有效列范围
                self._write(col, row, (char, fg, bg))  # 逐格写入

    def put_text(self, x: int, y: int, text: str,  # 写入文本（起始列、行、内容）
                 fg: str = DEFAULT_FG, bg: str = DEFAULT_BG) -> int:  # 写入一段文本
        """在 (x, y) 处写入文本，返回文本结束后的列位置。"""  # 函数说明
        if not 0 <= y < self.height:  # 行越界时忽略
            return x  # 返回原位置
        col = x  # 从指定列开始
        for ch in text:  # 逐字符写入
            width = char_width(ch)  # 计算当前字符宽度
            self._write(col, y, (ch, fg, bg))  # 写入字符主格
            if width == 2:  # 宽字符需要两个格子
                self._write(col + 1, y, None)  # 第二格标记为占位
            col += width  # 列游标前进
        return col  # 返回结束列

    def put_centered(self, left: int, width: int, y: int, text: str,  # 在指定区间内居中写入
                     fg: str = DEFAULT_FG, bg: str = DEFAULT_BG) -> int:  # 在区间内居中写入
        """在 [left, left + width) 区间内水平居中写入文本。"""  # 函数说明
        x = left + max(0, (width - text_width(text)) // 2)  # 计算居中起点
        return self.put_text(x, y, text, fg, bg)  # 写入并返回结束列

    def draw_border(self, x: int, y: int, width: int, height: int,  # 绘制矩形边框（左上角与宽高）
                    fg: str = "gray", bg: str = DEFAULT_BG) -> None:  # 绘制矩形边框
        """绘制单线矩形边框，包含四个直角。"""  # 函数说明
        for col in range(x + 1, x + width - 1):  # 遍历上下横线覆盖的列
            self._write(col, y, ("─", fg, bg))  # 画上边横线
            self._write(col, y + height - 1, ("─", fg, bg))  # 画下边横线
        for row in range(y + 1, y + height - 1):  # 遍历左右竖线覆盖的行
            self._write(x, row, ("│", fg, bg))  # 画左边竖线
            self._write(x + width - 1, row, ("│", fg, bg))  # 画右边竖线
        self._write(x, y, ("┌", fg, bg))  # 左上角
        self._write(x + width - 1, y, ("┐", fg, bg))  # 右上角
        self._write(x, y + height - 1, ("└", fg, bg))  # 左下角
        self._write(x + width - 1, y + height - 1, ("┘", fg, bg))  # 右下角

    def row_text(self, y: int) -> str:  # 取一行的纯文本
        """返回某一行的纯文本（宽字符占位格会被跳过）。"""  # 函数说明
        return "".join(cell[0] for cell in self.grid[y] if cell is not None)  # 拼接非占位字符

    def to_plain_text(self) -> str:  # 转成无颜色的纯文本
        """生成不带颜色控制符的整屏文本，便于快照与测试。"""  # 函数说明
        return "\n".join(self.row_text(y) for y in range(self.height))  # 逐行拼接

    def render(self) -> str:  # 转成可绘制到终端的 ANSI 字符串
        """生成一帧 ANSI 字符串：定位光标、切换颜色并输出字符。"""  # 函数说明
        parts = ["\x1b[H"]  # 光标移动到左上角
        current = None  # 当前颜色组合
        for y in range(self.height):  # 逐行输出
            parts.append(f"\x1b[{y + 1};1H")  # 光标绝对定位到行首
            for cell in self.grid[y]:  # 逐格输出
                if cell is None:  # 宽字符占位格跳过
                    continue  # 继续处理下一格
                ch, fg, bg = cell  # 拆出字符与颜色
                if (fg, bg) != current:  # 只有颜色变化时才输出转义序列
                    parts.append(FG_COLORS[fg] + BG_COLORS[bg])  # 应用新的前景/背景色
                    current = (fg, bg)  # 记录当前颜色组合
                parts.append(ch)  # 输出字符
        parts.append(RESET)  # 帧末尾重置颜色
        return "".join(parts)  # 拼接成完整帧
