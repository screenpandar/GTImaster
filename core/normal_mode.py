"""常规模式（批量刷新/购买）逻辑模块。

run_main_loop(interval, ctx) 与 rectify(ctx) 所需上下文 ctx 由 GTImaster 构建，
包含 get_running、output_text、root、rel_x/rel_y、价格区域、get_target_text、
fast_click、各模式参数与 rectify_fn/stop_fn 等。
"""

import time
import random
from datetime import datetime, time as dt_time

import pyautogui
import pygetwindow as gw
import customtkinter as ctk

from config import ITEM_POS_LIST_BASE, RECTIFY_CLICK_POS_1_BASE, RECTIFY_CLICK_POS_2_BASE


def run_main_loop(interval, ctx):
    """常规模式主循环：定时刷新、OCR 识别、条件购买与卡顿修正。"""
    pause_count = 0
    rectify_count = 0
    shop_item_base = ITEM_POS_LIST_BASE[0]

    try:
        pyautogui.PAUSE = 0.02
        window = gw.getWindowsWithTitle("三角洲行动")[0]
        window.activate()
        time.sleep(1)
        buy_counter = 0

        while ctx.get_running():
            start_time_str = ctx.get_start_time()
            end_time_str = ctx.get_end_time()
            if start_time_str and end_time_str:
                current_time = datetime.now().time()
                start = dt_time(*map(int, start_time_str.split(":")))
                end = dt_time(*map(int, end_time_str.split(":")))
                if start < end:
                    if not (start <= current_time <= end):
                        formatted_time = current_time.strftime("%H:%M:%S")
                        ctx.root.after(
                            0,
                            lambda t=formatted_time: ctx.output_text.insert(
                                ctk.END, f"当前时间为{t},不在定时时段\n"
                            ),
                        )
                        time.sleep(10)
                        continue
                else:
                    if not (current_time >= start or current_time <= end):
                        formatted_time = current_time.strftime("%H:%M:%S")
                        ctx.root.after(
                            0,
                            lambda t=formatted_time: ctx.output_text.insert(
                                ctk.END, f"当前时间为{t},不在定时时段\n"
                            ),
                        )
                        time.sleep(10)
                        continue

            if ctx.get_paused():
                time.sleep(0.15)
                continue

            random_time = random.uniform(0.001, 0.01)
            ctx.fast_click(
                ctx.rel_x(shop_item_base[0]),
                ctx.rel_y(shop_item_base[1]),
                move_duration=0.05,
            )
            time.sleep(interval + random_time)
            recognized_text = ctx.get_target_text(ctx.price_box)

            try:
                recognized_price = int(
                    recognized_text.replace(",", "")
                    .replace(".", "")
                    .replace(" ", "")
                    .replace("Q", "0")
                    .replace("O", "0")
                    .replace("，", "")
                )

                if recognized_price < ctx.max_price * 0.1:
                    ctx.root.after(
                        0,
                        lambda p=recognized_price: ctx.output_text.insert(
                            ctk.END, f"识别到的价格{p}过低，可能少位，跳过此次操作\n"
                        ),
                    )
                    pyautogui.press("esc")
                    ctx.fast_click(
                        ctx.rel_x(shop_item_base[0]),
                        ctx.rel_y(shop_item_base[1]),
                        move_duration=0.05,
                    )
                    continue

                ctx.root.after(
                    0,
                    lambda p=recognized_price: ctx.output_text.insert(
                        ctk.END, f"识别到的最低价格：{p}\n"
                    ),
                )
            except ValueError:
                ctx.fast_click(ctx.HVVK_SHOP_X, ctx.HVVK_SHOP_Y, move_duration=0.03)
                ctx.root.after(
                    0,
                    lambda t=recognized_text: ctx.output_text.insert(
                        ctk.END, f"无法识别文本：{t}\n"
                    ),
                )
                continue

            if recognized_price <= ctx.max_price and recognized_price != 0:
                current_active = gw.getActiveWindow()
                windows = gw.getWindowsWithTitle("三角洲行动")
                for w in windows:
                    if w != current_active:
                        w.activate()
                        break

                if ctx.get_card_mode():
                    if ctx.get_max_mode():
                        pyautogui.moveTo(ctx.NUM_MAX_X, ctx.NUM_MAX_Y)
                        pyautogui.click()
                    if buy_counter < ctx.buy_quantity:
                        pyautogui.moveTo(ctx.BUY_POS[0], ctx.BUY_POS[1])
                        pyautogui.click()
                        time.sleep(0.32 + random_time)
                        ctx.output_text.insert(
                            ctk.END,
                            f"以：{recognized_price}的价格尝试购买物品（{buy_counter + 1}/{ctx.buy_quantity}）\n",
                        )
                        buy_counter += 1
                    else:
                        ctx.output_text.insert(ctk.END, "已达到设定的购买数量，停止运行\n")
                        ctx.stop_fn()
                        break
                else:
                    try:
                        if ctx.goldegg_mode:
                            pyautogui.moveTo(ctx.NUM_MAX_X, ctx.NUM_MAX_Y)
                            pyautogui.click()
                            recognized_text1 = ctx.get_target_text(ctx.average_box)
                            average_price = int(
                                recognized_text1.replace(",", "")
                                .replace(".", "")
                                .replace(" ", "")
                                .replace("Q", "0")
                                .replace("O", "0")
                                .replace("，", "")
                            )
                            ctx.root.after(
                                0,
                                lambda p=average_price: ctx.output_text.insert(
                                    ctk.END, f"识别到的购买价格：{p}\n"
                                ),
                            )
                            while average_price <= ctx.max_price and average_price != 0:
                                buy_counter += 1
                                ctx.output_text.insert(
                                    ctk.END, f"以：{average_price}的均价尝试购买\n"
                                )
                                pyautogui.moveTo(ctx.BUY_POS[0], ctx.BUY_POS[1])
                                pyautogui.click()
                                time.sleep(0.32 + random_time)
                                recognized_text1 = ctx.get_target_text(ctx.average_box)
                                average_price = int(
                                    recognized_text1.replace(",", "")
                                    .replace(".", "")
                                    .replace(" ", "")
                                    .replace("Q", "0")
                                    .replace("O", "0")
                                    .replace("，", "")
                                )
                                if buy_counter >= ctx.buy_quantity:
                                    ctx.stop_fn()
                                    break
                                if not ctx.get_running():
                                    break
                            else:
                                ctx.output_text.insert(
                                    ctk.END, f"{average_price}的均价过高，低价商品不足\n"
                                )
                        else:
                            if ctx.get_max_mode():
                                pyautogui.moveTo(ctx.NUM_MAX_X, ctx.NUM_MAX_Y1)
                                pyautogui.click()
                            while (
                                recognized_price <= ctx.max_price and recognized_price != 0
                            ):
                                buy_counter += 1
                                ctx.output_text.insert(
                                    ctk.END, f"以：{recognized_price}的单价尝试购买商品\n"
                                )
                                pyautogui.moveTo(ctx.BUY_POS1[0], ctx.BUY_POS1[1])
                                pyautogui.click()
                                time.sleep(0.32 + random_time)
                                recognized_text = ctx.get_target_text(ctx.price_box)
                                recognized_price = int(
                                    recognized_text.replace(",", "")
                                    .replace(".", "")
                                    .replace(" ", "")
                                    .replace("Q", "0")
                                    .replace("O", "0")
                                    .replace("，", "")
                                )
                                if recognized_price == 380:
                                    recognized_price = 680
                                if buy_counter >= ctx.buy_quantity:
                                    ctx.stop_fn()
                                    break
                                if not ctx.get_running():
                                    break
                    except ValueError:
                        ctx.root.after(
                            0,
                            lambda t=recognized_text: ctx.output_text.insert(
                                ctk.END, f"无法识别文本：{t}\n"
                            ),
                        )
                        continue

            rectify_count += 1
            if rectify_count == ctx.max_rectify_count:
                rectify(ctx)
                rectify_count = 0
            pyautogui.press("esc")
            pause_count += 1
            if pause_count == 300:
                pyautogui.press("esc")
                time.sleep(3)
                pause_count = 0

    except Exception as e:
        err = str(e)
        ctx.root.after(
            0,
            lambda e=err: ctx.output_text.insert(ctk.END, f"发生错误：{e}\n"),
        )


def rectify(ctx):
    """消除卡顿的刷新操作序列。"""
    import keyboard

    keyboard.press_and_release("esc")
    time.sleep(1)
    keyboard.press_and_release("esc")
    time.sleep(1)
    screen_width, screen_height = pyautogui.size()
    pyautogui.click(screen_width // 2, screen_height // 2)
    time.sleep(1)
    keyboard.press_and_release("esc")
    time.sleep(1)
    if not ctx.get_running():
        return
    pyautogui.moveTo(
        ctx.rel_x(RECTIFY_CLICK_POS_1_BASE[0]),
        ctx.rel_y(RECTIFY_CLICK_POS_1_BASE[1]),
    )
    pyautogui.click()
    time.sleep(3)
    keyboard.press_and_release("space")
    time.sleep(1)
    pyautogui.click(screen_width // 2, screen_height // 2)
    time.sleep(1)
    keyboard.press_and_release("esc")
    time.sleep(1)
    if not ctx.get_running():
        return
    pyautogui.moveTo(
        ctx.rel_x(RECTIFY_CLICK_POS_2_BASE[0]),
        ctx.rel_y(RECTIFY_CLICK_POS_2_BASE[1]),
    )
    pyautogui.click()
    time.sleep(3)
