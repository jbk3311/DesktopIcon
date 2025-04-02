# src/gui/widgets.py
import tkinter as tk
from tkinter import ttk

class ScrollableIconFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="桌面图标", padding="5")
        self.create_widgets()
        self.icon_checkboxes = {}
        self.all_var = None
    
    def create_widgets(self):
        # 创建滚动条和画布
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor='nw',
            width=self.canvas.winfo_reqwidth()
        )
        
        # 绑定鼠标滚轮事件
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)
        
        self.inner_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _bind_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')
    
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def update_icons(self, icons):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        
        self.icon_checkboxes.clear()
        
        # 全选复选框
        self.all_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.inner_frame,
            text="全选/取消全选",
            variable=self.all_var,
            command=self.toggle_all
        ).pack(anchor='w', pady=2)
        
        # 图标复选框
        for icon in icons:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(
                self.inner_frame,
                text=icon['name'],
                variable=var,
                command=self.check_all_state
            )
            cb.pack(anchor='w', pady=2)
            self.icon_checkboxes[icon['path']] = {
                'checkbox': cb,
                'variable': var
            }
    
    def toggle_all(self):
        state = self.all_var.get()
        for data in self.icon_checkboxes.values():
            data['variable'].set(state)
    
    def check_all_state(self):
        if self.icon_checkboxes:
            all_selected = all(
                data['variable'].get() 
                for data in self.icon_checkboxes.values()
            )
            self.all_var.set(all_selected)
    
    def get_selected_items(self):
        return [
            path for path, data in self.icon_checkboxes.items()
            if data['variable'].get()
        ]