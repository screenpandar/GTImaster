"""全局运行状态，替代零散 global 变量。"""


class AppState:
    """程序运行状态：常规/实时检测运行标志、线程、快捷键等。"""

    def __init__(self):
        self.running = False
        self.paused = False
        self.program_thread = None
        self.current_hotkey = "f8"
        self.hotkey_active = False

    def is_program_running(self):
        """是否有任务线程在跑（常规或实时检测）。"""
        return self.program_thread is not None and self.program_thread.is_alive()
