"""
capture.py — Screen capture with layered fallback strategy.

Priority order:
  1. bettercam (DirectX Desktop Duplication -- fastest, needs hardware access)
  2. mss (GDI BitBlt -- works without elevation in most cases)
  3. PIL ImageGrab (GDI fallback)
  4. win32ui PrintWindow per-HWND (captures a specific window; no hardware access needed)
"""

import ctypes
import numpy as np
import cv2

# ── bettercam: patch BEFORE the class is ever used so __del__ doesn't crash ──
# bettercam has a bug where __del__ is called even on partially-constructed
# objects.  We pre-declare the missing private attribute so the destructor
# code path is safe.
try:
    import bettercam as _bc
    import threading as _t

    class _NoOp:
        """Sentinel object whose methods are no-ops — used to safely stub out
        bettercam's internal objects when the device failed to initialize."""
        def release(self): pass
        def clear(self):   pass
        def set(self):     pass
        def is_set(self):  return False

    cls = _bc.BetterCam
    _class_defaults = {
        '_BetterCam__frame_available': _t.Event(),
        '_BetterCam__stop_capture':    _t.Event(),
        '_BetterCam__thread':          None,
        '_duplicator':                 _NoOp(),
        'is_capturing':                False,
    }
    for _attr, _default in _class_defaults.items():
        if not hasattr(cls, _attr):
            setattr(cls, _attr, _default)
    _HAS_BETTERCAM = True
except Exception:
    _bc = None
    _HAS_BETTERCAM = False

try:
    import mss as _mss_mod
    _HAS_MSS = True
except ImportError:
    _HAS_MSS = False

try:
    from PIL import ImageGrab as _ImageGrab
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def _capture_hwnd_printwindow(hwnd: int) -> "np.ndarray | None":
    """
    Capture a window by its HWND using PrintWindow.
    Works even when BitBlt is blocked (e.g. GPU-composited or sandboxed contexts).
    Returns a BGR numpy array or None on failure.
    """
    try:
        import win32gui
        import win32ui
        import win32con

        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w, h = right - left, bot - top
        if w <= 0 or h <= 0:
            return None

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)

        # PW_RENDERFULLCONTENT = 0x00000002 — captures GPU-composited content
        result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

        if result:
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            frame = np.frombuffer(bmpstr, dtype=np.uint8).reshape(
                (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            )
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        else:
            frame = None

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        return frame
    except Exception:
        return None


class ScreenCapture:
    """
    Grab full-screen frames with graceful backend fallback.
    """

    def __init__(self, monitor_idx: int = 0):
        self.monitor_idx = monitor_idx
        self._backend: str | None = None
        self._camera = None
        self._mss = None

        # Try to init bettercam eagerly
        if _HAS_BETTERCAM:
            try:
                self._camera = _bc.create(output_idx=monitor_idx)
            except Exception:
                self._camera = None

    # ------------------------------------------------------------------ #
    def grab_frame(self) -> "np.ndarray | None":
        """
        Returns a BGR numpy array of the current screen.
        Tries: bettercam -> mss -> PIL -> win32ui PrintWindow (desktop hwnd).
        """
        # 1. bettercam
        if self._camera is not None:
            try:
                frame = self._camera.grab()
                if frame is not None:
                    self._backend = "bettercam"
                    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception:
                try:
                    self._camera.release()
                except Exception:
                    pass
                self._camera = None

        # 2. mss
        if _HAS_MSS:
            try:
                if self._mss is None:
                    import mss
                    self._mss = mss.mss()
                monitor = self._mss.monitors[self.monitor_idx + 1]
                sct_img = self._mss.grab(monitor)
                frame = np.array(sct_img)
                self._backend = "mss"
                return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            except Exception:
                if self._mss:
                    try:
                        self._mss.close()
                    except Exception:
                        pass
                    self._mss = None

        # 3. PIL ImageGrab
        if _HAS_PIL:
            try:
                pil_img = _ImageGrab.grab(all_screens=True)
                frame = np.array(pil_img)
                self._backend = "pil"
                return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception:
                pass

        # 4. win32ui PrintWindow on the desktop HWND
        try:
            import win32gui
            hwnd = win32gui.GetDesktopWindow()
            frame = _capture_hwnd_printwindow(hwnd)
            if frame is not None:
                self._backend = "win32ui"
                return frame
        except Exception:
            pass

        # print("[ScreenCapture] Full desktop backends failed. (Expected in headless or sandboxed contexts)")
        return None

    # ------------------------------------------------------------------ #
    def capture_window(self, hwnd: int) -> "np.ndarray | None":
        """Capture a single window by its HWND using PrintWindow."""
        frame = _capture_hwnd_printwindow(hwnd)
        if frame is not None:
            self._backend = "win32ui-hwnd"
        return frame

    def encode_frame(self, frame: np.ndarray, quality: int = 80) -> bytes:
        """Encode a BGR frame to JPEG bytes."""
        success, encoded = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )
        if not success:
            raise ValueError("Failed to encode frame to JPEG")
        return encoded.tobytes()

    def release(self):
        if self._camera:
            try:
                self._camera.release()
            except Exception:
                pass
        if self._mss:
            try:
                self._mss.close()
            except Exception:
                pass
