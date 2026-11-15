"""游戏状态：蛇的圆形圆心、空心正方形食物与分数（步骤 1 仅用于界面展示）。"""  # 模块说明

import math  # 计算食物与蛇圆的距离
import random  # 随机生成食物位置
from dataclasses import dataclass, field  # 数据类工具

from . import config  # 尺寸比例常量
from .layout import Layout  # 布局信息


@dataclass  # 数据类装饰器
class GameState:  # 一局游戏的全部数据
    """保存蛇的圆心列表、食物方块左上角、分数与方向。"""  # 类说明

    snake: list[tuple[float, float]] = field(default_factory=list)  # 蛇的圆心，第 0 个为蛇头
    food: tuple[int, int] = (0, 0)  # 空心正方形食物左上角
    score: int = 0  # 当前分数
    direction: tuple[int, int] = (1, 0)  # 当前方向（步骤 2 使用）


def _food_overlaps_snake(x: int, y: int, snake: list[tuple[float, float]]) -> bool:  # 判断食物是否压住蛇
    """检查空心正方形食物是否与任意蛇圆相交。"""  # 函数说明
    for cx, cy in snake:  # 遍历蛇的每个圆心
        nearest_x = min(max(cx, x), x + config.FOOD_SIDE - 1)  # 圆心到方块的最近横坐标
        nearest_y = min(max(cy, y), y + config.FOOD_SIDE - 1)  # 圆心到方块的最近纵坐标
        if math.hypot(cx - nearest_x, cy - nearest_y) <= config.SNAKE_RADIUS + config.FOOD_OUTLINE:  # 距离过近则相交
            return True  # 返回相交
    return False  # 没有相交


def _random_food(rng: random.Random, layout: Layout,  # 随机食物参数
                 snake: list[tuple[float, float]]) -> tuple[int, int]:  # 随机放置食物
    """在可活动区域内随机放置空心正方形食物，并避开蛇身。"""  # 函数说明
    interior = layout.interior  # 可活动区域
    min_x = interior.left + config.FOOD_MARGIN  # 食物最小左边界
    max_x = interior.right - config.FOOD_SIDE - config.FOOD_MARGIN  # 食物最大左边界
    min_y = interior.top + config.FOOD_MARGIN  # 食物最小上边界
    max_y = interior.bottom - config.FOOD_SIDE - config.FOOD_MARGIN  # 食物最大上边界
    for _ in range(200):  # 最多随机尝试 200 次
        x = rng.randint(min_x, max_x)  # 随机横坐标
        y = rng.randint(min_y, max_y)  # 随机纵坐标
        if not _food_overlaps_snake(x, y, snake):  # 不与蛇相交
            return (x, y)  # 返回该位置
    for y in range(min_y, max_y + 1):  # 随机失败后按顺序扫描
        for x in range(min_x, max_x + 1):  # 逐列扫描
            if not _food_overlaps_snake(x, y, snake):  # 找到空闲位置
                return (x, y)  # 返回该位置
    return (min_x, min_y)  # 兜底返回左上角


def create_initial_state(layout: Layout, seed: int | None = None) -> GameState:  # 创建初始状态
    """初始长度为“蛇头 + 一格身体”，随机放置空心正方形食物，分数为 0。"""  # 函数说明
    interior = layout.interior  # 可活动区域
    head = (interior.left + interior.width / 2, interior.top + interior.height / 2)  # 蛇头放在区域中心
    body = (head[0] - config.SNAKE_SPACING, head[1])  # 身体圆在蛇头左侧，与蛇头重叠半径的 1/4
    snake = [head, body]  # 蛇头在前、身体在后
    rng = random.Random(seed)  # 可选随机种子，便于复现
    food = _random_food(rng, layout, snake)  # 随机放置食物
    return GameState(snake=snake, food=food, score=0)  # 返回初始状态
