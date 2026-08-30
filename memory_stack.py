import os
import sys
import time
import ctypes
import shutil
import subprocess
from pathlib import Path

def print_folder_structure(path, indent="  ", show_files=True, ignore_dirs=None, level=0):
    """
    递归打印指定文件夹的结构。

    参数：
        path (str): 要打印的文件夹路径。
        indent (str): 每级缩进使用的字符串，默认为两个空格。
        show_files (bool): 是否显示文件名，默认为 True。
        ignore_dirs (list): 要忽略的文件夹名称列表，默认为 None。
        level (int): 内部使用的递归层级，调用时无需指定。
    """
    if ignore_dirs is None:
        ignore_dirs = []

    # 检查路径是否存在且为目录
    if not os.path.exists(path):
        print(f"错误：路径 '{path}' 不存在")
        return
    if not os.path.isdir(path):
        print(f"错误：'{path}' 不是一个文件夹")
        return

    # 获取当前文件夹名称并打印（根目录特殊处理）
    base_name = os.path.basename(os.path.normpath(path))
    if level == 0:
        print(base_name + "/")
    else:
        print(indent * (level - 1) + "|-- " + base_name + "/")

    try:
        items = sorted(os.listdir(path))  # 排序以保持输出一致
    except PermissionError:
        print(indent * level + "|-- [权限不足，无法访问]")
        return

    for item in items:
        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            if item in ignore_dirs:
                continue
            print_folder_structure(item_path, indent, show_files, ignore_dirs, level + 1)
        else:
            if show_files:
                print(indent * level + "|-- " + item)

def find_datapacks_directory():
    """从当前目录向上查找名为datapacks的目录"""
    current_path = Path.cwd()
    
    temp_cnt = 0
    while current_path != current_path.root:
        if temp_cnt > 50:
            return None
        if current_path.name == 'datapacks':
            return current_path
        
        for child in current_path.iterdir():
            if child.is_dir() and child.name == 'datapacks':
                return child
        
        current_path = current_path.parent
        temp_cnt += 1
    
    return None

def find_folders_with_memory_storage(datapacks_path):
    """在datapacks目录中查找包含memory_storage子文件夹的文件夹"""
    folders_with_memory_storage = []
    
    if not datapacks_path or not datapacks_path.exists():
        return folders_with_memory_storage
    
    for item in datapacks_path.iterdir():
        if item.is_dir():
            memory_storage_path = item / 'memory_storage'
            if memory_storage_path.exists() and memory_storage_path.is_dir():
                folders_with_memory_storage.append(item)
    
    return folders_with_memory_storage

def get_current_datapack_root():
    """从当前工作目录向上查找包含 pack.mcmeta 的目录，即数据包根目录"""
    path = Path.cwd()
    while path != path.root:
        if (path / 'pack.mcmeta').exists():
            return path
        path = path.parent
    return None

ex_paths = []
datapacks_path = find_datapacks_directory()
if datapacks_path:
    folders = find_folders_with_memory_storage(datapacks_path)
    if folders:
        for folder in folders:
            ex_paths.append(str(folder.absolute()))

# 模块文件夹预设 – 使用跨平台的路径解析
current_dir_parts = Path.cwd().parts  # 返回元组 ('C:', 'Users', ...) 或 ('/', 'home', ...)
anchor_found = False
sub_folders = []
for folder in reversed(current_dir_parts):
    if folder in ('functions', 'function'):
        anchor_found = True
        continue
    if anchor_found:
        namespace = folder
        break
    else:
        sub_folders.insert(0, folder)
if not anchor_found:
    print("路径不满足要求！")
    time.sleep(5)
    raise ValueError('path error')

# 构造模块前缀和模块名
if sub_folders:
    module_prefix = f"{namespace}:" + "/".join(sub_folders) + "/"
else:
    module_prefix = f"{namespace}:"
if sub_folders:
    module_name = sub_folders[-1]
else:
    module_name = namespace

print(f"project_name = {namespace}, module_prefix = {module_prefix}, module_name = {module_name}")

module_path = os.getcwd()
lib_path = os.path.dirname(os.path.abspath(__file__))

def folder_to_memory(folder_path):
    """将文件夹内容读取到内存"""
    folder_data = {}
    
    for root, dirs, files in os.walk(folder_path):
        relative_path = os.path.relpath(root, folder_path)
        if relative_path == '.':
            relative_path = ''
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.join(relative_path, file) if relative_path else file
            
            with open(file_path, 'rb') as f:
                folder_data[relative_file_path] = f.read()
    
    return folder_data

