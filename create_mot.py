import os
import sys
import shutil

# 获取路径参数
module_path = os.getcwd()
lib_path = sys.argv[1]

# 复制文件到目标文件夹
source = lib_path + '\\.mot.py'
destination = module_path + '\\.mot.py'

shutil.copy(source, destination)