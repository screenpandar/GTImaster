import time
import numpy as np
import pyautogui


def fast_click(x, y, move_duration=0, click_delay=0.001):
    """模拟人类快速移动点击"""
    final_x = x + np.random.randint(-2, 3)
    final_y = y + np.random.randint(-2, 3)
    pyautogui.moveTo(
        final_x,
        final_y,
        duration=move_duration + np.random.uniform(0, 0.001),
        tween=pyautogui.easeInOutQuad,
    )
    time.sleep(click_delay + np.random.uniform(0, 0.001))
    pyautogui.click()

