"""
待办事项管理器 (Todo App)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
遵循「约定式提交」风格组织代码结构
"""

import json
import os
import time


# ═══════════════════════════════════════════
# feat(config): 基础配置与常量
# ═══════════════════════════════════════════

DATA_FILE = "todos.json"
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
PRIORITY_ICON = {"高": "🔴", "中": "🟡", "低": "🟢"}
PRIORITY_LABEL = {"高": "High", "中": "Medium", "低": "Low"}
SEPARATOR = "━" * 52


# ═══════════════════════════════════════════
# feat(todo): 待办事项管理器核心类
# ═══════════════════════════════════════════

class TodoManager:
    """待办事项管理器 —— 数据持久化与 CRUD 操作"""

    def __init__(self):
        self.data_file = DATA_FILE
        self.todos = []
        self._load()

    # ── refactor(persist): 数据持久化 ────────────────

    def _load(self):
        """从 JSON 文件加载待办数据"""
        if not os.path.exists(self.data_file):
            self.todos = []
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.todos = json.load(f)
        except (json.JSONDecodeError, Exception):
            print("⚠️  数据文件损坏，已重新创建")
            self.todos = []

    def _save(self):
        """保存待办数据到 JSON 文件"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)

    # ── feat(todo): 核心功能 ────────────────────────

    def add(self, title, priority="中"):
        """添加新待办事项"""
        if not title or not title.strip():
            return False, "❌ 内容不能为空！"
        if priority not in PRIORITY_ORDER:
            priority = "中"

        todo = {
            "id": len(self.todos) + 1,
            "title": title.strip(),
            "priority": priority,
            "done": False,
            "created_at": time.strftime("%Y-%m-%d %H:%M"),
        }
        self.todos.append(todo)
        self._save()
        return True, f"✅ 已添加：[{priority}] {title.strip()}"

    def list_all(self, show_stats=True):
        """列出所有待办，并按优先级排序"""
        if not self.todos:
            return "📭 暂无待办事项\n"

        sorted_todos = sorted(
            self.todos,
            key=lambda t: (
                t.get("done", False),
                PRIORITY_ORDER.get(t.get("priority", "中"), 1),
            ),
        )

        # ── style(ui): 输出表格 ─────────────────────
        lines = [
            "",
            SEPARATOR,
            f"  {'ID':<3} {'优先级':<6} {'状态':<8}  {'内容'}",
            SEPARATOR,
        ]

        for todo in sorted_todos:
            pri = todo.get("priority", "中")
            icon = PRIORITY_ICON.get(pri, "🟡")
            status = "✅ 已完成" if todo["done"] else "⬜ 未完成"
            lines.append(f"  {todo['id']:<3} {icon:<6} {status:<8}  {todo['title']}")

        lines.append(SEPARATOR)

        if show_stats:
            lines.append(self._build_stats())

        return "\n".join(lines)

    def mark_done(self, todo_id):
        """标记待办为已完成"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                if todo["done"]:
                    return False, "⚠️  该待办已经是完成状态"
                todo["done"] = True
                self._save()
                return True, f"✅ 已标记完成：{todo['title']}"
        return False, f"❌ 未找到 ID 为 {todo_id} 的待办"

    def delete(self, todo_id):
        """删除待办事项"""
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                removed = self.todos.pop(i)
                self._save()
                return True, f"🗑️  已删除：{removed['title']}"
        return False, f"❌ 未找到 ID 为 {todo_id} 的待办"

    # ── feat(stats): 统计信息 ───────────────────────

    def _build_stats(self):
        """生成统计概览（类似 benchmark 的 Metrics 面板）"""
        total = len(self.todos)
        done = sum(1 for t in self.todos if t["done"])
        pending = total - done
        high = sum(
            1 for t in self.todos
            if not t["done"] and t.get("priority") == "高"
        )

        pct = (done / total * 100) if total > 0 else 0

        return (
            f"  📊 统计: 总计 {total}  | 已完成 {done} ({pct:.0f}%)"
            f"  | 待完成 {pending}  | 高优先级 {high} ⚠️"
        )

    def show_stats_only(self):
        """仅显示统计信息"""
        if not self.todos:
            return "📭 暂无待办事项\n"
        return "\n" + self._build_stats() + "\n"


