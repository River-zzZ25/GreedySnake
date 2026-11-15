# 贪吃蛇（终端 TUI）

按照 `docs/require.txt` 实现，**当前进度：实现步骤 1（静态界面），等待验收**。验收通过后再继续步骤 2。

## 环境要求

- Windows 11（使用 Windows 控制台 / Windows Terminal 运行）
- Python 3.10+（开发验证环境为 Python 3.14.2）
- 仅使用 Python 标准库，无需 `pip install` 任何依赖

## 运行方式

```powershell
# 方式一：使用项目脚本（推荐，双击或在该目录的终端中执行）
.\scripts\run.cmd

# 方式二：使用 PowerShell 脚本（若系统执行策略允许）
.\scripts\run.ps1

# 方式三：手动设置模块路径后运行
$env:PYTHONPATH = "$PWD\src"
python -m greedy_snake
```

> Windows 默认执行策略可能禁止运行 `.ps1`，此时请使用 `run.cmd` 或方式三。

## 步骤 1 的预览操作

| 按键 | 作用 |
| --- | --- |
| 任意键（开始界面） | 进入游戏画面 |
| `1` / `2` / `3` / `4` | 直接切换：游戏画面 / 开始界面 / 暂停界面 / 结束界面 |
| `P` | 在游戏画面预览暂停界面（步骤 1 只做画面切换，真实暂停在步骤 3 实现） |
| `R` | 在失败界面预览重试（步骤 3 实现真实重试） |
| `Esc` / `Q` | 退出预览 |

> 步骤 1 只验收界面绘制，因此按键只用于切换四种界面，不包含真实的移动、计分与暂停逻辑。

## 单帧快照（无需交互，便于检查）

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m greedy_snake --snapshot game --seed 7          # 纯文本
python -m greedy_snake --snapshot pause --seed 7 --color  # 带 ANSI 颜色
```

`--snapshot` 可选值：`game`、`start`、`pause`、`over`；`--seed` 用于复现食物位置。

## 运行测试

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s test -v
```

共 37 个单元测试，覆盖画布绘制、四种界面布局（墙 / 蛇头 / 蛇身 / 食物颜色与位置）、
分数右上角、暂停面板左上角、预览按键流程与命令行快照。

## 生成界面预览图（可选）

```powershell
# 需要 Pillow；可用 DSH 自带 Python 执行，或自行安装 Pillow
python scripts\render_preview.py
```

生成的 PNG 位于 `docs/screenshots/`：`game.png`、`start.png`、`pause.png`、`over.png`。

## 目录结构

```
GreedySnake/
├── docs/
│   ├── require.txt              # 需求文件
│   └── screenshots/             # 四个界面的 PNG 预览图
├── scripts/
│   ├── run.ps1                  # 启动脚本
│   └── render_preview.py        # 生成 PNG 预览图（开发用）
├── src/
│   └── greedy_snake/            # 游戏包
│       ├── __init__.py          # 包说明与版本
│       ├── __main__.py          # 命令行入口
│       ├── app.py               # 界面预览切换循环
│       ├── canvas.py            # 字符画布与 ANSI 渲染
│       ├── config.py            # 尺寸、颜色与样式常量
│       ├── screens.py           # 四种界面的绘制
│       ├── state.py             # 蛇 / 食物 / 分数状态
│       └── terminal.py          # Windows 终端控制与按键读取
├── test/                        # 单元测试
│   ├── test_app.py
│   ├── test_canvas.py
│   ├── test_cli.py
│   └── test_screens.py
├── .gitignore
└── pyproject.toml
```

## 实现进度

- [x] 实现步骤 1：墙、蛇、食物、暂停图形，分数、操作指引、开始 / 暂停 / 失败界面 UI —— **等待验收**
- [ ] 实现步骤 2：WSAD 移动、吃食物变长、撞墙 / 撞自己结束、分数增加
- [ ] 实现步骤 3：开始 / 暂停 / 结束流程（P 键与鼠标点击暂停、重试）
- [ ] 实现步骤 4：完整操作指引
- [ ] 实现步骤 5：进入后的教学关卡

## 说明

- 目前未执行 `git commit` / `git push`，也不会在未获许可时提交到远程。
- 需求原文“鼠标电机或者按 P 键两次”的暂停触发方式存在歧义，将在步骤 3 前与用户确认。
