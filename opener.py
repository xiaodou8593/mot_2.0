import subprocess
import sys
import os
from pathlib import Path

def open_with_default_app(file_path):
    """用系统默认程序打开文件"""
    path = Path(file_path).resolve()  # 转换为绝对路径
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    if sys.platform == "win32":  # Windows
        os.startfile(str(path))
    elif sys.platform == "darwin":  # macOS
        subprocess.run(["open", str(path)])
    else:  # Linux 及其他 Unix-like
        subprocess.run(["xdg-open", str(path)])

# 使用示例
open_with_default_app(r"D:\games\Minecraft\.minecraft\versions\1.21.11\saves\minigame_sys\datapacks\vve3.0\data\vve\function\_consts.mcfunction")