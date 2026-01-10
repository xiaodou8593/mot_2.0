import os
import time

# 模块文件夹预设
current_dir = os.getcwd().split('\\')
# 搜索模块的命名空间和路径
anchor_found = False
sub_folders = []
for folder in current_dir[::-1]:
    
    # 找到functions/function文件夹停止
    if folder in ('functions', 'function'):
        anchor_found = True
        continue
    
    # functions以外文件夹的处理
    if anchor_found:
        namespace = folder
        break
    else:
        sub_folders.insert(0, folder)
if not anchor_found:
    print("路径不满足要求！")
    time.sleep(5)
    raise ValueError('path error')
# 生成函数前缀
prefix = f'{namespace}:' + '/'.join(sub_folders)
if sub_folders:
    prefix += '/'

module_name = namespace
if sub_folders:
    module_name = sub_folders[-1]

this_fill = """_this:{
	
}"""

try:
    with open('.mot_memory/doc_plate.mcfo', 'r', encoding='utf-8') as file:
        this_fill = file.read()
except:
    pass

file = open('.doc.mcfo', 'w', encoding='utf-8')
content = """#{}doc.mcfo

# {}临时对象
{}""".format(prefix,module_name,this_fill)
file.write(content)
file.close()