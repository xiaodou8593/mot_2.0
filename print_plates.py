import os

# 获取当前目录
current_dir = os.getcwd()
found_files = []

# 遍历当前目录及其所有子目录
for root, dirs, files in os.walk(current_dir):
    for file in files:
        if file.endswith('.mcfi'):
            # 构建相对路径
            relative_path = os.path.relpath(os.path.join(root, file), current_dir)
            relative_path = relative_path.replace('\\','/').replace('.mcfi','')
            found_files.append(relative_path)

if not found_files:
    print("未找到任何.mcfi文件")
else:
    print(', '.join(found_files))
    
input()