import os
import sys
import ctypes
import ctypes.wintypes

def close_file_explorer():
    # 查找文件资源管理器窗口
    hwnd = ctypes.windll.user32.FindWindowW("CabinetWClass", None)
    if hwnd:
        # 发送关闭消息
        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        print("当前文件资源管理器窗口已关闭")
    else:
        print("未找到文件资源管理器窗口")

data_versions = {}

name = input("输入数据包名称：")
if name == '#':
    sys.exit(0)
namespace = input("请输入命名空间：")
if namespace == '#':
    sys.exit(0)

path = [name, 'data', namespace, 'function']
try:
    os.makedirs('/'.join(path))
except:
    pass
file = open(f'{name}/pack.mcmeta', 'w', encoding='utf-8')
file.write('''
{
    "pack":{
        "description": "version- by-",
        "pack_format": 71,
        "supported_formats": [71, 107],
        "min_format": 71,
        "max_format": [107, 1]
    }
}''')
file.close()

close_file_explorer()
os.startfile(f'{name}\\data\\{namespace}\\function')