"""
待办事项管理器 (Todo App)
命令行交互，数据保存到 JSON 文件。

功能：
  1. 添加待办事项
  2. 列出所有待办
  3. 标记为已完成
  4. 删除待办事项
"""

import json
import os


DATA_FILE = "todos.json"


def load_todos():
    """从文件加载待办列表"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        print("数据文件损坏，将重新创建。")
        return []


def save_todos(todos):
    """保存待办列表到文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def add_todo(todos):
    """添加新待办"""
    title = input("请输入待办事项内容：").strip()
    if not title:
        print("内容不能为空！")
        return
    todo = {
        "id": len(todos) + 1,
        "title": title,
        "done": False
    }
    todos.append(todo)
    save_todos(todos)
    print(f"✅ 已添加：{title}")


def list_todos(todos):
    """列出所有待办"""
    if not todos:
        print("📭 暂无待办事项")
        return
    print(f"\n{'ID':<4} {'状态':<8} {'内容'}")
    print("-" * 40)
    for todo in todos:
        status = "✅ 已完成" if todo["done"] else "⬜ 未完成"
        print(f"{todo['id']:<4} {status:<8} {todo['title']}")


def mark_done(todos):
    """标记待办为已完成"""
    list_todos(todos)
    if not todos:
        return
    try:
        tid = int(input("请输入要标记完成的 ID："))
        for todo in todos:
            if todo["id"] == tid:
                todo["done"] = True
                save_todos(todos)
                print(f"✅ 已标记完成：{todo['title']}")
                return
        print(f"未找到 ID 为 {tid} 的待办")
    except ValueError:
        print("请输入有效的数字 ID")


def delete_todo(todos):
    """删除待办"""
    list_todos(todos)
    if not todos:
        return
    try:
        tid = int(input("请输入要删除的 ID："))
        for i, todo in enumerate(todos):
            if todo["id"] == tid:
                removed = todos.pop(i)
                save_todos(todos)
                print(f"🗑️ 已删除：{removed['title']}")
                return
        print(f"未找到 ID 为 {tid} 的待办")
    except ValueError:
        print("请输入有效的数字 ID")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 30)
    print("      待办事项管理器")
    print("=" * 30)
    print("1. 添加待办")
    print("2. 列出待办")
    print("3. 标记完成")
    print("4. 删除待办")
    print("5. 退出")
    print("=" * 30)


def main():
    todos = load_todos()
    while True:
        show_menu()
        choice = input("请选择操作 (1-5)：").strip()
        if choice == "1":
            add_todo(todos)
        elif choice == "2":
            list_todos(todos)
        elif choice == "3":
            mark_done(todos)
        elif choice == "4":
            delete_todo(todos)
        elif choice == "5":
            print("👋 再见！")
            break
        else:
            print("无效选择，请输入 1-5")


if __name__ == "__main__":
    main()
