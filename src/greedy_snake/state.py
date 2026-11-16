"""连续运动：保留头部轨迹，沿曲线跟随，在实际轮廓接触时停下。"""  # 模块说明

import math  # 向量、角度和圆形几何
import random  # 随机生成食物
from dataclasses import dataclass, field  # 状态数据

from . import config  # 尺寸和速度
from .layout import Layout  # 棋盘边界

Vector = tuple[float, float]  # 浮点坐标或向量


def _lerp(first: Vector, second: Vector, fraction: float) -> Vector:  # 线性插值
    """返回两点间指定比例的位置。"""  # 函数说明
    return (first[0] + (second[0] - first[0]) * fraction,  # 横向插值
            first[1] + (second[1] - first[1]) * fraction)  # 纵向插值


@dataclass  # 游戏状态
class GameState:  # 保存可绘制状态和运动历史
    """snake 与 trail 都从头到尾排列；trail 额外保存一节供增长使用。"""  # 类说明

    snake: list[Vector]  # 蛇头和各节身体的真实圆心
    food: Vector | None = None  # 食物方块中心；棋盘没有空位时为 None
    score: int = 0  # 已吃食物数量
    direction: Vector = (1.0, 0.0)  # 当前前进方向，松键后保留
    rng: random.Random = field(default_factory=random.Random, repr=False, compare=False)  # 每局独立随机流
    trail: list[Vector] = field(default_factory=list, repr=False, compare=False)  # 蛇头经过的连续折线

    def __post_init__(self) -> None:  # 初始化轨迹
        """从初始身体生成向后的轨迹，并保留增长所需的一节。"""  # 函数说明
        if not self.trail:  # 允许测试或载入状态显式提供完整轨迹
            self.trail = self.snake.copy()  # 初始身体本身构成直线轨迹
            tail, previous = self.snake[-1], self.snake[-2]  # 获取尾端方向
            length = math.dist(tail, previous)  # 尾端线段长度
            extra = _lerp(previous, tail, 1 + config.SNAKE_SPACING / length)  # 向后延长一节
            self.trail.append(extra)  # 保存增长用轨迹


def _circle_hits_square(center: Vector, radius: float, square: Vector, side: float) -> bool:  # 圆与方块接触
    """采用正方形上的最近点，圆角附近也不会用包围框误判。"""  # 函数说明
    half = side / 2  # 半边长
    dx = max(abs(center[0] - square[0]) - half, 0.0)  # 到方块的横向距离
    dy = max(abs(center[1] - square[1]) - half, 0.0)  # 到方块的纵向距离
    return math.hypot(dx, dy) <= radius  # 实际圆形外围触碰方块


def _food_overlaps_snake(food: Vector, snake: list[Vector]) -> bool:  # 放置前检查重叠
    """食物的可见正方形不可与任意身体圆相交。"""  # 函数说明
    return any(_circle_hits_square(center, config.SNAKE_RADIUS, food, config.FOOD_SIDE)  # 圆与方块相交
               for center in snake)  # 逐节检查身体


def _random_food(rng: random.Random, layout: Layout, snake: list[Vector]) -> Vector | None:  # 生成食物
    """食物位置不对齐网格，优先随机，必要时扫描空位。"""  # 函数说明
    interior = layout.interior  # 活动区域
    margin = config.FOOD_SIDE / 2 + config.FOOD_MARGIN  # 食物半边长和墙边留白
    min_x, max_x = interior.left + margin, interior.left + interior.width - margin  # 横向中心边界
    min_y, max_y = interior.top + margin, interior.top + interior.height - margin  # 纵向中心边界
    if min_x > max_x or min_y > max_y:  # 区域不足以放置食物
        return None  # 不产生越界食物
    for _ in range(200):  # 先尝试随机位置
        food = (rng.uniform(min_x, max_x), rng.uniform(min_y, max_y))  # 连续随机坐标
        if not _food_overlaps_snake(food, snake):  # 真实轮廓没有相交
            return food  # 返回空位
    for y in range(math.ceil(min_y), math.floor(max_y) + 1):  # 随机失败后扫描
        for x in range(math.ceil(min_x), math.floor(max_x) + 1):  # 扫描横向位置
            if not _food_overlaps_snake((x, y), snake):  # 发现空位
                return (float(x), float(y))  # 返回合法中心
    return None  # 没有空位时不把食物塞进身体里


def create_initial_state(layout: Layout, seed: int | None = None) -> GameState:  # 开始一局
    """从棋盘中心向右前进，初始为头和一节身体。"""  # 函数说明
    head = (layout.interior.left + layout.interior.width / 2,  # 中心横坐标
            layout.interior.top + layout.interior.height / 2)  # 中心纵坐标
    state = GameState(snake=[head, (head[0] - config.SNAKE_SPACING, head[1])],  # 初始身体
                      rng=random.Random(seed))  # 独立随机数发生器
    state.food = _random_food(state.rng, layout, state.snake)  # 放置首个食物
    return state  # 返回初始状态


