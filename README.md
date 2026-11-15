# 贪吃蛇（图形窗口版，pygame）

按照 `docs/userdocs/require.txt` 实现。**当前进度：实现步骤 1（界面）修改版，等待验收**。
验收通过后再继续步骤 2（WSAD 移动、吃食物、计分、撞墙结束）。

## 本次修改（对应验收反馈）

| 反馈 | 处理 |
| --- | --- |
| 比例为头 3、身体 3、食物 1.5，食物改空心 | 蛇头/蛇身圆形直径 = 3 个单位、食物空心正方形边长 = 1.5 个单位（1 单位 = 24 像素） |
| 改为图形窗口获得平滑美观图形 | 改为 pygame 窗口，圆形/三角形/箭头均用抗锯齿绘制，不再使用终端字符 |
| 暂停界面太大，缩至一半，透明度 70% | 暂停面板 400×168 像素（旧版约 800×336 的一半），面板 alpha ≈ 76（70% 透明） |
| 重试图标开口向左 | 圆形箭头缺口开在左侧，箭头指向左侧缺口 |
| 开始界面不应显示食物 | 开始界面只画棋盘与蛇，不绘制食物 |
| 结束保留结束画面、显示蛇和食物最后位置、透明度 70% | 结束界面保留最后一帧的蛇与食物位置，遮罩/面板 70% 透明，仍能看到最后位置 |
| 左上角暂停 UI 不美观，去掉 | 已移除左上角暂停图标，暂停操作通过底部操作指引说明 |
| Ubuntu 22.04 可运行 | 仅依赖 pygame-ce，Windows / Ubuntu 通用，提供 `run.sh` |

## 环境要求

- Windows 11 或 Ubuntu 22.04（需要图形桌面）
- Python 3.10+（开发验证环境为 Python 3.14.2）
- 依赖：`pygame-ce>=2.5.8`（`import pygame` 使用）

### 安装依赖

```powershell
# Windows
python -m pip install -r requirements.txt
```

```bash
# Ubuntu 22.04
sudo apt update
sudo apt install -y python3-pip fonts-noto-cjk   # fonts-noto-cjk 用于显示中文
python3 -m pip install -r requirements.txt
```

> 没有安装 pygame-ce 时运行会提示 `No module named 'pygame'`。
> Ubuntu 若缺少中文字体，文字可能显示为方框，安装 `fonts-noto-cjk` 即可。

## 运行方式

```powershell
# Windows：项目脚本（推荐）
.\scripts\run.cmd

# Windows：手动运行
$env:PYTHONPATH = "$PWD\src"
python -m greedy_snake
```

```bash
# Ubuntu 22.04：项目脚本
bash scripts/run.sh

# Ubuntu 22.04：手动运行
PYTHONPATH=src python3 -m greedy_snake
```

## 操作说明

| 操作 | 作用 |
| --- | --- |
| 开始界面按任意键 / 鼠标单击 | 开始游戏 |
| 游戏画面 `P` 连按两次 | 暂停（单次按 P 不会暂停，防止误触） |
| 游戏画面鼠标单击 | 暂停 |
| 暂停后按一次 `P` | 继续游戏 |
| 暂停后点击中间 ▶ / 空白处 | 继续游戏 |
| 暂停后点击右侧环形箭头 | 重试 |
| 暂停后点击左侧图标 | 退出 |
| 结束界面按 `R` / 鼠标单击 | 重试 |
| `Esc` / `Q` | 退出 |
| `1` / `2` / `3` / `4` | 预览用：直接切换 游戏 / 开始 / 暂停 / 结束 界面 |

> 步骤 1 只验收界面；WSAD 移动、吃食物、计分、撞墙结束等逻辑在步骤 2 实现。
> 数字键 1~4 仅用于验收时快速查看四种界面，正式玩法中不会使用。

## 界面截图（无需打开窗口）

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m greedy_snake --screenshots docs/screenshots --seed 7
```

生成的 PNG：`docs/screenshots/game.png`、`start.png`、`pause.png`、`over.png`（窗口尺寸 1200×720）。
也可以用 `python scripts\render_preview.py` 重新生成。

> 截图仅用于本地验收预览，`docs/screenshots/` 已加入 `.gitignore`，不会提交到仓库（见 `docs/userdocs/fix.txt` 第 3 条）。

## 运行测试

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s test -v
```

