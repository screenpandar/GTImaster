"""主窗口 UI 构建：常规模式 + 实时检测模式两个 Tab，所有控件。"""

from types import SimpleNamespace
import customtkinter as ctk
from tkinter import scrolledtext


def create_main_window(app_state):
    """创建主窗口与全部控件，返回 (root, widgets)。调用方负责绑定 start/stop/shutdown 等 command。"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("GTImaster")
    root.geometry("800x700")

    tabview = ctk.CTkTabview(root)
    tabview.pack(fill="both", expand=True, padx=20, pady=20)
    tab_normal = tabview.add("常规模式")
    tab_single = tabview.add("实时检测模式")

    # === 常规模式 ===
    main_frame = ctk.CTkFrame(tab_normal)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    max_mode_var = ctk.BooleanVar()
    card_mode_var = ctk.BooleanVar()
    goldegg_mode_var = ctk.BooleanVar()

    price_frame = ctk.CTkFrame(main_frame)
    price_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(price_frame, text="最大购买价格:").pack(side="left", padx=5)
    max_price_entry = ctk.CTkEntry(price_frame, width=80)
    max_price_entry.pack(side="left", padx=5)
    ctk.CTkLabel(price_frame, text="最大购买次数(<9999):").pack(side="left", padx=5)
    buy_quantity_entry = ctk.CTkEntry(price_frame, width=80)
    buy_quantity_entry.pack(side="left", padx=5)
    buy_quantity_entry.insert(0, "9999")
    ctk.CTkLabel(price_frame, text="每刷新").pack(side="left", padx=5)
    rectify_count_entry = ctk.CTkEntry(price_frame, width=60)
    rectify_count_entry.pack(side="left", padx=5)
    rectify_count_entry.insert(0, "200")
    ctk.CTkLabel(price_frame, text="次切换模式消除卡顿").pack(side="left", padx=5)

    checkbox_frame = ctk.CTkFrame(main_frame)
    checkbox_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkCheckBox(checkbox_frame, text="数量拉满", variable=max_mode_var).pack(side="left", padx=20)
    ctk.CTkCheckBox(checkbox_frame, text="房卡/配件模式", variable=card_mode_var).pack(side="left", padx=20)
    ctk.CTkCheckBox(checkbox_frame, text="金弹模式(购买金弹请勾选)", variable=goldegg_mode_var).pack(side="left", padx=20)

    shutdown_frame = ctk.CTkFrame(main_frame)
    shutdown_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(shutdown_frame, text="关机时间(HH:MM):").pack(side="left", padx=5)
    shutdown_time_entry = ctk.CTkEntry(shutdown_frame, width=120)
    shutdown_time_entry.pack(side="left", padx=5)
    shutdown_time_entry.insert(0, "02:00")
    shutdown_button = ctk.CTkButton(shutdown_frame, text="启动定时关机", width=120)
    shutdown_button.pack(side="left", padx=10)

    interval_frame = ctk.CTkFrame(main_frame)
    interval_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(interval_frame, text="刷新间隔（秒）:").pack(side="left", padx=5)
    interval_entry = ctk.CTkEntry(interval_frame, width=120)
    interval_entry.pack(side="left", padx=5)
    interval_entry.insert(0, "0.3")
    ctk.CTkLabel(interval_frame, text="(不建议低于0.1，可能会被警告)").pack(side="left", padx=5)

    start_button = ctk.CTkButton(main_frame, text="开始")
    start_button.pack(pady=10)

    info_frame = ctk.CTkFrame(main_frame)
    info_frame.pack(fill="x", padx=10, pady=5)
    for t in ["时间冒号需为英文冒号！", "子弹补货0:00-4:00，", "房卡/配件全天不定时补，", "无货商品暂不支持"]:
        ctk.CTkLabel(info_frame, text=t).pack(side="left", expand=True)

    time_frame = ctk.CTkFrame(main_frame)
    time_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(time_frame, text="开始时间(HH:MM):").pack(side="left", padx=5)
    start_time_entry = ctk.CTkEntry(time_frame, width=120)
    start_time_entry.pack(side="left", padx=5)
    ctk.CTkLabel(time_frame, text="结束时间(HH:MM):").pack(side="left", padx=5)
    end_time_entry = ctk.CTkEntry(time_frame, width=120)
    end_time_entry.pack(side="left", padx=5)

    output_frame = ctk.CTkFrame(main_frame)
    output_frame.pack(fill="both", expand=True, padx=10, pady=5)
    output_text = scrolledtext.ScrolledText(output_frame, width=80, height=20)
    output_text.pack(fill="both", expand=True, padx=5, pady=5)

    # === 实时检测模式 ===
    single_frame = ctk.CTkFrame(tab_single)
    single_frame.pack(padx=20, pady=20, fill="both", expand=True)

    single_price_frame = ctk.CTkFrame(single_frame)
    single_price_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(single_price_frame, text="最大购买价格:").pack(side="left", padx=5)
    single_max_price_entry = ctk.CTkEntry(single_price_frame, width=120)
    single_max_price_entry.pack(side="left", padx=5)
    ctk.CTkLabel(single_price_frame, text="哈夫币余额位数:").pack(side="left", padx=5)
    balance_digits_entry = ctk.CTkEntry(single_price_frame, width=80)
    balance_digits_entry.pack(side="left", padx=5)

    single_hotkey_frame = ctk.CTkFrame(single_frame)
    single_hotkey_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(single_hotkey_frame, text="开始快捷键:").pack(side="left", padx=5)
    single_hotkey_entry = ctk.CTkEntry(single_hotkey_frame, width=80)
    single_hotkey_entry.pack(side="left", padx=5)
    single_hotkey_entry.insert(0, "f8")

    def update_single_hotkey():
        new_hotkey = single_hotkey_entry.get().lower().strip()
        if new_hotkey:
            app_state.current_hotkey = new_hotkey
            single_output_text.insert(ctk.END, f"快捷键已更新为：{app_state.current_hotkey.upper()}\n")

    single_hotkey_update_button = ctk.CTkButton(single_hotkey_frame, text="更新快捷键", width=100, command=update_single_hotkey)
    single_hotkey_update_button.pack(side="left", padx=10)
    ctk.CTkLabel(single_hotkey_frame, text="(仅实时检测模式支持快捷键启动，F12停止程序)").pack(side="left", padx=5)

    single_time_frame = ctk.CTkFrame(single_frame)
    single_time_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(single_time_frame, text="开始时间(HH:MM):").pack(side="left", padx=5)
    single_start_time_entry = ctk.CTkEntry(single_time_frame, width=120)
    single_start_time_entry.pack(side="left", padx=5)
    ctk.CTkLabel(single_time_frame, text="结束时间(HH:MM):").pack(side="left", padx=5)
    single_end_time_entry = ctk.CTkEntry(single_time_frame, width=120)
    single_end_time_entry.pack(side="left", padx=5)

    speed_frame = ctk.CTkFrame(single_frame)
    speed_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(speed_frame, text="实时检测延迟(秒):").pack(side="left", padx=5)
    speed_value_label = ctk.CTkLabel(speed_frame, text="1.0")
    speed_slider = ctk.CTkSlider(speed_frame, from_=0.1, to=2.0, number_of_steps=19)

    def update_speed_label(value):
        speed_value_label.configure(text=f"{float(value):.1f}")

    speed_slider.configure(command=update_speed_label)
    speed_slider.pack(side="left", padx=5, expand=True, fill="x")
    speed_slider.set(1.0)
    speed_value_label.pack(side="left", padx=5)

    single_shutdown_frame = ctk.CTkFrame(single_frame)
    single_shutdown_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(single_shutdown_frame, text="关机时间(HH:MM):").pack(side="left", padx=5)
    single_shutdown_time_entry = ctk.CTkEntry(single_shutdown_frame, width=120)
    single_shutdown_time_entry.pack(side="left", padx=5)
    single_shutdown_time_entry.insert(0, "02:00")
    single_shutdown_button = ctk.CTkButton(single_shutdown_frame, text="启动定时关机", width=120)
    single_shutdown_button.pack(side="left", padx=10)

    single_control_frame = ctk.CTkFrame(single_frame)
    single_control_frame.pack(fill="x", padx=10, pady=5)
    single_start_button = ctk.CTkButton(single_control_frame, text="开始检测")
    single_start_button.pack(pady=10)

    single_output_frame = ctk.CTkFrame(single_frame)
    single_output_frame.pack(fill="both", expand=True, padx=10, pady=5)
    single_output_text = scrolledtext.ScrolledText(single_output_frame, width=80, height=20)
    single_output_text.pack(fill="both", expand=True, padx=5, pady=5)

    widgets = SimpleNamespace(
        root=root,
        tabview=tabview,
        output_text=output_text,
        single_output_text=single_output_text,
        max_price_entry=max_price_entry,
        buy_quantity_entry=buy_quantity_entry,
        rectify_count_entry=rectify_count_entry,
        max_mode_var=max_mode_var,
        card_mode_var=card_mode_var,
        goldegg_mode_var=goldegg_mode_var,
        shutdown_time_entry=shutdown_time_entry,
        shutdown_button=shutdown_button,
        interval_entry=interval_entry,
        start_time_entry=start_time_entry,
        end_time_entry=end_time_entry,
        start_button=start_button,
        single_max_price_entry=single_max_price_entry,
        balance_digits_entry=balance_digits_entry,
        single_hotkey_entry=single_hotkey_entry,
        single_start_time_entry=single_start_time_entry,
        single_end_time_entry=single_end_time_entry,
        speed_slider=speed_slider,
        single_shutdown_time_entry=single_shutdown_time_entry,
        single_shutdown_button=single_shutdown_button,
        single_start_button=single_start_button,
    )
    return root, widgets
