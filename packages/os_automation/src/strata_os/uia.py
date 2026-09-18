import pywinauto
from typing import Dict, Any

def get_active_window_tree() -> Dict[str, Any]:
    # We use UIA backend for modern windows apps
    app = pywinauto.Desktop(backend="uia")
    # Actually getting the whole tree can be very slow.
    # Usually we get the active window.
    import win32gui
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return {}
    
    # Connect to the window
    window = app.window(handle=hwnd)
    
    # A simplified tree dump
    def dump_control(ctrl) -> dict:
        info = {
            "title": ctrl.texts()[0] if ctrl.texts() else "",
            "control_type": ctrl.element_info.control_type,
            "rectangle": {
                "left": ctrl.rectangle().left,
                "top": ctrl.rectangle().top,
                "right": ctrl.rectangle().right,
                "bottom": ctrl.rectangle().bottom,
            }
        }
        # Get children
        children = []
        for child in ctrl.children():
            children.append(dump_control(child))
        if children:
            info["children"] = children
        return info

    try:
        return dump_control(window)
    except Exception as e:
        return {"error": str(e)}

def invoke_element_by_name(window_hwnd: int, title: str, control_type: str = "Button"):
    app = pywinauto.Desktop(backend="uia")
    window = app.window(handle=window_hwnd)
    
    # Find the element
    elem = window.child_window(title=title, control_type=control_type)
    if elem.exists():
        elem.invoke()
        return True
    return False
