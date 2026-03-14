import cv2
import numpy as np
import time
import win32con
import win32api
from PIL import Image, ImageFilter, ImageEnhance
import pyautogui
import pygetwindow as gw
import keyboard
import customtkinter as ctk
from tkinter import scrolledtext
import threading
from datetime import datetime, time as dt_time
from types import SimpleNamespace
import easyocr
import mss
import psutil
import random
from core.fast_click import fast_click
import os
import ctypes
from config import (
    PRICE_BOX_BASE,
    BUY_POS_BASE,
    BUY_POS1_BASE,
    NUM_MAX_BASE,
    AVERAGE_PRICE_BOX_BASE,
    HVVK_SHOP_POS_BASE,
    ITEM_POS_LIST_BASE,
    RECTIFY_CLICK_POS_1_BASE,
    RECTIFY_CLICK_POS_2_BASE,
)
from core.shutdown import ShutdownController
from core.realtime_mode import RealtimeModeController
from core.app_state import AppState
from core import normal_mode
from utils.image_utils import capture_fast, box_to_region
from ui.main_window import create_main_window

# 获取屏幕分辨率
width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
# 初始化
reader = easyocr.Reader(['en'])  # 指定语言为英文（也支持数字识别）

# 相对坐标计算函数
def rel_x(x):
    return int(x * width / 1920)

def rel_y(y):
    return int(y * height / 1080)


# 相对坐标定义
PRICE_LEFT, PRICE_TOP, PRICE_RIGHT, PRICE_BOTTOM = (
    rel_x(PRICE_BOX_BASE[0]),
    rel_y(PRICE_BOX_BASE[1]),
    rel_x(PRICE_BOX_BASE[2]),
    rel_y(PRICE_BOX_BASE[3]),
)  # 左上角在售最低价
BUY_POS = (rel_x(BUY_POS_BASE[0]), rel_y(BUY_POS_BASE[1]))
BUY_POS1 = (rel_x(BUY_POS1_BASE[0]), rel_y(BUY_POS1_BASE[1]))  # 购买键
NUM_MAX_X, NUM_MAX_Y, NUM_MAX_Y1 = (
    rel_x(NUM_MAX_BASE[0]),
    rel_y(NUM_MAX_BASE[1]),
    rel_y(NUM_MAX_BASE[2]),
)  # 购买数量读条最右侧
AVERAGE_PRICE_LEFT, AVERAGE_PRICE_TOP, AVERAGE_PRICE_RIGHT, AVERAGE_PRICE_BOTTOM = (
    rel_x(AVERAGE_PRICE_BOX_BASE[0]),
    rel_y(AVERAGE_PRICE_BOX_BASE[1]),
    rel_x(AVERAGE_PRICE_BOX_BASE[2]),
    rel_y(AVERAGE_PRICE_BOX_BASE[3]),
)  # 右下角平均单价
HVVK_SHOP_X, HVVK_SHOP_Y = rel_x(HVVK_SHOP_POS_BASE[0]), rel_y(HVVK_SHOP_POS_BASE[1])


# 目标区域
price_box = (PRICE_LEFT, PRICE_TOP, PRICE_RIGHT, PRICE_BOTTOM)
num_max_pos = (NUM_MAX_X, NUM_MAX_Y)
item_pos_list = [
    (rel_x(item_x), rel_y(item_y)) for item_x, item_y in ITEM_POS_LIST_BASE
]
average_box = (AVERAGE_PRICE_LEFT, AVERAGE_PRICE_TOP, AVERAGE_PRICE_RIGHT, AVERAGE_PRICE_BOTTOM)

# 全局状态与控制器
app_state = AppState()
shutdown_controller = ShutdownController()

kernal = np.ones((3, 3), np.uint8)  # 定义卷积核


def get_target_text(box):
    img = capture_fast(box_to_region(box))
    img = img.filter(ImageFilter.SHARPEN)
#   enhancer = ImageEnhance.Contrast(img)
#   img = enhancer.enhance(1.3)
    img = img.convert('L')
    img = np.array(img)
    img = cv2.resize(img, (0, 0), fx=2, fy=4)
#   img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.bitwise_not(img)
    img = Image.fromarray(img)
    img_np = np.array(img)
    img_np = cv2.dilate(img_np,kernal,iterations=1)
    result = reader.readtext(img_np)
