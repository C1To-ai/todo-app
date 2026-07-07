"""
桌面版待办事项管理器 (Todo App)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于 PyWebView 的原生 Windows 桌面窗口
"""

import threading
import sys
import os

# 确保能正确导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import webview
from app import app as flask_app


# ═══════════════════════════════════════════
# feat(config): 桌面窗口配置
# ═══════════════════════════════════════════

WINDOW_TITLE = "待办事项管理器"
WINDOW_WIDTH = 780
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 420
WINDOW_MIN_HEIGHT = 500


# ═══════════════════════════════════════════
# feat(server): 内嵌 Flask 服务
# ═══════════════════════════════════════════

def start_flask():
    """在后台线程启动 Flask 服务"""
    flask_app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


# ═══════════════════════════════════════════
# feat(desktop): 桌面窗口
# ═══════════════════════════════════════════

def main():
    """启动桌面应用"""
    # 启动 Flask 服务（后台线程）
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()

    print(f"🚀  Todo App 桌面版已启动！")
    print(f"📂  数据文件: todos.json")
    print(f"🪟  正在打开窗口...")
    print(f"❌  关闭窗口即退出程序")

    # 创建原生桌面窗口
    webview.create_window(
        title=WINDOW_TITLE,
        url="http://127.0.0.1:5000",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
        resizable=True,
        text_select=True,
        confirm_close=True,
        # ── style(ui): 窗口图标
        # icon="icon.ico",  # 有图标可以取消注释
    )

    webview.start(gui="cef" if sys.platform == "win32" else None)


if __name__ == "__main__":
    main()
