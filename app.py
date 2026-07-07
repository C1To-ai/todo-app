"""
Web 版待办事项管理器 (Todo App)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flask 后端 + RESTful API
"""

from flask import Flask, jsonify, request, render_template
from todo import TodoManager, PRIORITY_ORDER, PRIORITY_ICON


app = Flask(__name__)
manager = TodoManager()


# ── Helper ───────────────────────────────────────

def _todo_to_dict(t):
    """将待办项转为前端友好格式"""
    pri = t.get("priority", "中")
    return {
        "id": t["id"],
        "title": t["title"],
        "priority": pri,
        "priority_order": PRIORITY_ORDER.get(pri, 1),
        "priority_icon": PRIORITY_ICON.get(pri, "🟡"),
        "done": t["done"],
        "created_at": t.get("created_at", ""),
    }


def _build_stats():
    """生成统计信息"""
    todos = manager.todos
    total = len(todos)
    done = sum(1 for t in todos if t["done"])
    pending = total - done
    high = sum(1 for t in todos if not t["done"] and t.get("priority") == "高")
    pct = round(done / total * 100, 1) if total > 0 else 0
    return {
        "total": total,
        "done": done,
        "pending": pending,
        "high_priority": high,
        "completion_pct": pct,
    }


# ═══════════════════════════════════════════
# feat(route): 页面路由
# ═══════════════════════════════════════════

@app.route("/")
def index():
    """渲染主页"""
    return render_template("index.html")


# ═══════════════════════════════════════════
# feat(api): RESTful API
# ═══════════════════════════════════════════

@app.route("/api/todos", methods=["GET"])
def list_todos():
    """获取所有待办（按优先级排序）"""
    sorted_todos = sorted(
        manager.todos,
        key=lambda t: (t["done"], PRIORITY_ORDER.get(t.get("priority", "中"), 1)),
    )
    return jsonify({
        "todos": [_todo_to_dict(t) for t in sorted_todos],
        "stats": _build_stats(),
    })


@app.route("/api/todos", methods=["POST"])
def add_todo():
    """添加新待办"""
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    priority = data.get("priority", "中")

    if not title:
        return jsonify({"success": False, "error": "内容不能为空"}), 400

    ok, msg = manager.add(title, priority)
    if not ok:
        return jsonify({"success": False, "error": msg}), 400

    return jsonify({
        "success": True,
        "message": msg,
        "todos": [_todo_to_dict(t) for t in sorted(
            manager.todos,
            key=lambda t: (t["done"], PRIORITY_ORDER.get(t.get("priority", "中"), 1)),
        )],
        "stats": _build_stats(),
    })


@app.route("/api/todos/<int:todo_id>/done", methods=["PUT"])
def mark_done(todo_id):
    """标记待办为已完成"""
    ok, msg = manager.mark_done(todo_id)
    if not ok:
        return jsonify({"success": False, "error": msg}), 404

    return jsonify({
        "success": True,
        "message": msg,
        "todos": [_todo_to_dict(t) for t in sorted(
            manager.todos,
            key=lambda t: (t["done"], PRIORITY_ORDER.get(t.get("priority", "中"), 1)),
        )],
        "stats": _build_stats(),
    })


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """删除待办"""
    ok, msg = manager.delete(todo_id)
    if not ok:
        return jsonify({"success": False, "error": msg}), 404

    return jsonify({
        "success": True,
        "message": msg,
        "todos": [_todo_to_dict(t) for t in sorted(
            manager.todos,
            key=lambda t: (t["done"], PRIORITY_ORDER.get(t.get("priority", "中"), 1)),
        )],
        "stats": _build_stats(),
    })


@app.route("/api/todos/stats", methods=["GET"])
def get_stats():
    """获取统计信息"""
    return jsonify(_build_stats())


# ═══════════════════════════════════════════
# feat(main): 启动入口
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print(f"🚀  Todo App 网页版已启动！")
    print(f"📂  数据文件: {manager.data_file}")
    print(f"📊  现有待办: {len(manager.todos)} 条")
    print(f"🌐  访问地址: http://127.0.0.1:5000")
    app.run(debug=True)
