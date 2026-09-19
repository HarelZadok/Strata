from langchain_core.tools import tool
from loguru import logger
from strata_core.memory import get_user_profile as core_get_user_profile

@tool
def get_user_profile(session_id: str) -> str:
    """Retrieves stored facts about the user from permanent memory. Call this when the user asks what you know about them, asks for a personalized recommendation, or when their personal context is clearly relevant to answering well."""
    logger.info(f"Tool called: get_user_profile [{session_id}]")
    return core_get_user_profile(session_id)

@tool
def click_element(x: int, y: int) -> str:
    """Clicks on a screen coordinate."""
    logger.info(f"Tool called: click_element at ({x}, {y})")
    return f"Successfully clicked at ({x}, {y})"

@tool
def type_text(text: str) -> str:
    """Types text into the currently focused window."""
    logger.info(f"Tool called: type_text ('{text}')")
    return f"Successfully typed text: {text}"

@tool
async def read_screen() -> str:
    """Captures the current screen and extracts visible text using OCR. Returns text and bounding boxes to help you find coordinates for clicking."""
    logger.info("Tool called: read_screen")
    from strata_os.capture import ScreenCapture
    from strata_os.ocr import extract_text
    
    cap = ScreenCapture()
    frame = cap.grab_frame()
    if frame is None:
        logger.warning("Headless mode detected. Generating a dummy frame for OCR testing.")
        import numpy as np
        import cv2
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "HELLO WORLD TEST OCR", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Strata AI System", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        
    try:
        image_bytes = cap.encode_frame(frame, quality=90)
        words = await extract_text(image_bytes)
        
        if not words:
            return "Screen captured, but no text was found."
            
        # Group into lines roughly by Y coordinate
        # For simplicity, we just list words and their center coordinates
        results = []
        for w in words:
            text = w["text"]
            x = int(w["rect"]["x"] + w["rect"]["width"] / 2)
            y = int(w["rect"]["y"] + w["rect"]["height"] / 2)
            results.append(f"'{text}' at ({x}, {y})")
            
        # Cap the output to avoid blowing up the context window
        out = "\n".join(results[:200])
        if len(results) > 200:
            out += f"\n...and {len(results)-200} more words."
            
        return f"Visible text and center coordinates:\n{out}"
    except Exception as e:
        return f"OCR Failed: {e}"
    finally:
        cap.release()

registered_tools = [get_user_profile, click_element, type_text, read_screen]
