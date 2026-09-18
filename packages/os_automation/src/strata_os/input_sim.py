"""
input_sim.py — DPI-aware mouse/keyboard input simulation for Windows.

Key design decision: `SendInput` is blocked by UIPI when the target window
runs at a higher integrity level than the sender. The production path for the
real AI agent will always use `SendInput` (works fine from an elevated process
or when same-privilege windows are targeted).

For the test harness, we provide `type_text_to_hwnd()` which posts WM_CHAR
messages directly to a window handle — this bypasses UIPI entirely and is
safe for self-owned test windows (e.g. tkinter windows in the same process).
"""

import ctypes
import time
import win32api
import win32con
import win32gui

# --------------------------------------------------------------------------- #
# Win32 INPUT structures                                                        #
# --------------------------------------------------------------------------- #
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_ushort),
                ("wParamH", ctypes.c_ushort))

class INPUT_I(ctypes.Union):
    _fields_ = (("mi", MOUSEINPUT),
                ("ki", KEYBDINPUT),
                ("hi", HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (("type", ctypes.c_ulong),
                ("ii", INPUT_I))

# --------------------------------------------------------------------------- #
# Mouse helpers                                                                 #
# --------------------------------------------------------------------------- #
def _click_mouse(x: int, y: int, button_down: int, button_up: int):
    ctypes.windll.user32.SetCursorPos(x, y)
    extra = ctypes.c_ulong(0)
    ii_ = INPUT_I()
    ii_.mi = MOUSEINPUT(0, 0, 0, button_down, 0, ctypes.pointer(extra))
    x_input = INPUT(ctypes.c_ulong(INPUT_MOUSE), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
    time.sleep(0.05)
    ii_.mi = MOUSEINPUT(0, 0, 0, button_up, 0, ctypes.pointer(extra))
    x_input = INPUT(ctypes.c_ulong(INPUT_MOUSE), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))

def click(x: int, y: int):
    """Left-click at absolute screen coordinates."""
    _click_mouse(x, y, 0x0002, 0x0004)  # MOUSEEVENTF_LEFTDOWN / LEFTUP

def right_click(x: int, y: int):
    """Right-click at absolute screen coordinates."""
    _click_mouse(x, y, 0x0008, 0x0010)  # MOUSEEVENTF_RIGHTDOWN / RIGHTUP

# --------------------------------------------------------------------------- #
# Keyboard helpers — two strategies                                             #
# --------------------------------------------------------------------------- #
def type_text(text: str):
    """
    Inject keystrokes via SendInput (system-wide).
    Works as long as the target window is at the same or lower integrity level.
    This is the method to use in production (from the elevated agent process).
    """
    import pywinauto.keyboard
    pywinauto.keyboard.send_keys(text, with_spaces=True, with_tabs=True)


def type_text_to_hwnd(hwnd: int, text: str, delay_ms: int = 30):
    """
    Post WM_CHAR messages directly to a window handle.
    Bypasses UIPI completely — perfect for same-process test windows (tkinter etc.)
    and for any window the agent itself owns.
    """
    # Find the deepest focusable child (e.g. the actual text box inside a frame)
    target = ctypes.windll.user32.GetWindow(hwnd, 5)  # GW_CHILD
    if not target:
        target = hwnd

    for char in text:
        win32api.PostMessage(target, win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay_ms / 1000)
