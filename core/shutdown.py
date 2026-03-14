import os
import time
import threading
from datetime import datetime

import customtkinter as ctk


class ShutdownController:
    """负责定时关机逻辑的控制器。"""

    def __init__(self) -> None:
        self.thread = None
        self.running = False

    def _shutdown_now(self) -> None:
        """执行一次关机操作。"""
        try:
            # 关机前等待 5 秒，与原逻辑保持一致
            time.sleep(5)
            os.system("shutdown /s /t 0")
        except Exception as e:
            # 原逻辑只是打印错误信息
            print(f"关机时发生错误：{e}")

    def _check_time_loop(self, shutdown_time: str, output_widget) -> None:
        """在独立线程中循环检测是否到达关机时间。"""
        try:
            target_hour, target_minute = map(int, shutdown_time.split(":"))
        except ValueError:
            output_widget.insert(ctk.END, f"无效的关机时间格式：{shutdown_time}\n")
            output_widget.see(ctk.END)
            self.running = False
            return

        while self.running:
            try:
                now = datetime.now().time()
                if now.hour == target_hour and now.minute == target_minute:
                    output_widget.insert(
                        ctk.END, f"到达关机时间 {shutdown_time}，准备关机...\n"
                    )
                    output_widget.see(ctk.END)
                    self._shutdown_now()
                    break
                time.sleep(30)
            except Exception as e:
                output_widget.insert(ctk.END, f"定时关机检查出错：{e}\n")
                output_widget.see(ctk.END)
                break

        self.running = False
        self.thread = None

    def start(self, shutdown_time: str, output_widget) -> None:
        """启动定时关机检测线程。"""
        if self.thread is not None and self.thread.is_alive():
            output_widget.insert(ctk.END, "定时关机已在运行中\n")
            output_widget.see(ctk.END)
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._check_time_loop, args=(shutdown_time, output_widget)
        )
        self.thread.daemon = True
        self.thread.start()
        output_widget.insert(ctk.END, f"定时关机已启动，将在 {shutdown_time} 关机\n")
        output_widget.see(ctk.END)

    def stop(self, output_widget=None) -> None:
        """停止定时关机线程。"""
        self.running = False
        if self.thread is not None and self.thread.is_alive():
            self.thread = None
            if output_widget is not None:
                output_widget.insert(ctk.END, "定时关机已停止\n")
                output_widget.see(ctk.END)
        else:
            if output_widget is not None:
                output_widget.insert(ctk.END, "定时关机未在运行\n")
                output_widget.see(ctk.END)

