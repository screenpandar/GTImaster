"""实时检测模式逻辑模块。

包含 RealTimeDetector 及其控制器 RealtimeModeController。
"""

import threading
import time
from datetime import datetime, time as dt_time

import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image, ImageFilter
import easyocr
import win32api
import win32con

from config import (
    SSD_BUY_POS1_BASE,
    SSD_NUM_MAX_BASE,
    SSD_NUM_MIN_BASE,
    SSD_HAFV_HOVER_POS_BASE,
    SSD_HAFV_BALANCE_BOX_BASE,
    SSD_HVVK_SHOP_POS_BASE,
    SSD_HVVK_SHOP_ITEM_POS_BASE,
)


class RealTimeDetector:
    def __init__(self):
        self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        self.reader = easyocr.Reader(["en"])

        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

        self.BUY_POS1 = (
            self.rel_x(SSD_BUY_POS1_BASE[0]),
            self.rel_y(SSD_BUY_POS1_BASE[1]),
        )
        self.NUM_MAX_X, self.NUM_MAX_Y1 = (
            self.rel_x(SSD_NUM_MAX_BASE[0]),
            self.rel_y(SSD_NUM_MAX_BASE[1]),
        )
        self.NUM_MIN_X, self.NUM_MIN_Y1 = (
            self.rel_x(SSD_NUM_MIN_BASE[0]),
            self.rel_y(SSD_NUM_MIN_BASE[1]),
        )
        self.HAFV_HOVER_POS = (
            self.rel_x(SSD_HAFV_HOVER_POS_BASE[0]),
            self.rel_y(SSD_HAFV_HOVER_POS_BASE[1]),
        )
        self.HAFV_BALANCE_BOX = (
            self.rel_x(SSD_HAFV_BALANCE_BOX_BASE[0]),
            self.rel_y(SSD_HAFV_BALANCE_BOX_BASE[1]),
            self.rel_x(SSD_HAFV_BALANCE_BOX_BASE[2]),
            self.rel_y(SSD_HAFV_BALANCE_BOX_BASE[3]),
        )
        self.HVVK_SHOP_POS = (
            self.rel_x(SSD_HVVK_SHOP_POS_BASE[0]),
            self.rel_y(SSD_HVVK_SHOP_POS_BASE[1]),
        )
        self.HVVK_SHOP_ITEM_POS = (
            self.rel_x(SSD_HVVK_SHOP_ITEM_POS_BASE[0]),
            self.rel_y(SSD_HVVK_SHOP_ITEM_POS_BASE[1]),
        )

        self.is_batch_mode = False
        self.running = False
        self.balance_digits = None
        self.detection_delay = 0.3
        self.start_time = None
        self.end_time = None
        self.callback = None
        self.last_balance = None
        self.max_price = None

        self.digit_change_counter = 0
        self.last_digit_count = None

    def set_balance_digits(self, digits):
        self.balance_digits = digits

    def set_detection_delay(self, delay):
        self.detection_delay = delay

    def set_time_window(self, start_time_str, end_time_str):
        if start_time_str and end_time_str:
            self.start_time = dt_time(*map(int, start_time_str.split(":")))
            self.end_time = dt_time(*map(int, end_time_str.split(":")))
        else:
            self.start_time = None
            self.end_time = None

    def check_time_window(self):
        if not self.start_time or not self.end_time:
            return True

        current_time = datetime.now().time()
        if self.start_time < self.end_time:
            return self.start_time <= current_time <= self.end_time
        else:
            return current_time >= self.start_time or current_time <= self.end_time

    def rel_x(self, x):
        return int(x * self.width / 1920)

    def rel_y(self, y):
        return int(y * self.height / 1080)

    def capture_fast(self, region):
        with mss.mss() as sct:
            screenshot = sct.grab(
                {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2] - region[0],
                    "height": region[3] - region[1],
                }
            )
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    def correct_balance(self, balance_text, max_change):
        try:
            current_balance = int(balance_text)
            if self.last_balance is None:
                return current_balance

            change = abs(current_balance - self.last_balance)
            if self.is_batch_mode:
                change_per_item = change // 200
            else:
                change_per_item = change // 31

            if change_per_item <= max_change:
                return current_balance

            digits = list(balance_text)
            for i in range(len(digits) - 1, -1, -1):
                if digits[i] == "8":
                    digits[i] = "6"
                    new_balance = int("".join(digits))
                    new_change = abs(new_balance - self.last_balance)
                    if self.is_batch_mode:
                        new_change_per_item = new_change // 200
                    else:
                        new_change_per_item = new_change // 31
                    if new_change_per_item <= max_change:
                        if self.callback:
                            self.callback(
                                f"已修正余额：{current_balance} -> {new_balance} (8->6)"
                            )
                        return new_balance

            if self.callback:
                mode_str = "批量模式" if self.is_batch_mode else "实时检测模式"
                change_str = f"{change//200 if self.is_batch_mode else change//31}"
                self.callback(
                    f"{mode_str}下余额变化过大且无法修正：{current_balance}，上次余额：{self.last_balance}，单价变化：{change_str}"
                )

            pyautogui.moveTo(self.NUM_MIN_X, self.NUM_MIN_Y1)
            time.sleep(0.05)
            pyautogui.click()
            time.sleep(0.2)
            return current_balance

        except ValueError:
            return None

    def get_balance(self):
        try:
            time.sleep(0.05)
            pyautogui.moveTo(self.HAFV_HOVER_POS)
            time.sleep(0.05)
            if not self.is_batch_mode:
                time.sleep(self.detection_delay)
            else:
                time.sleep(0.15)
            img = self.capture_fast(self.HAFV_BALANCE_BOX)

            img = img.filter(ImageFilter.SHARPEN)
            img = img.convert("L")
            img_np = np.array(img)

            result = self.reader.readtext(img_np)
            if result:
                balance_text = result[0][1]
                replace_dict = {
                    "O": "0",
                    "o": "0",
                    "Q": "0",
                    "D": "0",
                    "Z": "2",
                    "z": "2",
                    "l": "1",
                    "I": "1",
                    "i": "1",
                    "S": "5",
                    "s": "5",
                    "B": "8",
                    "b": "8",
                    "g": "9",
                    "G": "9",
                    "，": "",
                    ",": "",
                    ".": "",
                    " ": "",
                }
                for old_char, new_char in replace_dict.items():
                    balance_text = balance_text.replace(old_char, new_char)

                balance_text = "".join(ch for ch in balance_text if ch.isdigit())
                if not balance_text:
                    if self.callback:
                        self.callback("处理后的余额字符串为空")
                    return None

                if self.balance_digits:
                    current_digits = len(balance_text)
                    if current_digits == self.balance_digits - 1:
                        if self.last_digit_count == current_digits:
                            self.digit_change_counter += 1
                            if self.digit_change_counter >= 8:
                                old_digits = self.balance_digits
                                self.balance_digits = current_digits
                                if self.callback:
                                    self.callback(
                                        f"检测到余额位数持续减少，自动更新预期位数：{old_digits} -> {self.balance_digits}"
                                    )
                                self.digit_change_counter = 0
                        else:
                            self.digit_change_counter = 1
                    else:
                        self.digit_change_counter = 0

                    self.last_digit_count = current_digits

                    if current_digits != self.balance_digits:
                        if current_digits < self.balance_digits:
                            balance_text = balance_text + "0" * (
                                self.balance_digits - current_digits
                            )
                            if self.callback:
                                self.callback(f"位数不足，修正后结果：{balance_text}")
                        elif current_digits > self.balance_digits:
                            balance_text = balance_text[: self.balance_digits]
                            if self.callback:
                                self.callback(f"位数过多，修正后结果：{balance_text}")

                max_change = (
                    self.max_price + 500 if self.max_price is not None else 99999
                )
                corrected_balance = self.correct_balance(balance_text, max_change)

                if corrected_balance is not None:
                    if self.callback:
                        self.callback(
                            f"OCR原始识别结果: {result[0][1]}, 最终结果: {corrected_balance}"
                        )
                    self.last_balance = corrected_balance
                    return corrected_balance
                return None

            else:
                if self.callback:
                    self.callback("OCR未能识别到文本")
                return None

        except Exception as e:
            if self.callback:
                self.callback(f"余额识别发生错误：{str(e)}")
            return None

    def start_detection(self, max_price, callback=None):
        if not self.balance_digits:
            raise ValueError("请先设置哈夫币余额位数")

        self.callback = callback
        self.max_price = max_price
        self.running = True
        self.last_balance = None

        window = gw.getWindowsWithTitle("三角洲行动")[0]
        window.activate()
        time.sleep(0.5)

        pyautogui.moveTo(self.NUM_MIN_X, self.NUM_MIN_Y1)
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.2)

        while self.running:
            try:
                if not self.check_time_window():
                    if callback:
                        current_time = datetime.now().time()
                        callback(
                            f"当前时间 {current_time.strftime('%H:%M:%S')} 不在设定的运行时间范围内"
                        )
                    time.sleep(10)
                    continue

                before_balance = self.get_balance()
                if before_balance is None:
                    continue

                if not self.is_batch_mode:
                    pyautogui.moveTo(self.BUY_POS1[0], self.BUY_POS1[1])
                    time.sleep(0.1)
                    pyautogui.click()
                    time.sleep(0.05)

                    after_balance = self.get_balance()
                    if after_balance is None:
                        continue

                    price_per_item = (before_balance - after_balance) // 31
                    if callback:
                        callback(f"实时检测 - 当前价格: {price_per_item}")

                    if price_per_item <= max_price and price_per_item > 10:
                        self.is_batch_mode = True
                        if callback:
                            callback(
                                f"发现低价商品！单价：{price_per_item}，切换到批量购买模式"
                            )
                        time.sleep(0.05)

                else:
                    pyautogui.moveTo(self.NUM_MAX_X, self.NUM_MAX_Y1)
                    time.sleep(0.05)
                    pyautogui.click()
                    time.sleep(0.05)

                    pyautogui.moveTo(self.BUY_POS1[0], self.BUY_POS1[1])
                    time.sleep(0.05)
                    pyautogui.click()
                    time.sleep(0.05)

                    after_balance = self.get_balance()
                    if after_balance is None:
                        self.is_batch_mode = False
                        if callback:
                            callback("批量模式下余额检测失败，继续检测")

                        pyautogui.moveTo(self.NUM_MIN_X, self.NUM_MIN_Y1)
                        time.sleep(0.05)
                        pyautogui.click()
                        time.sleep(0.2)
                        continue

                    total_cost = before_balance - after_balance
                    if total_cost < 0 or total_cost > ((max_price + 500) * 200):
                        self.is_batch_mode = False
                        if callback:
                            callback(
                                f"批量模式下余额变化异常：{total_cost}，继续检测"
                            )

                        pyautogui.moveTo(self.NUM_MIN_X, self.NUM_MIN_Y1)
                        time.sleep(0.05)
                        pyautogui.click()
                        time.sleep(0.2)
                        continue

                    price_per_item = total_cost // 200
                    if callback:
                        callback(f"批量模式 - 均价: {price_per_item}")

                    if price_per_item > max_price:
                        self.is_batch_mode = False
                        if callback:
                            callback(
                                f"批量购买价格超出限制！均价：{price_per_item}，继续检测"
                            )

                        pyautogui.moveTo(self.NUM_MIN_X, self.NUM_MIN_Y1)
                        time.sleep(0.05)
                        pyautogui.click()
                        time.sleep(0.2)
                    time.sleep(0.1)
            except Exception as e:
                if callback:
                    callback(f"发生错误：{str(e)}")
                time.sleep(0.3)
                continue

    def stop_detection(self):
        self.running = False
        self.is_batch_mode = False


class RealtimeModeController:
    """实时检测模式控制器。负责配置并运行 RealTimeDetector，对外提供 start/stop。"""

    def __init__(self) -> None:
        self.detector = RealTimeDetector()

    def start(
        self,
        max_price: int,
        balance_digits: int,
        detection_delay: float,
        start_time: str,
        end_time: str,
        message_callback,
    ) -> threading.Thread:
        self.detector.set_balance_digits(balance_digits)
        self.detector.set_detection_delay(detection_delay)
        self.detector.set_time_window(start_time, end_time)

        def run():
            self.detector.start_detection(max_price, message_callback)

        thread = threading.Thread(target=run)
        thread.daemon = True
        return thread

    def stop_detection(self) -> None:
        self.detector.stop_detection()
