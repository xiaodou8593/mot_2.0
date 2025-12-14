import os
import sys
import ctypes
import pickle
import shutil
import subprocess

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

# 获取路径参数
module_path = os.getcwd()
lib_path = sys.argv[1]

def folder_to_memory(folder_path):
    """将文件夹内容读取到内存"""
    folder_data = {}
    
    for root, dirs, files in os.walk(folder_path):
        # 处理目录结构
        relative_path = os.path.relpath(root, folder_path)
        if relative_path == '.':
            relative_path = ''
        
        # 读取文件内容
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.join(relative_path, file) if relative_path else file
            
            with open(file_path, 'rb') as f:
                folder_data[relative_file_path] = f.read()
    
    return folder_data

def memory_to_folder(folder_data, output_path):
    """将内存中的数据还原为文件夹"""
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    for relative_path, content in folder_data.items():
        file_path = os.path.join(output_path, relative_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件内容
        with open(file_path, 'wb') as f:
            f.write(content)

def merge_folders(src_folder, dst_folder):
    """
    将源文件夹内容合并到目标文件夹
    """
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dst_path = os.path.join(dst_folder, item)
        
        if os.path.isdir(src_path):
            # 如果是文件夹，递归合并
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                merge_folders(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path)
        else:
            # 如果是文件，复制文件
            shutil.copy2(src_path, dst_path)

def delete_folder(folder_path):
    """
    删除文件夹
    """
    try:
        os.rmdir(folder_path)
    except:
        try:
            shutil.rmtree(folder_path)
        except:
            pass

# 修改终端标题
def modify_title():
    title = f'[.memory_stack.py - {os.getcwd()}]'
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass  # 如果失败则静默处理
modify_title()

# 记忆模板的数据结构
lst_memories = []
# 读取储存的记忆模板
def read_memories():
    """
    查找指定目录下的直接子文件夹（不包含子文件夹的子文件夹）
    """
    global lst_memories
    folders = []
    directory = lib_path+'\\memory_storage'
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item)
    lst_memories = folders
    print(f'read {len(lst_memories)} memories.')
read_memories()

# 储存当前记忆
def save_memory():
    if stack[-1] is None:
        print("无法储存空记忆")
        return
    while True:
        memory_name = input('请为记忆模板命名：')
        if memory_name in lst_memories:
            print('命名不能与现有名字重复')
        elif memory_name == '#':
            print('cancelled.')
            return
        break
    input_path = lib_path + '\\memory_storage\\' + f'{memory_name}'
    os.makedirs(input_path, exist_ok=True)
    memory_to_folder(stack[-1], input_path)
    print(f'memory {memory_name} saved.')
    read_memories()

# 输出所有记忆
def print_memories():
    index = 0
    for _ in range((len(lst_memories)+2)//3):
        line_string = ''
        for __ in range(3):
            if index >= len(lst_memories):
                break
            line_string += f'{index+1}.{lst_memories[index]}\t'
            index += 1
        print((line_string))

# 栈的数据结构
stack = [None]
# 读取栈顶元素
def read_stack_top():
    global stack
    stack.pop()
    input_path = module_path + '\\.mot_memory'
    if os.path.exists(input_path) and os.path.isdir(input_path):
        stack.append(folder_to_memory(input_path))
    else:
        stack.append(None)
    print('read memory stack top.')
read_stack_top()
    
# 栈顶元素同步到文件夹
def stack_sync_folder():
    input_path = module_path + '\\.mot_memory'
    delete_folder(input_path)
    if stack[-1] is None:
        return
    memory_to_folder(stack[-1], input_path)
    print('memory stack top synced.')

# 指定记忆模板入栈
def push_memory():
    global user_input
    memory_name = user_input[0]
    input_path = lib_path + '\\memory_storage\\' + f'{memory_name}'
    if os.path.exists(input_path) and os.path.isdir(input_path):
        pass
    else:
        print('memory not exit!')
        return
    stack.append(folder_to_memory(input_path))
    print(f'pushed memory: {memory_name}.')
    stack_sync_folder()

# 选择记忆模板入栈
def stack_push():
    global user_input
    if len(user_input)<2:
        print_memories()
        while True:
            memory_name = input('请选择记忆模板(输入名称)：')
            if memory_name == '#':
                print('cancelled.')
                return
            if memory_name in lst_memories:
                break
            print('记忆模板不存在！')
        user_input = [memory_name]
    else:
        user_input = [user_input[1]]
    push_memory()

# 向下合并
def stack_merge():
    if len(stack)<2:
        return
    mem_a = stack.pop()
    mem_b = stack.pop()
    if mem_a is None:
        mem_merge = mem_b
    elif mem_b is None:
        mem_merge = mem_a
    else:
        path_a = lib_path + '\\mem_a'
        path_b = lib_path + '\\mem_b'
        memory_to_folder(mem_a, path_a)
        memory_to_folder(mem_b, path_b)
        merge_folders(path_b, path_a)
        mem_merge = folder_to_memory(path_a)
        delete_folder(path_a)
        delete_folder(path_b)
    stack.append(mem_merge)
    print('memory stack down merge.')
    stack_sync_folder()

# 弹出栈顶元素
def stack_pop():
    stack.pop()
    if len(stack)==0:
        stack.append(None)
    print('memory stack pop.')
    stack_sync_folder()

# 创建文件夹
def create_folder(path):
    try:
        os.makedirs(path,exist_ok=True)
        print(f'created folder: {path}')
    except:
        pass
def create_folders():
    for path in user_input[1:]:
        create_folder(path)

# 删除文件夹
def destroy_folder(path):
    try:
        shutil.rmtree(path)
        print(f"folder destroyed: {path}")
    except FileNotFoundError:
        print(f"folder not exist: {path}")
    except Exception as e:
        pass
def destroy_folders():
    for path in user_input[1:]:
        destroy_folder(path)

def stop():
    """
    结束程序
    """
    sys.exit(0)

def run_mot():
    """
    运行mot1.1终端
    """
    print("mot1.1 running.")
    subprocess.run(['python', lib_path+'\\.mot.py'])
    print('mot1.1 exit.')
    modify_title()
    read_stack_top()

print('\n')

# 命令映射表
command_table = {'':run_mot, 'run':run_mot, 'stop':stop, 'save':save_memory}
command_table |= {'push':stack_push, 'pop':stack_pop, 'merge':stack_merge}
command_table |= {'mread':read_memories, 'sread':read_stack_top, 'print':print_memories}
command_table |= {'make':create_folders, 'destroy':destroy_folders}
# 主程序
while True:
    user_input = input().split(' ')
    command = user_input[0]
    if command in command_table:
        command_table[command]()
    elif command in lst_memories:
        push_memory()
    else:
        print(f'未识别命令: {command}')
    print('\n')