def _sample_trail(path: list[Vector], count: int) -> tuple[list[Vector], list[Vector]]:  # 沿轨迹取圆心
    """按路径长度采样身体，保留尾后的一节轨迹并裁去更早的历史。"""  # 函数说明
    centers = [path[0]]  # 蛇头始终为路径起点
    index, traversed = 1, 0.0  # 当前线段及此前的累计长度
    for number in range(1, count + 1):  # 最后一项是未来增长的备用位置
        target = number * config.SNAKE_SPACING  # 距离蛇头的路径长度
        length = math.dist(path[index - 1], path[index])  # 当前线段长度
        while traversed + length < target and index < len(path) - 1:  # 跳到目标所在的线段
            traversed += length  # 累计已经走过的线段长度
            index += 1  # 移到下一条线段
            length = math.dist(path[index - 1], path[index])  # 新线段长度
        fraction = (target - traversed) / length if length > 1e-12 else 0.0  # 目标在线段上的比例
        centers.append(_lerp(path[index - 1], path[index], fraction))  # 按真实轨迹插值
    return centers[:-1], path[:index] + [centers[-1]]  # 身体圆心和裁剪后的路径


def _sweep_circle(start: Vector, end: Vector, radius: float) -> float | None:  # 运动点碰圆的时间
    """求线段与原点圆第一次接触的比例，包含相切，避免高速穿过。"""  # 函数说明
    dx, dy = end[0] - start[0], end[1] - start[1]  # 相对位移
    c = start[0] ** 2 + start[1] ** 2 - radius ** 2  # 起点是否已经接触
    if c <= 0:  # 起点已在圆内或圆周上
        return 0.0  # 立即接触
    a = dx * dx + dy * dy  # 二次项系数
    if a <= 1e-20:  # 相对静止且没有接触
        return None  # 无碰撞
    b = 2 * (start[0] * dx + start[1] * dy)  # 一次项系数
    discriminant = b * b - 4 * a * c  # 求交判别式
    if discriminant < 0:  # 没有实数交点
        return None  # 无碰撞
    fraction = (-b - math.sqrt(discriminant)) / (2 * a)  # 第一次接触时间
    return min(1.0, max(0.0, fraction)) if -1e-10 <= fraction <= 1 + 1e-10 else None  # 将浮点误差限制在本段内


def _wall_contact(start: Vector, end: Vector, layout: Layout) -> float | None:  # 求墙体接触时间
    """把墙向内平移蛇头半径，求圆周刚好贴墙时的运动比例。"""  # 函数说明
    interior, radius = layout.interior, config.SNAKE_RADIUS  # 几何边界与半径
    bounds = ((interior.left + radius, interior.left + interior.width - radius),  # 水平中心范围
              (interior.top + radius, interior.top + interior.height - radius))  # 垂直中心范围
    contacts = []  # 各面墙的候选接触时间
    for axis, (low, high) in enumerate(bounds):  # 分别检查两轴
        delta = end[axis] - start[axis]  # 本轴位移
        if start[axis] < low or start[axis] > high:  # 输入状态本身已越界
            contacts.append(0.0)  # 立即停止
        elif delta < 0 and end[axis] <= low:  # 触及左墙或上墙
            contacts.append((low - start[axis]) / delta)  # 计算接触比例
        elif delta > 0 and end[axis] >= high:  # 触及右墙或下墙
            contacts.append((high - start[axis]) / delta)  # 计算接触比例
    return min(contacts) if contacts else None  # 采用最早接触的墙


def _body_contact(old: list[Vector], new: list[Vector]) -> float | None:  # 求身体接触时间
    """对运动中的两圆求相对扫掠交点，排除本来就连接的颈部。"""  # 函数说明
    contacts = []  # 每节身体的候选时间
    for index in range(2, len(old)):  # 头和相邻颈部不参与自撞判定
        start = (old[0][0] - old[index][0], old[0][1] - old[index][1])  # 起始相对位置
        end = (new[0][0] - new[index][0], new[0][1] - new[index][1])  # 结束相对位置
        contact = _sweep_circle(start, end, config.SNAKE_DIAMETER)  # 两圆接触半径为半径之和
        if contact is not None:  # 本段会接触
            contacts.append(contact)  # 保存时间
    return min(contacts) if contacts else None  # 最早接触时间


