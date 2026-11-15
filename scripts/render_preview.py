"""生成四类界面的 PNG 预览图（开发/验收用，执行后输出到 docs/screenshots）。"""  # 模块说明

import pathlib  # 路径处理
import sys  # 修改模块搜索路径

ROOT = pathlib.Path(__file__).resolve().parents[1]  # 项目根目录
sys.path.insert(0, str(ROOT / "src"))  # 让脚本可以导入 greedy_snake 包

from greedy_snake.__main__ import render_screenshots  # 界面截图渲染函数

if __name__ == "__main__":  # 直接运行脚本
    raise SystemExit(render_screenshots(ROOT / "docs" / "screenshots", 7))  # 生成截图并返回退出码
