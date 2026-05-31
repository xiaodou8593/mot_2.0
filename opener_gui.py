import os
import sys
import subprocess
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def stop(x):
    """
    结束程序
    """
    root.destroy()

class SlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件槽位管理器")
        self.root.geometry("700x400")
        self.root.resizable(True, True)

        # 配置文件路径（位于脚本同级目录）
        self.config_path = Path(__file__).parent / "slot_config.json"

        # 槽位数据：存储每个槽位的文件路径 (None 表示未设置)
        self.slots = [None] * 5
        self.current_slot = 0  # 当前选中的槽位索引 (0-4)

        # 存储每个槽位对应的显示标签 (用于更新路径文本)
        self.path_labels = []

        self.create_widgets()
        self.bind_shortcuts()
        self.load_slots()          # 加载上次保存的配置
        self.update_highlight()

        # 窗口关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """创建界面组件：5个槽位区域"""
        for i in range(5):
            slot_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=5, pady=5)
            slot_frame.pack(fill=tk.X, padx=10, pady=5, expand=False)
            slot_frame.slot_index = i
            slot_frame.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))
            for child in (slot_frame,):
                child.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))

            title_label = tk.Label(slot_frame, text=f"槽位 {i+1}", font=("Arial", 10, "bold"), width=8, anchor="w")
            title_label.pack(side=tk.LEFT, padx=(0, 10))
            title_label.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))

            path_var = tk.StringVar(value="(未设置)")
            path_label = tk.Label(slot_frame, textvariable=path_var, anchor="w", relief=tk.SUNKEN,
                                  bg="white", fg="black", padx=5, pady=2)
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            path_label.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))
            self.path_labels.append(path_var)

            select_btn = tk.Button(slot_frame, text="选择文件", command=lambda idx=i: self.select_file(idx))
            select_btn.pack(side=tk.LEFT, padx=(0, 5))
            select_btn.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))

            clear_btn = tk.Button(slot_frame, text="清除", command=lambda idx=i: self.clear_slot(idx))
            clear_btn.pack(side=tk.LEFT)
            clear_btn.bind("<Button-1>", lambda e, idx=i: self.set_current_slot(idx))

            slot_frame.bg_original = slot_frame.cget("bg")
            setattr(self, f"slot_frame_{i}", slot_frame)

    def bind_shortcuts(self):
        self.root.bind("<Control-Left>", self.prev_slot)
        self.root.bind("<Control-Right>", self.next_slot)
        self.root.bind("<Control-Up>", self.prev_slot)
        self.root.bind("<Control-Down>", self.next_slot)
        self.root.bind("<Return>", lambda e: self.open_current_slot())
        self.root.bind("<Control-e>",stop)

    def set_current_slot(self, index):
        if 0 <= index < 5:
            self.current_slot = index
            self.update_highlight()

    def prev_slot(self, event=None):
        self.current_slot = (self.current_slot - 1) % 5
        self.update_highlight()

    def next_slot(self, event=None):
        self.current_slot = (self.current_slot + 1) % 5
        self.update_highlight()

    def update_highlight(self):
        for i in range(5):
            frame = getattr(self, f"slot_frame_{i}")
            if i == self.current_slot:
                frame.config(bg="lightblue", highlightbackground="blue", highlightthickness=2)
                for child in frame.winfo_children():
                    try:
                        child.config(bg="lightblue")
                    except tk.TclError:
                        pass
            else:
                frame.config(bg=frame.bg_original, highlightthickness=0)
                for child in frame.winfo_children():
                    try:
                        child.config(bg=frame.bg_original)
                    except tk.TclError:
                        pass

    def select_file(self, idx):
        file_path = filedialog.askopenfilename(title=f"选择槽位 {idx+1} 的文件")
        if file_path:
            self.slots[idx] = file_path
            display_path = self.shorten_path(file_path)
            self.path_labels[idx].set(display_path)
            self.save_slots()   # 立即保存配置

    def clear_slot(self, idx):
        self.slots[idx] = None
        self.path_labels[idx].set("(未设置)")
        self.save_slots()       # 立即保存配置

    def shorten_path(self, path, max_len=50):
        if len(path) <= max_len:
            return path
        p = Path(path)
        name = p.name
        parent = p.parent.name
        if parent:
            return f".../{parent}/{name}"
        else:
            return f".../{name}"

    def open_current_slot(self):
        path = self.slots[self.current_slot]
        if not path:
            messagebox.showwarning("警告", f"槽位 {self.current_slot+1} 未设置文件")
            return
        if not os.path.exists(path):
            messagebox.showerror("错误", f"文件不存在:\n{path}")
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("错误", f"打开文件失败:\n{e}")

    def load_slots(self):
        """从 JSON 文件加载槽位信息"""
        if not self.config_path.exists():
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 预期 data 是一个包含 5 个元素的列表（元素为路径字符串或 null）
            if isinstance(data, list) and len(data) == 5:
                for i, path in enumerate(data):
                    if path is not None and os.path.exists(path):
                        self.slots[i] = path
                        self.path_labels[i].set(self.shorten_path(path))
                    else:
                        self.slots[i] = None
                        self.path_labels[i].set("(未设置)")
            else:
                print("配置文件格式无效，使用默认空槽位")
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_slots(self):
        """将当前槽位信息保存到 JSON 文件"""
        data = [path if path else None for path in self.slots]  # None 转为 null
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def on_close(self):
        """窗口关闭时保存配置并销毁窗口"""
        self.save_slots()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SlotApp(root)
    # 确保窗口启动时获得焦点，快捷键可用
    root.lift()
    root.after(100, root.focus_force)
    root.mainloop()