def _food_contact(start: Vector, end: Vector, food: Vector | None) -> float | None:  # 求食物接触时间
    """圆扫过方块等价于点扫过圆角矩形，分别检查边与四个圆角。"""  # 函数说明
    if food is None:  # 当前没有食物
        return None  # 无接触
    radius, half = config.SNAKE_RADIUS, config.FOOD_SIDE / 2  # 圆半径和方块半边长
    if _circle_hits_square(start, radius, food, config.FOOD_SIDE):  # 起点已经接触
        return 0.0  # 立即吃到
    contacts = []  # 边和角的候选接触时间
    for axis in (0, 1):  # 分别检查竖边和横边
        delta = end[axis] - start[axis]  # 本轴位移
        if abs(delta) <= 1e-12:  # 不穿过该轴的边
            continue  # 交给另一轴或圆角处理
        for sign in (-1, 1):  # 两侧平移后的边
            fraction = (food[axis] + sign * (half + radius) - start[axis]) / delta  # 到达边的时间
            if 0 <= fraction <= 1:  # 落在本次运动区间
                other = _lerp(start, end, fraction)[1 - axis]  # 交点的另一坐标
                if abs(other - food[1 - axis]) <= half:  # 交点在直边范围内
                    contacts.append(fraction)  # 保存接触时间
    for sx in (-1, 1):  # 方块两列角点
        for sy in (-1, 1):  # 方块两行角点
            corner = (food[0] + sx * half, food[1] + sy * half)  # 真实方块角点
            first = (start[0] - corner[0], start[1] - corner[1])  # 起点相对角点位置
            last = (end[0] - corner[0], end[1] - corner[1])  # 终点相对角点位置
            contact = _sweep_circle(first, last, radius)  # 点与角点圆的交点
            if contact is not None:  # 本段触及圆角
                contacts.append(contact)  # 保存候选时间
    return min(contacts) if contacts else None  # 返回最早接触时间


def _advance_step(state: GameState, layout: Layout, dt: float, steering: Vector) -> bool:  # 物理小步
    """求一次微小转弯及该段内的最早接触位置。"""  # 函数说明
    angle = math.atan2(state.direction[1], state.direction[0])  # 当前航向
    turn = 0.0  # 松开方向键时不再转弯
    if math.hypot(*steering) > 1e-9:  # 只有按住 WASD 才施加转向
        target = math.atan2(steering[1], steering[0])  # 摇杆对应的目标航向
        difference = (target - angle + math.pi) % math.tau - math.pi  # 沿最短方向转弯，反向键也能掉头
        turn = max(-config.TURN_RATE, min(config.TURN_RATE, difference * config.TURN_RESPONSE)) * dt  # 限制转速
    midpoint = angle + turn / 2  # 采用区间中点航向积分位移
    travel = config.SNAKE_SPEED * dt  # 恒定前进速度
    head = (state.snake[0][0] + math.cos(midpoint) * travel,  # 候选蛇头横坐标
            state.snake[0][1] + math.sin(midpoint) * travel)  # 候选蛇头纵坐标
    path = [head, *state.trail]  # 新蛇头加入真实路径
    candidate, _ = _sample_trail(path, len(state.snake))  # 身体沿原路径前进
    wall = _wall_contact(state.snake[0], head, layout)  # 墙体接触时间
    body = _body_contact(state.snake, candidate)  # 非相邻身体接触时间
    collision = min((value for value in (wall, body) if value is not None), default=None)  # 最早失败接触
    food = _food_contact(state.snake[0], head, state.food)  # 食物接触时间
    ate = food is not None and (collision is None or food < collision)  # 同时接触时失败优先
    fraction = min((value for value in (collision, food) if value is not None), default=1.0)  # 本段实际可走比例
    contact_head = _lerp(state.snake[0], head, fraction)  # 精确停在接触点
    path = [contact_head, *state.trail] if fraction > 1e-12 else state.trail  # 零位移时不引入重复点
    count = len(state.snake) + int(ate)  # 每吃一个食物新增一个身体圆
    state.snake, state.trail = _sample_trail(path, count)  # 保存接触点及完整身体轨迹
    state.direction = (math.cos(angle + turn * fraction), math.sin(angle + turn * fraction))  # 保存实际航向
    if ate:  # 更新吃食物后的状态
        state.score += 1  # 分数加一
        state.food = _random_food(state.rng, layout, state.snake)  # 刷新合法食物位置
        remaining = dt * (1 - fraction)  # 食物接触后还需继续前进的时间
        return _advance_step(state, layout, remaining, steering) if remaining > 1e-10 else False  # 完成本段剩余运动
    return collision is not None  # 碰撞后保持接触位置，供结束画面渲染


def advance_state(state: GameState, layout: Layout, dt: float, steering: Vector = (0.0, 0.0)) -> bool:  # 连续推进
    """把帧时长分成物理小步，直线、曲线、吃食物均采用实际几何轮廓。"""  # 函数说明
    if dt <= 0:  # 没有时间流逝
        return False  # 保持状态
    count = max(1, math.ceil(dt / config.PHYSICS_DT - 1e-10))  # 保证单步最大位移约半像素
    for _ in range(count):  # 稳定积分，不受屏幕帧率影响
        if _advance_step(state, layout, dt / count, steering):  # 连续推进并检测本段接触
            return True  # 碰撞立即停止剩余时间
    return False  # 本帧安全
