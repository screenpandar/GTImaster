"""
一键打包脚本：使用 PyInstaller 将 GTImaster 打成单文件 exe，不进行 pyd 编译。
"""
import os
import sys
import subprocess
import shutil


def build_exe():
    """使用 PyInstaller 打包为单文件、无控制台窗口的 exe。"""
    print("正在使用 PyInstaller 打包...")

    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--clean",
        "--windowed",
        "--noupx",
        "--name",
        "GTImaster",
        # 入口
        "GTImaster.py",
        # 显式收集易漏的包
        "--hidden-import",
        "numpy",
        "--hidden-import",
        "cv2",
        "--hidden-import",
        "PIL",
        "--hidden-import",
        "PIL.Image",
        "--hidden-import",
        "PIL.ImageFilter",
        "--hidden-import",
        "win32con",
        "--hidden-import",
        "win32api",
        "--hidden-import",
        "pyautogui",
        "--hidden-import",
        "pygetwindow",
        "--hidden-import",
        "keyboard",
        "--hidden-import",
        "customtkinter",
        "--hidden-import",
        "easyocr",
        "--hidden-import",
        "mss",
        "--hidden-import",
        "config",
        "--hidden-import",
        "core",
        "--hidden-import",
        "core.realtime_mode",
        "--hidden-import",
        "core.normal_mode",
        "--hidden-import",
        "core.shutdown",
        "--hidden-import",
        "core.app_state",
        "--hidden-import",
        "core.fast_click",
        "--hidden-import",
        "ui",
        "--hidden-import",
        "ui.main_window",
        "--hidden-import",
        "utils",
        "--hidden-import",
        "utils.image_utils",
        "--hidden-import",
        "scipy",
        "--hidden-import",
        "scipy._lib",
        "--hidden-import",
        "scipy.ndimage",
        "--collect-all",
        "easyocr",
        "--collect-all",
        "numpy",
        "--collect-all",
        "scipy",
    ]

    r = subprocess.run(cmd)
    if r.returncode != 0:
        print("打包失败，请检查依赖与 PyInstaller 是否安装：pip install pyinstaller")
        sys.exit(1)

    # 打包成功后只清空 build 目录内容，保留 build 目录
    if os.path.exists("build"):
        for name in os.listdir("build"):
            path = os.path.join("build", name)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        print("已清理 build 目录内容。")

    print("\n打包完成。可执行文件：dist/GTImaster.exe")


if __name__ == "__main__":
    build_exe()
