import json
import os
import uuid

from src.config import GROUPS_FILE


class GroupManager:
    UNGROUPED_ID = "__ungrouped__"

    def __init__(self):
        self.groups_file = GROUPS_FILE
        self.groups = []
        self.assignments = {}
        self.load()

    def load(self):
        """加载分组配置"""
        try:
            if os.path.exists(self.groups_file):
                with open(self.groups_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.groups = data.get("groups", [])
                self.assignments = data.get("assignments", {})
            else:
                self.groups = []
                self.assignments = {}
        except Exception as e:
            print(f"加载分组配置失败: {str(e)}")
            self.groups = []
            self.assignments = {}

    def save(self):
        """保存分组配置"""
        try:
            os.makedirs(os.path.dirname(self.groups_file), exist_ok=True)
            with open(self.groups_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"groups": self.groups, "assignments": self.assignments},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            return True
        except Exception as e:
            print(f"保存分组配置失败: {str(e)}")
            return False

    def get_groups(self):
        return list(self.groups)

    def get_group_by_id(self, group_id):
        for group in self.groups:
            if group["id"] == group_id:
                return group
        return None

    def get_group_name(self, group_id):
        group = self.get_group_by_id(group_id)
        return group["name"] if group else None

    def _name_exists(self, name, exclude_id=None):
        normalized = name.strip()
        return any(
            g["name"] == normalized and g["id"] != exclude_id for g in self.groups
        )

    def create_group(self, name):
        name = name.strip()
        if not name:
            raise ValueError("分组名称不能为空")
        if self._name_exists(name):
            raise ValueError("分组名称已存在")

        group = {"id": uuid.uuid4().hex[:8], "name": name}
        self.groups.append(group)
        self.save()
        return group

    def rename_group(self, group_id, name):
        name = name.strip()
        if not name:
            raise ValueError("分组名称不能为空")
        if self._name_exists(name, exclude_id=group_id):
            raise ValueError("分组名称已存在")

        group = self.get_group_by_id(group_id)
        if not group:
            raise ValueError("分组不存在")

        group["name"] = name
        self.save()

    def delete_group(self, group_id):
        group = self.get_group_by_id(group_id)
        if not group:
            raise ValueError("分组不存在")

        self.groups = [g for g in self.groups if g["id"] != group_id]
        self.assignments = {
            path: gid
            for path, gid in self.assignments.items()
            if gid != group_id
        }
        self.save()

    def assign_icon(self, path, group_id):
        if group_id is None:
            self.unassign_icon(path)
            return

        if not self.get_group_by_id(group_id):
            raise ValueError("分组不存在")

        self.assignments[path] = group_id
        self.save()

    def unassign_icon(self, path):
        if path in self.assignments:
            del self.assignments[path]
            self.save()

    def get_icon_group(self, path):
        return self.assignments.get(path)

    def get_group_icons(self, group_id, valid_paths=None):
        valid_set = set(valid_paths) if valid_paths is not None else None
        result = []
        for path, gid in self.assignments.items():
            if gid != group_id:
                continue
            if valid_set is not None and path not in valid_set:
                continue
            result.append(path)
        return result

    def get_ungrouped_icons(self, valid_paths):
        valid_set = set(valid_paths)
        assigned = set(self.assignments.keys())
        return [path for path in valid_paths if path not in assigned]

    def prune_stale_assignments(self, valid_paths):
        valid_set = set(valid_paths)
        stale = [path for path in self.assignments if path not in valid_set]
        if not stale:
            return False

        for path in stale:
            del self.assignments[path]

        self.save()
        return True
