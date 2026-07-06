"""
待办事项管理器 (Todo App) — 面向对象版
命令行交互，数据保存到 JSON 文件。
"""

import json
import os


PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
PRIORITY_ICON = {"高": "🔴", "中": "🟡", "低": "🟢"}


class TodoManager:
    """待办事项管理器"""

    def __init__(self, data_file="todos.json"):
        self.data_file = data_file
        self.todos = []
        self._load()

    # ─── 数据持久化 ──────────────────────────────────

    def _load(self):
        """从文件加载待办列表"""
        if not os.path.exists(self.data_file):
            self.todos = []
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.todos = json.load(f)
        except (json.JSONDecodeError, Exception):
            print("数据文件损坏，将重新创建。")
            self.todos = []

    def _save(self):
        """保存待办列表到文件"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)

    # ─── 核心功能 ──────────────────────────────────

    def add(self, title, priority="中"):
        """添加新待办"""
        if not title or not title.strip():
            return False, "内容不能为空！"
        if priority not in PRIORITY_ORDER:
            priority = "中"

        todo = {
            "id": len(self.todos) + 1,
            "title": title.strip(),
            "priority": priority,
            "done": False,
        }
        self.todos.append(todo)
        self._save()
        return True, f"✅ 已添加：[{priority}] {title.strip()}"

    def list_all(self):
        """列出所有待办（按优先级排序），返回格式化文本"""
        if not self.todos:
            return "📭 暂无待办事项"

        sorted_todos = sorted(
            self.todos,
            key=lambda t: (t.get("done", False), PRIORITY_ORDER.get(t.get("priority", "中"), 1)),
        )

        lines = [f"\n{'ID':<4} {'优先级':<6} {'状态':<8} {'内容'}", "-" * 50]
        for todo in sorted_todos:
            pri = todo.get("priority", "中")
            icon = PRIORITY_ICON.get(pri, "🟡")
            status = "✅ 已完成" if todo["done"] else "⬜ 未完成"
            lines.append(f"{todo['id']:<4} {icon:<6} {status:<8} {todo['title']}")
        return "\n".join(lines)

    def mark_done(self, todo_id):
        """标记待办为已完成"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                if todo["done"]:
                    return False, "该待办已经是完成状态"
                todo["done"] = True
                self._save()
                return True, f"✅ 已标记完成：{todo['title']}"
        return False, f"未找到 ID 为 {todo_id} 的待办"

    def delete(self, todo_id):
        """删除待办"""
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                removed = self.todos.pop(i)
                self._save()
                return True, f"🗑️ 已删除：{removed['title']}"
        return False, f"未找到 ID 为 {todo_id} 的待办"

    # ─── 交互界面 ──────────────────────────────────

    def run(self):
        """启动命令行交互界面"""
        while True:
            print("\n" + "=" * 30)
            print("      待办事项管理器")
            print("=" * 30)
            print("1. 添加待办（支持优先级）")
            print("2. 列出待办（按优先级排序）")
            print("3. 标记完成")
            print("4. 删除待办")
            print("5. 退出")
            print("=" * 30)

            choice = input("请选择操作 (1-5)：").strip()

            if choice == "1":
                self._interactive_add()
            elif choice == "2":
                print(self.list_all())
            elif choice == "3":
                self._interactive_mark_done()
            elif choice == "4":
                self._interactive_delete()
            elif choice == "5":
                print("👋 再见！")
                break
            else:
                print("无效选择，请输入 1-5")

    def _interactive_add(self):
        """交互式添加待办"""
        title = input("请输入待办事项内容：").strip()
        if not title:
            print("内容不能为空！")
            return
        priority = input("请输入优先级 (高/中/低，默认中)：").strip() or "中"
        success, msg = self.add(title, priority)
        print(msg)

    def _interactive_mark_done(self):
        """交互式标记完成"""
        print(self.list_all())
        if not self.todos:
            return
        try:
            tid = int(input("请输入要标记完成的 ID："))
            success, msg = self.mark_done(tid)
            print(msg)
        except ValueError:
            print("请输入有效的数字 ID")

    def _interactive_delete(self):
        """交互式删除待办"""
        print(self.list_all())
        if not self.todos:
            return
        try:
            tid = int(input("请输入要删除的 ID："))
            success, msg = self.delete(tid)
            print(msg)
        except ValueError:
            print("请输入有效的数字 ID")


def main():
    try:
        manager = TodoManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"发生未知错误：{e}")
        exit(1)


if __name__ == "__main__":
    main()
