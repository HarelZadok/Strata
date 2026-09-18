import win32gui
import win32con
import ctypes
from typing import List, Dict

DWMWA_CLOAKED = 14

def is_window_cloaked(hwnd):
    cloaked = ctypes.c_int(0)
    try:
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)
        )
        return bool(cloaked.value)
    except Exception:
        return False

def list_windows() -> List[Dict]:
    windows = []
    def enum_cb(hwnd, results):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            if not is_window_cloaked(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                results.append({
                    "hwnd": hwnd,
                    "title": win32gui.GetWindowText(hwnd),
                    "rect": rect
                })
    win32gui.EnumWindows(enum_cb, windows)
    return windows

def focus_window(title_substring: str) -> bool:
    windows = list_windows()
    for w in windows:
        if title_substring.lower() in w["title"].lower():
            hwnd = w["hwnd"]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            return True
    return False

def close_window(title_substring: str) -> bool:
    windows = list_windows()
    for w in windows:
        if title_substring.lower() in w["title"].lower():
            win32gui.PostMessage(w["hwnd"], win32con.WM_CLOSE, 0, 0)
            return True
    return False
