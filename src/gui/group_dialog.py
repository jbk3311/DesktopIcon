import copy
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class GroupDialog:
    UNGROUPED_LABEL = "(未分组)"

    def __init__(self, parent, group_manager, icons):
        self.parent = parent
        self.source_manager = group_manager
        self.icons = icons
        self.result = False

        self.working_groups = copy.deepcopy(group_manager.groups)
        self.working_assignments = dict(group_manager.assignments)
        # iid (str index) -> original icon path
        self._iid_to_path = {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("管理分组")
        self.dialog.geometry("700x460")
        self.dialog.minsize(660, 420)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.selected_group_id = tk.StringVar()
        self._build_ui()
        self._refresh_group_list()
        self._refresh_icon_assignments()

        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 先 pack btn_frame（side=BOTTOM），保证无论内容多高按钮始终可见
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="保存", command=self._on_save, width=12).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(btn_frame, text="取消", command=self._on_cancel, width=12).pack(
            side=tk.RIGHT
        )

        # 内容区再 expand 填充剩余空间
        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        # ---- 左：分组列表 ----
        left_frame = ttk.LabelFrame(content, text="分组列表", padding="8")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8))

        self.group_listbox = tk.Listbox(
            left_frame, width=22, height=12, exportselection=False
        )
        self.group_listbox.pack(fill=tk.BOTH, expand=True)
        self.group_listbox.bind("<<ListboxSelect>>", self._on_group_selected)

        group_btn_frame = ttk.Frame(left_frame)
        group_btn_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(
            group_btn_frame, text="新建", command=self._create_group, width=8
        ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(
            group_btn_frame, text="重命名", command=self._rename_group, width=8
        ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(
            group_btn_frame, text="删除", command=self._delete_group, width=8
        ).pack(side=tk.LEFT)

        # ---- 右：图标归属 ----
        right_frame = ttk.LabelFrame(content, text="图标归属", padding="8")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "group")
        self.icon_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self.icon_tree.heading("name", text="图标名称")
        self.icon_tree.heading("group", text="所属分组")
        self.icon_tree.column("name", width=280, anchor="w")
        self.icon_tree.column("group", width=160, anchor="w")
        self.icon_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        icon_scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.icon_tree.yview
        )
        icon_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.icon_tree.configure(yscrollcommand=icon_scroll.set)

        assign_frame = ttk.Frame(right_frame)
        assign_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(assign_frame, text="将选中图标设为:").pack(side=tk.LEFT)
        self.assign_var = tk.StringVar(value=self.UNGROUPED_LABEL)
        self.assign_combo = ttk.Combobox(
            assign_frame,
            textvariable=self.assign_var,
            state="readonly",
            width=24,
        )
        self.assign_combo.pack(side=tk.LEFT, padx=(8, 8))
        ttk.Button(
            assign_frame, text="应用", command=self._apply_assignment
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _regrab(self):
        """simpledialog/messagebox 会释放全局 grab，操作后恢复到本对话框。"""
        try:
            self.dialog.grab_set()
        except tk.TclError:
            pass

    def _get_group_by_id(self, group_id):
        for group in self.working_groups:
            if group["id"] == group_id:
                return group
        return None

    def _name_exists(self, name, exclude_id=None):
        normalized = name.strip()
        return any(
            g["name"] == normalized and g["id"] != exclude_id
            for g in self.working_groups
        )

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------

    def _refresh_group_list(self):
        self.group_listbox.delete(0, tk.END)
        for group in self.working_groups:
            self.group_listbox.insert(tk.END, group["name"])

        group_names = [self.UNGROUPED_LABEL] + [
            g["name"] for g in self.working_groups
        ]
        self.assign_combo["values"] = group_names
        if self.assign_var.get() not in group_names:
            self.assign_var.set(self.UNGROUPED_LABEL)

    def _refresh_icon_assignments(self):
        for item in self.icon_tree.get_children():
            self.icon_tree.delete(item)

        self._iid_to_path = {}

        for idx, icon in enumerate(self.icons):
            # 使用整数索引作为 iid，避免 Windows 路径中的反斜杠被 Tcl 转义
            iid = str(idx)
            self._iid_to_path[iid] = icon["path"]

            group_id = self.working_assignments.get(icon["path"])
            group_name = self.UNGROUPED_LABEL
            if group_id:
                group = self._get_group_by_id(group_id)
                if group:
                    group_name = group["name"]
                else:
                    self.working_assignments.pop(icon["path"], None)

            self.icon_tree.insert(
                "",
                tk.END,
                iid=iid,
                values=(icon["name"], group_name),
            )

    # ------------------------------------------------------------------
    # Event handlers — groups
    # ------------------------------------------------------------------

    def _on_group_selected(self, event=None):
        selection = self.group_listbox.curselection()
        if not selection:
            self.selected_group_id.set("")
            return
        index = selection[0]
        if index < len(self.working_groups):
            self.selected_group_id.set(self.working_groups[index]["id"])

    def _create_group(self):
        name = simpledialog.askstring("新建分组", "请输入分组名称:", parent=self.dialog)
        self._regrab()
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("提示", "分组名称不能为空", parent=self.dialog)
            self._regrab()
            return
        if self._name_exists(name):
            messagebox.showwarning("提示", "分组名称已存在", parent=self.dialog)
            self._regrab()
            return

        group = {"id": uuid.uuid4().hex[:8], "name": name}
        self.working_groups.append(group)
        self._refresh_group_list()
        self.group_listbox.selection_clear(0, tk.END)
        self.group_listbox.selection_set(tk.END)
        self.selected_group_id.set(group["id"])

    def _rename_group(self):
        selection = self.group_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要重命名的分组", parent=self.dialog)
            self._regrab()
            return

        index = selection[0]
        group = self.working_groups[index]
        name = simpledialog.askstring(
            "重命名分组",
            "请输入新的分组名称:",
            initialvalue=group["name"],
            parent=self.dialog,
        )
        self._regrab()
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("提示", "分组名称不能为空", parent=self.dialog)
            self._regrab()
            return
        if self._name_exists(name, exclude_id=group["id"]):
            messagebox.showwarning("提示", "分组名称已存在", parent=self.dialog)
            self._regrab()
            return

        group["name"] = name
        self._refresh_group_list()
        self._refresh_icon_assignments()
        self.group_listbox.selection_set(index)

    def _delete_group(self):
        selection = self.group_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要删除的分组", parent=self.dialog)
            self._regrab()
            return

        index = selection[0]
        group = self.working_groups[index]
        confirmed = messagebox.askyesno(
            "确认删除",
            f"确定删除分组「{group['name']}」吗？\n组内图标将变为未分组。",
            parent=self.dialog,
        )
        self._regrab()
        if not confirmed:
            return

        group_id = group["id"]
        self.working_groups.pop(index)
        self.working_assignments = {
            path: gid
            for path, gid in self.working_assignments.items()
            if gid != group_id
        }
        self.selected_group_id.set("")
        self._refresh_group_list()
        self._refresh_icon_assignments()

    # ------------------------------------------------------------------
    # Event handlers — assignments
    # ------------------------------------------------------------------

    def _resolve_group_id_from_label(self, label):
        if label == self.UNGROUPED_LABEL:
            return None
        for group in self.working_groups:
            if group["name"] == label:
                return group["id"]
        return None

    def _apply_assignment(self):
        selected_iids = self.icon_tree.selection()
        if not selected_iids:
            messagebox.showinfo("提示", "请先在右侧选择图标", parent=self.dialog)
            self._regrab()
            return

        group_id = self._resolve_group_id_from_label(self.assign_var.get())
        for iid in selected_iids:
            path = self._iid_to_path.get(iid)
            if path is None:
                continue
            if group_id is None:
                self.working_assignments.pop(path, None)
            else:
                self.working_assignments[path] = group_id

        self._refresh_icon_assignments()

    # ------------------------------------------------------------------
    # Save / Cancel
    # ------------------------------------------------------------------

    def _on_save(self):
        self.source_manager.groups = copy.deepcopy(self.working_groups)
        self.source_manager.assignments = dict(self.working_assignments)
        if not self.source_manager.save():
            messagebox.showerror("错误", "保存分组配置失败", parent=self.dialog)
            self._regrab()
            return

        self.result = True
        self.dialog.destroy()

    def _on_cancel(self):
        self.result = False
        self.dialog.destroy()

    def show(self):
        self.parent.wait_window(self.dialog)
        return self.result