测试覆盖：布局与比例、初始状态、抗锯齿圆/重叠加深/空心方块/圆环缺口、四类界面的颜色与位置、
暂停触发（P 连按两次、单击切换）、暂停三个图标点击、结束重试、截图命令等。

## 明确尺寸（对应 docs/userdocs/fix.txt 的提醒）

窗口 1200×720，棋盘外框 1152×600，内部可活动区域 1128×576。单位为像素：

| 元素 | 形状 | 尺寸 |
| --- | --- | --- |
| 蛇头 | 蓝色实心**正圆** | 直径 72 像素（3 单位），半径 36 |
| 蛇身 | 黄色实心**正圆** | 直径 72 像素（3 单位） |
| 相邻圆形 | 圆心距 63 像素 | 重叠 9 像素 = 半径的 1/4，重叠区域颜色加深 |
| 食物 | 绿色**空心正方形** | 边长 36 像素（1.5 单位），边框 5 像素 |
| 墙 | 灰色实心边框 | 厚 12 像素 |
| 暂停面板 | 半透明圆角面板 | 400×168 像素（旧版的一半），70% 透明 |
| 暂停图标 | 像素矢量图标 | 左退出 / 中继续三角形 / 右重试环形箭头（开口向左） |
| 结束遮罩 | 70% 透明 | 保留蛇与食物最后位置 |

> 暂停面板与结束遮罩按“70% 透明（不透明度约 30%）”实现；如果你指的是“不透明度 70%”，
> 只需把 `config.TRANSPARENCY_70` 的用法对调即可，告诉我即可调整。

## 目录结构

```
GreedySnake/
├── docs/
│   ├── userdocs/
│   │   ├── require.txt          # 需求文件
│   │   ├── fix.txt              # 开发记录
│   │   └── chats.md             # 对话记录
│   └── screenshots/             # 界面 PNG 截图（本地预览用，已被 git 忽略）
├── scripts/
│   ├── run.cmd / run.ps1        # Windows 启动脚本
│   ├── run.sh                   # Ubuntu 启动脚本
│   └── render_preview.py        # 生成界面截图（开发用）
├── src/
│   └── greedy_snake/            # 游戏包
│       ├── __init__.py          # 包说明与版本
│       ├── __main__.py          # 命令行入口与截图模式
│       ├── app.py               # 窗口主循环、暂停触发与鼠标交互
│       ├── config.py            # 窗口、颜色、比例尺寸、透明度与文案
│       ├── graphics.py          # 抗锯齿圆/多边形、空心方块、圆环与中文文字
│       ├── layout.py            # 窗口、棋盘、可活动区域与面板布局
│       ├── screens.py           # 四类界面渲染（含暂停菜单与结束遮罩）
│       └── state.py             # 蛇圆心 / 食物 / 分数状态
├── test/                        # 单元测试
│   ├── test_app.py
│   ├── test_cli.py
│   ├── test_graphics.py
│   ├── test_layout.py
│   ├── test_screens.py
│   └── test_state.py
├── requirements.txt             # pygame-ce 依赖
├── .gitignore
└── pyproject.toml
```

## 实现进度

- [x] 实现步骤 1：墙、蛇、食物、暂停图形，分数、操作指引、开始 / 暂停 / 结束界面 UI（修改版，等待验收）
- [ ] 实现步骤 2：WSAD 移动、吃食物变长、撞墙 / 撞自己结束、分数增加
- [ ] 实现步骤 3：开始 / 暂停 / 结束流程（P 键与鼠标点击暂停、重试）
- [ ] 实现步骤 4：完整操作指引
- [ ] 实现步骤 5：进入后的教学关卡

## 说明

- 目前未执行 `git commit` / `git push`，也不会在未获许可时提交到远程。
- 暂停触发方式按补充要求实现：`P` 连按两次暂停、单次 `P` 退出暂停、鼠标单击切换暂停/继续。
- 圆形、三角形、环形箭头均使用 pygame 抗锯齿绘制，在 Windows 与 Ubuntu 上均平滑显示。