#   cv2.imwrite('result.png',img_np)
    texts = [item[1] for item in result]  # item[1] 是识别的文本内容
    combined_text = ' '.join(texts)  # 将所有文本合并为一个字符串
    return combined_text.strip()  # 去除首尾空白字符并返回
    



def stop_running():
    app_state.running = False
    realtime_controller.stop_detection()
    if app_state.hotkey_active:
        try:
            keyboard.remove_hotkey(app_state.current_hotkey)
            app_state.hotkey_active = False
        except Exception:
            pass
    output_text.insert(ctk.END, "程序已停止\n")
    single_output_text.insert(ctk.END, "程序已停止\n")

def start_program():
    if app_state.is_program_running():
        output_text.insert(ctk.END, "程序已在运行中，请勿重复启动\n")
        return
    max_price = int(max_price_entry.get())
    interval = float(interval_entry.get())
    goldegg_mode = goldegg_mode_var.get()
    buy_quantity = int(buy_quantity_entry.get())
    max_rectify_count = int(rectify_count_entry.get())

    app_state.running = True
    app_state.paused = False
    output_text.insert(ctk.END, "程序开始运行...\n")

    if not app_state.hotkey_active:
        try:
            keyboard.add_hotkey(app_state.current_hotkey, lambda: threading.Thread(target=stop_running).start(), suppress=True)
            app_state.hotkey_active = True
            output_text.insert(ctk.END, f"快捷键 {app_state.current_hotkey.upper()} 已激活，按此键可停止程序\n")
        except Exception as e:
            output_text.insert(ctk.END, f"快捷键设置失败：{str(e)}\n")

    ctx = SimpleNamespace()
    ctx.get_running = lambda: app_state.running
    ctx.get_paused = lambda: app_state.paused
    ctx.get_start_time = lambda: start_time_entry.get()
    ctx.get_end_time = lambda: end_time_entry.get()
    ctx.output_text = output_text
    ctx.root = root
    ctx.rel_x = rel_x
    ctx.rel_y = rel_y
    ctx.price_box = price_box
    ctx.average_box = average_box
    ctx.BUY_POS = BUY_POS
    ctx.BUY_POS1 = BUY_POS1
    ctx.NUM_MAX_X = NUM_MAX_X
    ctx.NUM_MAX_Y = NUM_MAX_Y
    ctx.NUM_MAX_Y1 = NUM_MAX_Y1
    ctx.HVVK_SHOP_X = HVVK_SHOP_X
    ctx.HVVK_SHOP_Y = HVVK_SHOP_Y
    ctx.get_target_text = get_target_text
    ctx.fast_click = fast_click
    ctx.max_price = max_price
    ctx.buy_quantity = buy_quantity
    ctx.goldegg_mode = goldegg_mode
    ctx.max_rectify_count = max_rectify_count
    ctx.get_card_mode = card_mode_var.get
    ctx.get_max_mode = max_mode_var.get
    ctx.rectify_fn = lambda: normal_mode.rectify(ctx)
    ctx.stop_fn = stop_running

    app_state.program_thread = threading.Thread(target=normal_mode.run_main_loop, args=(interval, ctx))
    app_state.program_thread.daemon = True
    app_state.program_thread.start()

# ---------------------------------------------------------------------------
# 主窗口与控件（由 ui 模块创建，此处解包并绑定业务逻辑）
# ---------------------------------------------------------------------------
realtime_controller = RealtimeModeController()
root, widgets = create_main_window(app_state)

output_text = widgets.output_text
single_output_text = widgets.single_output_text
max_price_entry = widgets.max_price_entry
buy_quantity_entry = widgets.buy_quantity_entry
rectify_count_entry = widgets.rectify_count_entry
max_mode_var = widgets.max_mode_var
card_mode_var = widgets.card_mode_var
goldegg_mode_var = widgets.goldegg_mode_var
shutdown_time_entry = widgets.shutdown_time_entry
shutdown_button = widgets.shutdown_button
interval_entry = widgets.interval_entry
start_time_entry = widgets.start_time_entry
end_time_entry = widgets.end_time_entry
start_button = widgets.start_button
single_max_price_entry = widgets.single_max_price_entry
balance_digits_entry = widgets.balance_digits_entry
single_hotkey_entry = widgets.single_hotkey_entry
single_start_time_entry = widgets.single_start_time_entry
single_end_time_entry = widgets.single_end_time_entry
speed_slider = widgets.speed_slider
single_shutdown_time_entry = widgets.single_shutdown_time_entry
single_shutdown_button = widgets.single_shutdown_button
single_start_button = widgets.single_start_button
tabview = widgets.tabview


