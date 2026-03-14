"""截图与区域转换工具。"""

from PIL import Image
import mss


def box_to_region(box):
    """(left, top, right, bottom) -> (left, top, width, height) 供 mss 使用。"""
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    return (left, top, width, height)


def capture_fast(region):
    """高速截图。region: (left, top, width, height)，返回 PIL Image RGB。"""
    with mss.mss() as sct:
        screenshot = sct.grab({
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        })
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
