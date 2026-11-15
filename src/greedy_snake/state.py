"""游戏状态：蛇、食物与分数（实现步骤 1 仅用于界面展示）。"""  # 模块说明

import random  # 随机生成食物位置
from dataclasses import dataclass, field  # 数据类工具

from . import config  # 引入全局尺寸配置


@dataclass  # 数据类装饰器，自动生成初始化方法
class GameState:  # 一局游戏的全部数据
    """保存蛇的格子、食物格子和当前分数。"""  # 类说明

    cells: list[tuple[int, int]] = field(default_factory=list)  # 蛇的格子列表，第 0 格为蛇头
    food: tuple[int, int] = (0, 0)  # 食物所在格子坐标
    score: int = 0  # 当前分数（每吃一个食物 +1）


def _random_food(rng: random.Random, blocked: set[tuple[int, int]]) -> tuple[int, int]:  # 随机挑选食物格
    """在棋盘可活动区域内随机挑一个没被蛇占用的格子。"""  # 函数说明
    free = [  # 收集全部空闲格子
        (x, y)  # 候选坐标
        for y in range(config.INTERIOR_TOP, config.INTERIOR_TOP + config.INTERIOR_HEIGHT)  # 遍历可活动区域的行
        for x in range(config.INTERIOR_LEFT, config.INTERIOR_LEFT + config.INTERIOR_WIDTH)  # 遍历可活动区域的列
        if (x, y) not in blocked  # 排除已被蛇占用的格子
    ]  # 空闲格子列表结束
    return rng.choice(free)  # 从空闲格子中随机选一个


def create_initial_state(seed: int | None = None) -> GameState:  # 创建初始游戏状态
    """初始长度为“蛇头 + 一格身体”，随机放置食物，分数为 0。"""  # 函数说明
    rng = random.Random(seed)  # 可选随机种子，便于复现同一画面
    center_x = config.INTERIOR_LEFT + config.INTERIOR_WIDTH // 2  # 可活动区域水平中心列
    center_y = config.INTERIOR_TOP + config.INTERIOR_HEIGHT // 2  # 可活动区域垂直中心行
    head = (center_x, center_y)  # 蛇头放在区域中心
    body = (center_x - 1, center_y)  # 身体放在蛇头左侧一格
    cells = [head, body]  # 蛇头在前、身体在后
    food = _random_food(rng, set(cells))  # 随机食物，且避开蛇身
    return GameState(cells=cells, food=food, score=0)  # 返回初始状态