def toggle_shutdown():
    if not shutdown_controller.running:
        shutdown_time = shutdown_time_entry.get()
        if shutdown_time:
            shutdown_controller.start(shutdown_time, output_text)
            shutdown_button.configure(text="停止定时关机")
        else:
            output_text.insert(ctk.END, "请设置关机时间\n")
    else:
        shutdown_controller.stop(output_text)
        shutdown_button.configure(text="启动定时关机")


def toggle_single_shutdown():
    if not shutdown_controller.running:
        shutdown_time = single_shutdown_time_entry.get()
        if shutdown_time:
            shutdown_controller.start(shutdown_time, single_output_text)
            single_shutdown_button.configure(text="停止定时关机")
        else:
            single_output_text.insert(ctk.END, "请设置关机时间\n")
    else:
        shutdown_controller.stop(single_output_text)
        single_shutdown_button.configure(text="启动定时关机")


def on_closing():
    app_state.running = False
    shutdown_controller.stop()
    if app_state.hotkey_active:
        try:
            keyboard.remove_hotkey(app_state.current_hotkey)
            app_state.hotkey_active = False
        except Exception:
            pass
    root.destroy()


def start_single_detection():
    if app_state.is_program_running():
        single_output_text.insert(ctk.END, "程序已在运行中，请勿重复启动\n")
        return
    try:
        max_price = int(single_max_price_entry.get())
        balance_digits = int(balance_digits_entry.get())
        detection_delay = float(speed_slider.get())
        start_time = single_start_time_entry.get()
        end_time = single_end_time_entry.get()

        def on_message(msg):
            single_output_text.insert(ctk.END, msg + "\n")
            single_output_text.see(ctk.END)

        app_state.running = True
        if not app_state.hotkey_active:
            try:
                keyboard.add_hotkey(app_state.current_hotkey, lambda: threading.Thread(target=stop_running).start(), suppress=True)
                app_state.hotkey_active = True
                single_output_text.insert(ctk.END, f"快捷键 {app_state.current_hotkey.upper()} 已激活，按此键可停止程序\n")
            except Exception as e:
                single_output_text.insert(ctk.END, f"快捷键设置失败：{str(e)}\n")

        app_state.program_thread = realtime_controller.start(
            max_price, balance_digits, detection_delay, start_time, end_time, on_message
        )
        app_state.program_thread.start()
        single_output_text.insert(ctk.END, "实时检测模式启动...\n")
    except ValueError as e:
        single_output_text.insert(ctk.END, f"启动失败：{str(e)}\n")


shutdown_button.configure(command=toggle_shutdown)
single_shutdown_button.configure(command=toggle_single_shutdown)
start_button.configure(command=start_program)
single_start_button.configure(command=start_single_detection)
root.protocol("WM_DELETE_WINDOW", on_closing)
keyboard.add_hotkey("f12", lambda: threading.Thread(target=stop_running).start(), suppress=True)


def start_with_hotkey():
    """通过快捷键启动程序（仅实时检测模式）"""
    if app_state.running or app_state.is_program_running():
        return
    current_tab = tabview.get()
    if current_tab == "实时检测模式":
        try:
            int(single_max_price_entry.get())
            int(balance_digits_entry.get())
            threading.Thread(target=start_single_detection).start()
        except ValueError:
            single_output_text.insert(ctk.END, "请先设置必要的参数（最大价格、余额位数）\n")

try:
    keyboard.add_hotkey(app_state.current_hotkey, start_with_hotkey, suppress=True)
    print(f"全局快捷键 {app_state.current_hotkey.upper()} 已设置，按此键可启动程序")
except Exception as e:
    print(f"全局快捷键设置失败：{str(e)}")

root.mainloop()