# ═══════════════════════════════════════════
# feat(ui): 交互式命令行界面
# ═══════════════════════════════════════════

class TodoCLI:
    """命令行交互界面 —— 带操作计时与格式化输出"""

    def __init__(self):
        self.manager = TodoManager()

    def _menu(self):
        """显示主菜单"""
        print(f"""
{SEPARATOR}
  📋  待办事项管理器 (Conventional Commits Style)
{SEPARATOR}
  1. ➕ 添加待办
  2. 📋 列出待办
  3. 📊 查看统计
  4. ✅ 标记完成
  5. 🗑️  删除待办
  6. 🚪 退出
{SEPARATOR}""")

    def _timed_op(self, label, fn, *args):
        """带计时执行操作（类似 benchmark 的 per-operation timing）"""
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = (time.perf_counter() - t0) * 1000  # ms
        return result, elapsed

    # ── feat(ui): 操作处理 ─────────────────────────

    def _handle_add(self):
        """处理添加操作"""
        title = input("  请输入待办内容：").strip()
        if not title:
            print("  ❌ 内容不能为空！")
            return
        priority = input("  优先级 (高/中/低，默认中)：").strip() or "中"

        (success, msg), elapsed = self._timed_op(
            "add", self.manager.add, title, priority
        )
        print(f"  {msg}")
        if success:
            print(f"  ⏱  {elapsed:.1f}ms")

    def _handle_list(self):
        """处理列出操作"""
        (output,), elapsed = self._timed_op("list", self.manager.list_all)
        print(output)
        print(f"  ⏱  {elapsed:.1f}ms")

    def _handle_stats(self):
        """处理统计查看"""
        (output,), elapsed = self._timed_op("stats", self.manager.show_stats_only)
        print(output)
        print(f"  ⏱  {elapsed:.1f}ms")

    def _handle_done(self):
        """处理标记完成"""
        print(self.manager.list_all(show_stats=False))
        if not self.manager.todos:
            return
        try:
            tid = int(input("  请输入要标记完成的 ID："))
            (success, msg), elapsed = self._timed_op(
                "done", self.manager.mark_done, tid
            )
            print(f"  {msg}")
            if success:
                print(f"  ⏱  {elapsed:.1f}ms")
        except ValueError:
            print("  ❌ 请输入有效的数字 ID")

    def _handle_delete(self):
        """处理删除操作"""
        print(self.manager.list_all(show_stats=False))
        if not self.manager.todos:
            return
        try:
            tid = int(input("  请输入要删除的 ID："))
            (success, msg), elapsed = self._timed_op(
                "delete", self.manager.delete, tid
            )
            print(f"  {msg}")
            if success:
                print(f"  ⏱  {elapsed:.1f}ms")
        except ValueError:
            print("  ❌ 请输入有效的数字 ID")

    # ── feat(ui): 主循环 ───────────────────────────

    def run(self):
        """启动主循环"""
        print("\n👋  欢迎使用待办事项管理器！")
        print(f"  数据文件: {self.manager.data_file}")
        print(f"  现有待办: {len(self.manager.todos)} 条")

        while True:
            self._menu()
            choice = input("  请选择 (1-6)：").strip()

            if choice == "1":
                self._handle_add()
            elif choice == "2":
                self._handle_list()
            elif choice == "3":
                self._handle_stats()
            elif choice == "4":
                self._handle_done()
            elif choice == "5":
                self._handle_delete()
            elif choice == "6":
                print(f"\n{SEPARATOR}")
                print("  👋 再见！")
                print(f"{SEPARATOR}\n")
                break
            else:
                print("  ❌ 无效选择，请输入 1-6")


# ═══════════════════════════════════════════
# feat(main): 程序入口
# ═══════════════════════════════════════════

def main():
    """程序入口点"""
    try:
        app = TodoCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n  👋 再见！\n")
    except Exception as e:
        print(f"\n  💥 发生未知错误：{e}")
        exit(1)


if __name__ == "__main__":
    main()
