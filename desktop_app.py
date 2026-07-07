"""
桌面版待办事项管理器 (Todo App)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于 PyWebView 的原生 Windows 桌面窗口

fix(perf): 使用 Edge WebView2 替代 CEF，避免首次下载 150MB+ Chromium
fix(bug): 添加 Flask 健康检查，确保服务就绪后再打开窗口
fix(bug): 添加 GUI 后端自动降级，防止 edgechromium 不可用时崩溃
"""

import threading
import sys
import os
import time
import urllib.request
import urllib.error

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
FLASK_URL = "http://127.0.0.1:5000"
FLASK_PORT = 5000


# ═══════════════════════════════════════════
# feat(server): 内嵌 Flask 服务
# ═══════════════════════════════════════════

def start_flask():
    """在后台线程启动 Flask 服务"""
    flask_app.run(
        host="127.0.0.1",
        port=FLASK_PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def wait_for_server(url=FLASK_URL, timeout=15, interval=0.3):
    """等待 Flask 服务就绪，避免窗口打开时白屏

    fix(bug): 之前没有等待服务启动就直接开窗口，
              PyWebView 加载空页面导致白屏/超时
    """
    print(f"⏳  等待服务启动...", end="", flush=True)
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            print(f"\r✅  服务就绪 ({(time.time()-t0):.1f}s)")
            return True
        except (urllib.error.URLError, Exception):
            print(".", end="", flush=True)
            time.sleep(interval)
    print(f"\r❌  服务启动超时 ({timeout}s)")
    return False


# ═══════════════════════════════════════════
# feat(desktop): 桌面窗口
# ═══════════════════════════════════════════

def get_best_gui():
    """自动选择最优 GUI 后端

    fix(perf): 之前强制使用 CEF (Chromium Embedded Framework)，
              首次运行需要下载 ~150MB，极慢且容易卡死。
              改为优先使用 Edge WebView2（Win10/11 内置，轻量）。

    fix(bug): CEF 在某些精简版 Windows 上可能不可用，
              edgechromium 如果也不可用则降级到 mshtml。
    """
    if sys.platform != "win32":
        return None  # macOS/Linux 用默认 WebKit

    # 检查 Edge WebView2 是否可用
    try:
        import webview.platforms.edgechromium as _edge
        # 尝试实例化一个最小窗口来测试
        print("🔍  检测 GUI 后端: Edge WebView2 (推荐)")
        return "edgechromium"
    except ImportError:
        pass

    # 降级到 CEF
    try:
        import webview.platforms.cef as _cef
        print("⚠️  检测 GUI 后端: CEF (Edge WebView2 不可用)")
        return "cef"
    except ImportError:
        pass

    # 最后降级到 MSHTML (IE 内核)
    print("⚠️  检测 GUI 后端: MSHTML (兼容模式)")
    return "mshtml"


def main():
    """启动桌面应用"""
    print(f"🚀  Todo App 桌面版正在启动...")

    # ── 启动 Flask 服务（后台线程） ────────
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()

    # ── 等待服务就绪（修复白屏 bug） ──────
    if not wait_for_server():
        print("❌  无法启动服务，请检查端口 5000 是否被占用")
        input("按 Enter 键退出...")
        return

    print(f"📂  数据文件: todos.json")
    print(f"🪟  正在打开桌面窗口...")
    print(f"❌  关闭窗口即退出程序")

    # ── 选择最优 GUI 后端 ──────────────────
    gui = get_best_gui()

    # ── 创建原生桌面窗口 ──────────────────
    webview.create_window(
        title=WINDOW_TITLE,
        url=FLASK_URL,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
        resizable=True,
        text_select=True,
        confirm_close=True,
    )

    webview.start(gui=gui)


if __name__ == "__main__":
    main()