def memory_to_folder(folder_data, output_path):
    """将内存中的数据还原为文件夹"""
    os.makedirs(output_path, exist_ok=True)
    
    for relative_path, content in folder_data.items():
        file_path = os.path.join(output_path, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
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
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                merge_folders(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path)
        else:
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

# 修改终端标题（跨平台）
def modify_title():
    title = f'[.memory_stack.py - {os.getcwd()}]'
    if sys.platform == 'win32':
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass
    else:
        # 大多数类 Unix 终端支持 ANSI 转义序列设置标题
        try:
            sys.stdout.write(f'\033]0;{title}\007')
            sys.stdout.flush()
        except Exception:
            pass

modify_title()

# 记忆模板的数据结构
lst_memories = []

def read_memories():
    global ex_paths, lst_memories
    # 重新扫描所有数据包，更新 ex_paths
    datapacks_path = find_datapacks_directory()
    new_ex_paths = []
    if datapacks_path:
        for item in datapacks_path.iterdir():
            if item.is_dir() and (item / 'memory_storage').exists():
                new_ex_paths.append(str(item.absolute()))
    ex_paths = new_ex_paths   # 替换全局列表

    # 收集所有记忆名称
    folders = set()
    # 原有 lib_path/memory_storage
    lib_mem = os.path.join(lib_path, 'memory_storage')
    if os.path.isdir(lib_mem):
        for name in os.listdir(lib_mem):
            if os.path.isdir(os.path.join(lib_mem, name)):
                folders.add(name)
    # 所有数据包中的 memory_storage
    for root_path in ex_paths:
        mem_dir = os.path.join(root_path, 'memory_storage')
        if os.path.isdir(mem_dir):
            for name in os.listdir(mem_dir):
                if os.path.isdir(os.path.join(mem_dir, name)):
                    folders.add(name)
    lst_memories = sorted(folders)
    print(f'read {len(lst_memories)} memories.')

read_memories()

def save_memory():
    global stack, lst_memories, ex_paths

    if stack[-1] is None:
        print("无法储存空记忆")
        return

    # 获取当前数据包根目录
    root = get_current_datapack_root()
    if root is None:
        print("错误：当前目录不在任何数据包中（缺少 pack.mcmeta），无法保存。")
        return

    # 确定记忆名称
    if len(user_input) >= 2:
        # 直接指定名称
        memory_name = user_input[1].strip()
        if memory_name == '#':
            print('cancelled.')
            return
        if not memory_name:
            print("记忆名称不能为空。")
            return
        # 检查是否已存在（所有数据包 + lib）
        if memory_name in lst_memories:
            print(f"记忆 '{memory_name}' 已存在，不能重复保存。")
            return
    else:
        # 交互式命名
        while True:
            memory_name = input('请为记忆模板命名：').strip()
            if memory_name == '#':
                print('cancelled.')
                return
            if not memory_name:
                print("记忆名称不能为空。")
                continue
            if memory_name in lst_memories:
                print('命名不能与现有名字重复')
                continue
            break

    # 保存到当前数据包的 memory_storage
    save_dir = root / 'memory_storage' / memory_name
    save_dir.mkdir(parents=True, exist_ok=True)
    memory_to_folder(stack[-1], str(save_dir))
    print(f'memory {memory_name} saved to {save_dir}.')

    # 刷新记忆列表（使其立即可用）
    read_memories()

# ---------- 新增 delete_memory 函数 ----------
def delete_memory():
    """删除当前数据包 memory_storage 下的记忆（禁止删除其他位置）"""
    root = get_current_datapack_root()
    if root is None:
        print("错误：当前目录不在任何数据包中，无法删除。")
        return

    mem_dir = root / 'memory_storage'
    if not mem_dir.exists() or not mem_dir.is_dir():
        print("当前数据包中没有 memory_storage 目录。")
        return

    # 获取当前数据包内的所有记忆
    available = [d.name for d in mem_dir.iterdir() if d.is_dir()]
    if not available:
        print("当前数据包中没有可删除的记忆。")
        return

    global user_input
    if len(user_input) < 2:
        # 交互式选择
        print("当前数据包中的记忆：")
        for idx, name in enumerate(available, 1):
            print(f"{idx}. {name}")
        while True:
            choice = input("请输入要删除的记忆名称（或输入 # 取消）：").strip()
            if choice == '#':
                print("取消删除。")
                return
            if choice in available:
                memory_name = choice
                break
            print("输入的名称不在列表中，请重新输入。")
    else:
        memory_name = user_input[1]
        if memory_name not in available:
            print(f"记忆 '{memory_name}' 不在当前数据包中，无法删除。")
            return

    target_path = mem_dir / memory_name
    try:
        shutil.rmtree(target_path)
        print(f"已删除记忆: {memory_name}")
        read_memories()  # 刷新记忆列表
    except Exception as e:
        print(f"删除失败: {e}")

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

def read_stack_top():
    global stack
    stack.pop()
    input_path = os.path.join(module_path, '.mot_memory')
    if os.path.exists(input_path) and os.path.isdir(input_path):
        stack.append(folder_to_memory(input_path))
    else:
        stack.append(None)
    print('read memory stack top.')

read_stack_top()
    
def stack_sync_folder():
    input_path = os.path.join(module_path, '.mot_memory')
    delete_folder(input_path)
    if stack[-1] is None:
        return
    memory_to_folder(stack[-1], input_path)
    print('memory stack top synced.')

def push_memory():
    global user_input
    memory_name = user_input[0]
    input_path = os.path.join(lib_path, 'memory_storage', memory_name)
    if os.path.exists(input_path) and os.path.isdir(input_path):
        pass
    else:
        bool_flag = True
        for ex_path in ex_paths:
            input_path = os.path.join(ex_path, 'memory_storage', memory_name)
            if os.path.exists(input_path) and os.path.isdir(input_path):
                bool_flag = False
                break
        if bool_flag:
            print('memory not exit!')
            return
    stack.append(folder_to_memory(input_path))
    print(f'pushed memory: {memory_name}.')
    stack_sync_folder()

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
        path_a = os.path.join(lib_path, 'mem_a')
        path_b = os.path.join(lib_path, 'mem_b')
        memory_to_folder(mem_a, path_a)
        memory_to_folder(mem_b, path_b)
        merge_folders(path_b, path_a)
        mem_merge = folder_to_memory(path_a)
        delete_folder(path_a)
        delete_folder(path_b)
    stack.append(mem_merge)
    print('memory stack down merge.')
    stack_sync_folder()

def stack_pop():
    stack.pop()
    if len(stack)==0:
        stack.append(None)
    print('memory stack pop.')
    stack_sync_folder()

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f'created folder: {path}')
    except:
        pass

def create_folders():
    for path in user_input[1:]:
        create_folder(path)

def destroy_folder(path):
    try:
        shutil.rmtree(path)
        print(f"folder destroyed: {path}")
    except FileNotFoundError:
        print(f"folder not exist: {path}")
    except Exception as e:
        print(e)
        pass

def destroy_folders():
    for path in user_input[1:]:
        destroy_folder(path)

def extract_this_blocks(text: str) -> list[str]:
    """
    提取所有 _this:{...} 片段，支持花括号嵌套。
    返回匹配的完整片段列表。
    """
    blocks = []
    i = 0
    while i < len(text):
        pos = text.find("_this:", i)
        if pos == -1:
            break
        j = pos + len("_this:")
        if j < len(text) and text[j] == '{':
            brace_count = 1
            k = j + 1
            while k < len(text) and brace_count > 0:
                if text[k] == '{':
                    brace_count += 1
                elif text[k] == '}':
                    brace_count -= 1
                k += 1
            if brace_count == 0:
                blocks.append(text[pos:k])
                i = k
            else:
                # 未匹配到闭合花括号，跳过这个 "_this:"
                i = pos + 1
        else:
            i = pos + 1
    return blocks


def migrate_doc_mcfo():
    """
    迁移所有 .doc.mcfo 文件到 .mot_memory/templates 中，
    仅保留 _this:{...} 片段，其余删除。
    """
    templates_dir = os.path.join(module_path, '.mot_memory', 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # 递归收集所有 .doc.mcfo 文件（跳过 .mot_memory 目录）
    doc_files = []
    for root, dirs, files in os.walk(module_path):
        if '.mot_memory' in root.split(os.sep):
            continue
        for f in files:
            if f.endswith('.doc.mcfo'):
                doc_files.append(os.path.join(root, f))

    if not doc_files:
        print("未找到任何 .doc.mcfo 文件。")
        return

    for src_path in doc_files:
        rel_path = os.path.relpath(src_path, module_path)
        target_path = os.path.join(templates_dir, rel_path)

        # 读取源文件
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有 _this 块
        blocks = extract_this_blocks(content)

        if blocks:
            # 拼接（每个块换行分隔，保持清晰）
            new_content = '\n'.join(blocks)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已迁移: {rel_path}")
        else:
            # 无匹配片段，删除目标文件（若存在）
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"已删除（无有效内容）: {rel_path}")
            else:
                print(f"跳过（无内容且目标不存在）: {rel_path}")

    print("迁移完成。")

def init_global_settings():
    """初始化全局设置文件 .mot_memory/objects/global_settings.mcfo"""
    # 确保 .mot_memory 存在
    mot_path = os.path.join(module_path, '.mot_memory')
    if not os.path.exists(mot_path):
        os.makedirs(mot_path)

    objects_dir = os.path.join(mot_path, 'objects')
    os.makedirs(objects_dir, exist_ok=True)

    settings_path = os.path.join(objects_dir, 'global_settings.mcfo')
    content = """# 无需初始化/创建的数据位置
global_default: {
	positions: {
		<@s, x>, <@s, y>, <@s, z>,
		<@s, x, 1w>, <@s, y, 1w>, <@s, z, 1w>
	},
	caches: {
		[storage math:io xyz, ListDouble, 3],
		[storage math:io xyzw, ListFloat, 4],
		[storage math:io rec, ListCompound, 1],
		[storage math:io rotation, ListFloat, 2]
	}
}

# 整数常量
int_consts: {-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000, 10000}

# 实体对象的数据位置
entity_store_path:data

# 实体对象的类型
entity_type:item_display"""
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已生成全局设置文件: {settings_path}")

def transform_line(line: str) -> str:
    """
    逐行替换规则（待实现）
    当前直接返回原行，请根据需求修改此函数。
    """
    line = line.replace("$","")
    line = line.replace(f"#{module_prefix}", "#$(module_prefix)")
    line = line.replace(f'# {module_prefix}', '# $(module_prefix)')
    line = line.replace(f'function {module_prefix}', 'function $(module_prefix)')
    line = line.replace(f'storage {namespace}', 'storage $(project_name)')
    line = line.replace(f'storage $(project_name):io {module_name}_plate', 'storage $(project_name):io $(module_name)_plate')
    line = line.replace(f'storage $(project_name):class {module_name}_plate', 'storage $(project_name):class $(module_name)_plate')
    line = line.replace(f'{namespace}_{module_name}','$(project_name)_$(module_name)')
    return line


def rebuild_templates():
    """
    重建 .mot_memory/templates 目录：
      1. 备份旧的 templates（如果存在）
      2. 删除整个 .mot_memory
      3. 新建 .mot_memory/templates
      4. 遍历所有 .mcfunction 文件，生成对应的 .mcfi
         - 若旧 templates 中有同名文件，则直接复制
         - 否则逐行应用 transform_line 生成新文件
    """
    old_mot = os.path.join(module_path, '.mot_memory')
    backup_dir = os.path.join(module_path, '.mot_backup_tmp')

    # 1. 备份旧 templates
    if os.path.exists(old_mot):
        old_templates = os.path.join(old_mot, 'templates')
        if os.path.exists(old_templates) and os.path.isdir(old_templates):
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(old_templates, backup_dir)
        # 删除整个旧 .mot_memory
        delete_folder(old_mot)

    # 2. 创建新的 .mot_memory/templates
    new_mot = os.path.join(module_path, '.mot_memory')
    os.makedirs(new_mot, exist_ok=True)
    templates_dir = os.path.join(new_mot, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # 3. 遍历所有 .mcfunction 文件（递归）
    for root, dirs, files in os.walk(module_path):
        # 跳过新创建的 .mot_memory 目录，避免死循环
        if '.mot_memory' in root.split(os.sep):
            continue
        for file in files:
            if file.endswith('.mcfunction'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, module_path)
                # 目标 .mcfi 相对路径（仅改扩展名）
                mcfi_rel = os.path.splitext(rel_path)[0] + '.mcfi'
                target_path = os.path.join(templates_dir, mcfi_rel)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # 检查备份中是否有对应的 .mcfi
                if backup_dir and os.path.exists(backup_dir):
                    backup_file = os.path.join(backup_dir, mcfi_rel)
                    if os.path.exists(backup_file) and os.path.isfile(backup_file):
                        shutil.copy2(backup_file, target_path)
                        continue

                # 否则逐行转换
                with open(src_path, 'r', encoding='utf-8') as f_in:
                    lines = f_in.readlines()
                with open(target_path, 'w', encoding='utf-8') as f_out:
                    for line in lines:
                        f_out.write(transform_line(line))

    # 4. 清理备份
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    
    # 迁移对象格式文档
    migrate_doc_mcfo()
    init_global_settings()

    print('templates rebuilt.')

def inspect():
    print_folder_structure('.mot_memory/templates')

def stop():
    sys.exit(0)

def run_mot():
    print("mot1.2 running.")
    subprocess.run([sys.executable, os.path.join(lib_path, 'mot.py')])
    print('mot1.2 exit.')
    modify_title()
    read_stack_top()

def run_mcfo():
    print("create mcfo running.")
    subprocess.run([sys.executable, os.path.join(lib_path, 'create_mcfo.py')])
    print('create mcfo exit.')
    modify_title()
    read_stack_top()

def main():
    pass

print('\n')

# 命令映射表
command_table = {'':run_mot, 'run':run_mot, 'stop':stop, 'save':save_memory}
command_table |= {'push':stack_push, 'pop':stack_pop, 'merge':stack_merge}
command_table |= {'mread':read_memories, 'sread':read_stack_top, 'print':print_memories}
command_table |= {'make':create_folders, 'destroy':destroy_folders, 'inspect':inspect}
command_table |= {'mcfo':run_mcfo, 'build':rebuild_templates}
command_table |= {'delete': delete_memory}

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